"""Search engine for visual and text-based image search."""
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from .feature_extractor import FeatureExtractor
from .indexer import ImageIndexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchEngine:
    """Search engine for finding similar images."""
    
    def __init__(self, feature_extractor: FeatureExtractor, indexer: ImageIndexer, 
                 search_config: Dict):
        """
        Initialize search engine.
        
        Args:
            feature_extractor: Feature extractor instance
            indexer: Image indexer instance
            search_config: Search configuration
        """
        self.feature_extractor = feature_extractor
        self.indexer = indexer
        self.search_config = search_config
        self.top_k = search_config.get('top_k', 20)
        self.similarity_threshold = search_config.get('similarity_threshold', 0.7)
    
    def search_by_image(self, query_image_path: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Search for similar images using a query image.
        
        Args:
            query_image_path: Path to the query image
            top_k: Number of results to return (uses config default if None)
            
        Returns:
            List of search results with metadata and similarity scores
        """
        if not self.indexer.is_indexed:
            logger.error("Index not loaded. Please build or load index first.")
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        try:
            # Extract features from query image
            logger.info(f"Extracting features from query image: {query_image_path}")
            query_features = self.feature_extractor.extract_features(query_image_path)
            
            if query_features is None:
                logger.error("Failed to extract features from query image")
                return []
            
            # Compute similarities with all indexed images
            similarities = self._compute_similarities(query_features)
            
            # Get top-k results
            results = self._get_top_k_results(similarities, top_k)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during image search: {e}")
            return []
    
    def search_by_features(self, query_features: np.ndarray, top_k: Optional[int] = None) -> List[Dict]:
        """
        Search using pre-computed feature vector.
        
        Args:
            query_features: Pre-computed feature vector
            top_k: Number of results to return
            
        Returns:
            List of search results with metadata and similarity scores
        """
        if not self.indexer.is_indexed:
            logger.error("Index not loaded")
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        similarities = self._compute_similarities(query_features)
        results = self._get_top_k_results(similarities, top_k)
        
        return results
    
    def search_by_text(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Search for images containing specific text (using OCR index).
        
        Args:
            query: Text query to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of matching images with metadata
        """
        if not self.indexer.is_indexed:
            logger.error("Index not loaded")
            return []
        
        if max_results is None:
            max_results = self.top_k
        
        try:
            # Search in OCR index
            matching_indices = self.indexer.search_by_text(query, max_results)
            
            # Get metadata for matching images
            results = []
            for idx in matching_indices:
                metadata = self.indexer.metadata[idx]
                result = {
                    'index': idx,
                    'path': metadata['path'],
                    'filename': metadata['filename'],
                    'ocr_text': metadata.get('ocr_text', ''),
                    'match_type': 'text'
                }
                results.append(result)
            
            logger.info(f"Found {len(results)} images matching text query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Error during text search: {e}")
            return []
    
    def _compute_similarities(self, query_features: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarities between query and all indexed images.
        
        Args:
            query_features: Query feature vector
            
        Returns:
            Array of similarity scores
        """
        # Normalize query features
        query_norm = np.linalg.norm(query_features)
        if query_norm > 0:
            query_features = query_features / query_norm
        
        # Compute cosine similarity with all embeddings
        # Since both query and embeddings are normalized, dot product gives cosine similarity
        similarities = np.dot(self.indexer.embeddings, query_features)
        
        return similarities
    
    def _get_top_k_results(self, similarities: np.ndarray, top_k: int) -> List[Dict]:
        """
        Get top-k most similar results.
        
        Args:
            similarities: Array of similarity scores
            top_k: Number of results to return
            
        Returns:
            List of results with metadata and scores
        """
        # Get indices of top-k most similar images
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            similarity = float(similarities[idx])
            
            # Apply similarity threshold
            if similarity < self.similarity_threshold:
                continue
            
            metadata = self.indexer.metadata[idx]
            result = {
                'index': int(idx),
                'path': metadata['path'],
                'filename': metadata['filename'],
                'similarity': similarity,
                'match_type': 'visual'
            }
            
            # Include OCR text if available
            if 'ocr_text' in metadata:
                result['ocr_text'] = metadata['ocr_text']
            
            results.append(result)
        
        logger.info(f"Found {len(results)} similar images (threshold: {self.similarity_threshold})")
        return results
    
    def hybrid_search(self, query_image_path: str = None, query_text: str = None, 
                     top_k: Optional[int] = None) -> List[Dict]:
        """
        Perform hybrid search using both visual and text queries.
        
        Args:
            query_image_path: Optional path to query image
            query_text: Optional text query
            top_k: Number of results to return
            
        Returns:
            Combined and ranked search results
        """
        if not query_image_path and not query_text:
            logger.error("At least one of query_image_path or query_text must be provided")
            return []
        
        all_results = {}
        
        # Visual search
        if query_image_path:
            visual_results = self.search_by_image(query_image_path, top_k)
            for result in visual_results:
                idx = result['index']
                if idx not in all_results:
                    all_results[idx] = result
                    all_results[idx]['visual_score'] = result['similarity']
                else:
                    all_results[idx]['visual_score'] = result['similarity']
        
        # Text search
        if query_text:
            text_results = self.search_by_text(query_text, top_k)
            for result in text_results:
                idx = result['index']
                if idx not in all_results:
                    all_results[idx] = result
                    all_results[idx]['text_match'] = True
                else:
                    all_results[idx]['text_match'] = True
        
        # Convert to list and sort by combined score
        results_list = list(all_results.values())
        
        # Sort by visual score if available, otherwise by text match
        results_list.sort(key=lambda x: x.get('visual_score', 0), reverse=True)
        
        if top_k:
            results_list = results_list[:top_k]
        
        return results_list
