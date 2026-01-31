"""
Basic tests for Visual Search Engine components.
"""
import unittest
import os
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import Config, FileScanner


class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_loads(self):
        """Test that config loads successfully."""
        config = Config('config.yaml')
        self.assertIsNotNone(config.config)
    
    def test_get_methods(self):
        """Test config getter methods."""
        config = Config('config.yaml')
        self.assertIsNotNone(config.get_scan_directories())
        self.assertIsNotNone(config.get_image_extensions())
        self.assertIsNotNone(config.get_model_config())


class TestFileScanner(unittest.TestCase):
    """Test file scanner functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = './test_images'
        Path(self.test_dir).mkdir(exist_ok=True)
    
    def test_scanner_initialization(self):
        """Test scanner initializes correctly."""
        scanner = FileScanner(['.jpg', '.png'])
        self.assertEqual(scanner.extensions, ['.jpg', '.png'])
    
    def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        scanner = FileScanner()
        images = scanner.scan_directory(self.test_dir)
        self.assertEqual(len(images), 0)
    
    def test_is_image_file(self):
        """Test image file detection."""
        scanner = FileScanner()
        self.assertTrue(scanner._is_image_file('test.jpg'))
        self.assertTrue(scanner._is_image_file('test.PNG'))
        self.assertFalse(scanner._is_image_file('test.txt'))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction."""
    
    def test_extractor_initialization(self):
        """Test that feature extractor initializes."""
        # This test requires tensorflow, so we'll skip if not available
        try:
            from backend import FeatureExtractor
            extractor = FeatureExtractor('vgg16')
            self.assertIsNotNone(extractor.model)
        except ImportError:
            self.skipTest("TensorFlow not available")


if __name__ == '__main__':
    unittest.main()
