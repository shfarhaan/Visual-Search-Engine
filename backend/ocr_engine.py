"""OCR engine for extracting text from images."""
import logging
from typing import List, Dict, Tuple
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """Extract text from images using OCR."""
    
    def __init__(self, languages: List[str] = None, use_gpu: bool = False):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes (e.g., ['en', 'es'])
            use_gpu: Whether to use GPU for processing
        """
        self.languages = languages or ['en']
        self.use_gpu = use_gpu
        self.reader = None
        self._load_ocr_engine()
    
    def _load_ocr_engine(self):
        """Load the OCR engine."""
        try:
            import easyocr
            logger.info(f"Loading EasyOCR with languages: {self.languages}")
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.use_gpu,
                verbose=False
            )
            logger.info("EasyOCR loaded successfully")
        except ImportError:
            logger.warning("EasyOCR not available, trying pytesseract")
            try:
                import pytesseract
                self.reader = 'pytesseract'
                logger.info("Using pytesseract as fallback")
            except ImportError:
                logger.error("No OCR engine available. Install easyocr or pytesseract.")
                self.reader = None
    
    def extract_text(self, image_path: str) -> Dict[str, any]:
        """
        Extract text from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted text and metadata:
            {
                'text': str,  # Full extracted text
                'words': List[str],  # Individual words
                'confidences': List[float],  # Confidence scores
                'boxes': List[Tuple],  # Bounding boxes for each text region
            }
        """
        if self.reader is None:
            return {'text': '', 'words': [], 'confidences': [], 'boxes': []}
        
        try:
            if self.reader == 'pytesseract':
                return self._extract_with_pytesseract(image_path)
            else:
                return self._extract_with_easyocr(image_path)
        except Exception as e:
            logger.error(f"Error extracting text from {image_path}: {e}")
            return {'text': '', 'words': [], 'confidences': [], 'boxes': []}
    
    def _extract_with_easyocr(self, image_path: str) -> Dict[str, any]:
        """Extract text using EasyOCR."""
        results = self.reader.readtext(image_path)
        
        text_parts = []
        words = []
        confidences = []
        boxes = []
        
        for detection in results:
            box, text, confidence = detection
            text_parts.append(text)
            words.extend(text.split())
            confidences.append(confidence)
            boxes.append(box)
        
        full_text = ' '.join(text_parts)
        
        return {
            'text': full_text,
            'words': words,
            'confidences': confidences,
            'boxes': boxes
        }
    
    def _extract_with_pytesseract(self, image_path: str) -> Dict[str, any]:
        """Extract text using pytesseract."""
        import pytesseract
        from pytesseract import Output
        
        img = Image.open(image_path)
        
        # Get detailed information
        data = pytesseract.image_to_data(img, output_type=Output.DICT)
        
        # Extract text and metadata
        text_parts = []
        words = []
        confidences = []
        boxes = []
        
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # Only include confident detections
                text = data['text'][i]
                if text.strip():
                    text_parts.append(text)
                    words.append(text)
                    confidences.append(float(data['conf'][i]) / 100.0)
                    
                    # Create bounding box
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    box = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                    boxes.append(box)
        
        full_text = ' '.join(text_parts)
        
        return {
            'text': full_text,
            'words': words,
            'confidences': confidences,
            'boxes': boxes
        }
    
    def search_text_in_image(self, image_path: str, query: str) -> bool:
        """
        Check if query text exists in the image.
        
        Args:
            image_path: Path to the image file
            query: Text to search for
            
        Returns:
            True if query found in image, False otherwise
        """
        result = self.extract_text(image_path)
        text = result['text'].lower()
        query = query.lower()
        return query in text
    
    def extract_text_batch(self, image_paths: List[str]) -> List[Dict[str, any]]:
        """
        Extract text from multiple images.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of results for each image
        """
        results = []
        for i, path in enumerate(image_paths):
            result = self.extract_text(path)
            results.append(result)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Processed OCR for {i + 1}/{len(image_paths)} images")
        
        return results
