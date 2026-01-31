"""File scanner utility to find images on device."""
import os
from pathlib import Path
from typing import List, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileScanner:
    """Scanner to find image files in specified directories."""
    
    def __init__(self, extensions: List[str] = None):
        """
        Initialize file scanner.
        
        Args:
            extensions: List of file extensions to scan (e.g., ['.jpg', '.png'])
        """
        self.extensions = extensions or ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        # Convert to lowercase for case-insensitive matching
        self.extensions = [ext.lower() for ext in self.extensions]
    
    def scan_directory(self, directory: str, recursive: bool = True) -> List[str]:
        """
        Scan directory for image files.
        
        Args:
            directory: Path to directory to scan
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            List of image file paths found
        """
        image_files = []
        directory = Path(directory)
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return image_files
        
        if not directory.is_dir():
            logger.warning(f"Path is not a directory: {directory}")
            return image_files
        
        try:
            if recursive:
                # Recursively find all files
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self._is_image_file(file_path):
                            image_files.append(file_path)
            else:
                # Only scan top level
                for file in directory.iterdir():
                    if file.is_file() and self._is_image_file(str(file)):
                        image_files.append(str(file))
            
            logger.info(f"Found {len(image_files)} images in {directory}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        return image_files
    
    def scan_multiple_directories(self, directories: List[str], recursive: bool = True) -> List[str]:
        """
        Scan multiple directories for image files.
        
        Args:
            directories: List of directory paths to scan
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            List of unique image file paths found across all directories
        """
        all_images = []
        seen_paths = set()
        
        for directory in directories:
            images = self.scan_directory(directory, recursive)
            for img in images:
                # Normalize path and check for duplicates
                normalized_path = os.path.normpath(os.path.abspath(img))
                if normalized_path not in seen_paths:
                    seen_paths.add(normalized_path)
                    all_images.append(img)
        
        logger.info(f"Total unique images found: {len(all_images)}")
        return all_images
    
    def _is_image_file(self, file_path: str) -> bool:
        """
        Check if file is an image based on extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file has image extension, False otherwise
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.extensions
    
    def validate_image(self, file_path: str) -> bool:
        """
        Validate that file is actually a readable image.
        
        Args:
            file_path: Path to image file
            
        Returns:
            True if image can be opened, False otherwise
        """
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.debug(f"Invalid image {file_path}: {e}")
            return False
