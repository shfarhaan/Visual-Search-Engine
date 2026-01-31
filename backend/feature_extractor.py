"""Feature extraction from images using pre-trained models."""
import numpy as np
from PIL import Image
import logging
from typing import List, Union
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extract features from images using pre-trained CNN models."""
    
    def __init__(self, model_name: str = 'vgg16', embedding_size: int = 512):
        """
        Initialize feature extractor.
        
        Args:
            model_name: Name of the model to use ('vgg16' or 'resnet50')
            embedding_size: Size of the output embedding vector
        """
        self.model_name = model_name.lower()
        self.embedding_size = embedding_size
        self.model = None
        self.preprocess_fn = None
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model."""
        try:
            import tensorflow as tf
            from tensorflow.keras.applications import VGG16, ResNet50
            from tensorflow.keras.applications.vgg16 import preprocess_input as vgg16_preprocess
            from tensorflow.keras.applications.resnet50 import preprocess_input as resnet50_preprocess
            from tensorflow.keras.models import Model
            from tensorflow.keras.layers import GlobalAveragePooling2D
            
            if self.model_name == 'vgg16':
                base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
                self.preprocess_fn = vgg16_preprocess
                logger.info("Loaded VGG16 model")
            elif self.model_name == 'resnet50':
                base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
                self.preprocess_fn = resnet50_preprocess
                logger.info("Loaded ResNet50 model")
            else:
                raise ValueError(f"Unknown model: {self.model_name}")
            
            # Add global average pooling to get fixed-size embeddings
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            self.model = Model(inputs=base_model.input, outputs=x)
            
            logger.info(f"Feature extractor initialized with {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def extract_features(self, image_path: str) -> np.ndarray:
        """
        Extract features from a single image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Feature vector as numpy array
        """
        try:
            # Load and preprocess image
            img = Image.open(image_path)
            img = img.convert('RGB')  # Ensure RGB format
            img = img.resize((224, 224))  # Resize to model input size
            
            # Convert to array and preprocess
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = self.preprocess_fn(img_array)
            
            # Extract features
            features = self.model.predict(img_array, verbose=0)
            
            # Normalize the feature vector
            features = features.flatten()
            norm = np.linalg.norm(features)
            if norm > 0:
                features = features / norm
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from {image_path}: {e}")
            return None
    
    def extract_features_batch(self, image_paths: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Extract features from multiple images in batches.
        
        Args:
            image_paths: List of image file paths
            batch_size: Number of images to process at once
            
        Returns:
            Array of feature vectors
        """
        all_features = []
        
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]
            batch_images = []
            valid_indices = []
            
            # Load and preprocess batch
            for idx, path in enumerate(batch_paths):
                try:
                    img = Image.open(path)
                    img = img.convert('RGB')
                    img = img.resize((224, 224))
                    img_array = np.array(img)
                    batch_images.append(img_array)
                    valid_indices.append(i + idx)
                except Exception as e:
                    logger.warning(f"Skipping {path}: {e}")
                    all_features.append(None)
            
            if batch_images:
                # Process batch
                batch_array = np.array(batch_images)
                batch_array = self.preprocess_fn(batch_array)
                
                # Extract features
                features = self.model.predict(batch_array, verbose=0)
                
                # Normalize each feature vector
                for j, feat in enumerate(features):
                    feat = feat.flatten()
                    norm = np.linalg.norm(feat)
                    if norm > 0:
                        feat = feat / norm
                    all_features.append(feat)
            
            if (i + batch_size) % 100 == 0:
                logger.info(f"Processed {min(i + batch_size, len(image_paths))}/{len(image_paths)} images")
        
        # Filter out None values and convert to array
        valid_features = [f for f in all_features if f is not None]
        
        if valid_features:
            return np.array(valid_features)
        else:
            return np.array([])
    
    def compute_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Compute cosine similarity between two feature vectors.
        
        Args:
            features1: First feature vector
            features2: Second feature vector
            
        Returns:
            Similarity score between 0 and 1
        """
        similarity = np.dot(features1, features2)
        return float(similarity)
