"""Image indexing system to build and maintain searchable index."""
import numpy as np
import pickle
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageIndexer:
    """Index images with their features and metadata."""
    
    def __init__(self, storage_config: Dict):
        """
        Initialize image indexer.
        
        Args:
            storage_config: Configuration for storage paths
        """
        self.storage_config = storage_config
        self.embeddings = None
        self.metadata = []
        self.ocr_index = {}
        self.is_indexed = False
    
    def build_index(self, image_paths: List[str], features: np.ndarray, 
                    ocr_results: Optional[List[Dict]] = None):
        """
        Build index from image paths and their features.
        
        Args:
            image_paths: List of image file paths
            features: Array of feature vectors for each image
            ocr_results: Optional list of OCR results for each image
        """
        logger.info(f"Building index for {len(image_paths)} images")
        
        # Store embeddings
        self.embeddings = features
        
        # Build metadata
        self.metadata = []
        for i, path in enumerate(image_paths):
            metadata = {
                'index': i,
                'path': path,
                'filename': os.path.basename(path),
                'size': os.path.getsize(path) if os.path.exists(path) else 0
            }
            
            # Add OCR data if available
            if ocr_results and i < len(ocr_results):
                metadata['ocr_text'] = ocr_results[i].get('text', '')
                metadata['ocr_words'] = ocr_results[i].get('words', [])
            
            self.metadata.append(metadata)
        
        # Build OCR index for text search
        if ocr_results:
            self._build_ocr_index(ocr_results)
        
        self.is_indexed = True
        logger.info("Index built successfully")
    
    def _build_ocr_index(self, ocr_results: List[Dict]):
        """
        Build inverted index for text search.
        
        Args:
            ocr_results: List of OCR results
        """
        self.ocr_index = {}
        
        for i, result in enumerate(ocr_results):
            words = result.get('words', [])
            for word in words:
                word_lower = word.lower().strip()
                if word_lower:
                    if word_lower not in self.ocr_index:
                        self.ocr_index[word_lower] = []
                    self.ocr_index[word_lower].append(i)
        
        logger.info(f"OCR index built with {len(self.ocr_index)} unique words")
    
    def save_index(self):
        """Save index to disk."""
        try:
            # Save embeddings
            embeddings_path = self.storage_config.get('embeddings_path')
            if self.embeddings is not None:
                np.save(embeddings_path, self.embeddings)
                logger.info(f"Saved embeddings to {embeddings_path}")
            
            # Save metadata
            metadata_path = self.storage_config.get('metadata_path')
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}")
            
            # Save OCR index
            ocr_index_path = self.storage_config.get('ocr_index_path')
            with open(ocr_index_path, 'wb') as f:
                pickle.dump(self.ocr_index, f)
            logger.info(f"Saved OCR index to {ocr_index_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self) -> bool:
        """
        Load index from disk.
        
        Returns:
            True if index loaded successfully, False otherwise
        """
        try:
            # Load embeddings
            embeddings_path = self.storage_config.get('embeddings_path')
            if os.path.exists(embeddings_path):
                self.embeddings = np.load(embeddings_path)
                logger.info(f"Loaded embeddings from {embeddings_path}")
            else:
                logger.warning(f"Embeddings file not found: {embeddings_path}")
                return False
            
            # Load metadata
            metadata_path = self.storage_config.get('metadata_path')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                logger.info(f"Loaded metadata from {metadata_path}")
            else:
                logger.warning(f"Metadata file not found: {metadata_path}")
                return False
            
            # Load OCR index
            ocr_index_path = self.storage_config.get('ocr_index_path')
            if os.path.exists(ocr_index_path):
                with open(ocr_index_path, 'rb') as f:
                    self.ocr_index = pickle.load(f)
                logger.info(f"Loaded OCR index from {ocr_index_path}")
            else:
                logger.info("No OCR index found")
                self.ocr_index = {}
            
            self.is_indexed = True
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def get_metadata(self, indices: List[int]) -> List[Dict]:
        """
        Get metadata for specific indices.
        
        Args:
            indices: List of image indices
            
        Returns:
            List of metadata dictionaries
        """
        return [self.metadata[i] for i in indices if i < len(self.metadata)]
    
    def search_by_text(self, query: str, max_results: int = 20) -> List[int]:
        """
        Search for images containing specific text.
        
        Args:
            query: Text query to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of image indices matching the query
        """
        query_words = query.lower().split()
        matching_indices = set()
        
        for word in query_words:
            if word in self.ocr_index:
                matching_indices.update(self.ocr_index[word])
        
        # Also check for phrase matches in metadata
        phrase_matches = []
        query_lower = query.lower()
        for i, meta in enumerate(self.metadata):
            ocr_text = meta.get('ocr_text', '').lower()
            if query_lower in ocr_text:
                phrase_matches.append(i)
        
        # Combine and deduplicate
        all_matches = list(matching_indices.union(set(phrase_matches)))
        return all_matches[:max_results]
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        stats = {
            'total_images': len(self.metadata),
            'total_embeddings': len(self.embeddings) if self.embeddings is not None else 0,
            'unique_words': len(self.ocr_index),
            'is_indexed': self.is_indexed
        }
        
        if self.metadata:
            total_size = sum(m.get('size', 0) for m in self.metadata)
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        return stats
