"""Configuration management for Visual Search Engine."""
import yaml
import os
from pathlib import Path


class Config:
    """Configuration class to load and manage settings."""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize configuration from YAML file."""
        self.config_path = config_path
        self.config = self._load_config()
        self._ensure_directories()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration
            return {
                'scan_directories': ['./sample_images'],
                'image_extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
                'model': {'name': 'vgg16', 'embedding_size': 512, 'batch_size': 32},
                'ocr': {'enabled': True, 'languages': ['en'], 'gpu': False},
                'search': {'top_k': 20, 'similarity_threshold': 0.7},
                'storage': {
                    'index_path': './data/image_index.pkl',
                    'embeddings_path': './data/embeddings.npy',
                    'metadata_path': './data/metadata.json',
                    'ocr_index_path': './data/ocr_index.pkl'
                },
                'server': {'host': '0.0.0.0', 'port': 5000, 'debug': True}
            }
    
    def _ensure_directories(self):
        """Ensure required directories exist."""
        # Create data directory
        data_dir = Path('./data')
        data_dir.mkdir(exist_ok=True)
        
        # Create sample images directory if specified
        for scan_dir in self.config.get('scan_directories', []):
            Path(scan_dir).mkdir(parents=True, exist_ok=True)
    
    def get(self, key, default=None):
        """Get configuration value by key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def get_scan_directories(self):
        """Get list of directories to scan."""
        return self.config.get('scan_directories', [])
    
    def get_image_extensions(self):
        """Get list of supported image extensions."""
        return self.config.get('image_extensions', ['.jpg', '.jpeg', '.png'])
    
    def get_model_config(self):
        """Get model configuration."""
        return self.config.get('model', {})
    
    def get_ocr_config(self):
        """Get OCR configuration."""
        return self.config.get('ocr', {})
    
    def get_search_config(self):
        """Get search configuration."""
        return self.config.get('search', {})
    
    def get_storage_config(self):
        """Get storage configuration."""
        return self.config.get('storage', {})
    
    def get_server_config(self):
        """Get server configuration."""
        return self.config.get('server', {})
