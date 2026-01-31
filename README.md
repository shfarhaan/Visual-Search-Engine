# Visual Search Engine

A complete deployable visual search engine that can search through your device looking for patterns, visual similarities, or text in images using OCR.

## Features

- **Visual Search**: Find similar images based on visual patterns and features
- **Text Search**: Search for text within images using OCR (Optical Character Recognition)
- **Pattern Recognition**: Identify visual patterns across your image collection
- **Device Scanning**: Automatically index images from specified directories on your device
- **Web Interface**: Easy-to-use web interface for searching and viewing results

## Architecture

The system uses:
- **VGG16/ResNet** pre-trained models for image feature extraction
- **EasyOCR** for text recognition in images
- **FAISS** for efficient similarity search
- **Flask** for REST API backend
- **Simple HTML/JS** frontend for user interface

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) GPU support for faster processing

### Setup

1. Clone the repository:
```bash
git clone https://github.com/shfarhaan/Visual-Search-Engine.git
cd Visual-Search-Engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For OCR with Tesseract (optional, EasyOCR is default):
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Usage

### Quick Start

1. Start the server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Configure the directories you want to index in the web interface

4. Upload an image or enter text to search

### API Endpoints

- `POST /api/index` - Index images from specified directories
- `POST /api/search/visual` - Search for visually similar images
- `POST /api/search/text` - Search for text in images using OCR
- `GET /api/status` - Get indexing status

## Configuration

Create a `config.yaml` file to customize settings:

```yaml
# Directories to scan for images
scan_directories:
  - /path/to/your/images
  - /path/to/another/folder

# Image extensions to index
image_extensions:
  - .jpg
  - .jpeg
  - .png
  - .gif
  - .bmp

# Model settings
model:
  name: vgg16  # or resnet50
  embedding_size: 512

# OCR settings
ocr:
  enabled: true
  languages: ['en']  # Add more language codes as needed
```

## Project Structure

```
Visual-Search-Engine/
├── app.py                 # Main Flask application
├── backend/
│   ├── feature_extractor.py    # Image feature extraction
│   ├── ocr_engine.py            # OCR processing
│   ├── indexer.py               # Image indexing system
│   └── search_engine.py         # Search functionality
├── frontend/
│   └── static files & templates
├── models/
│   └── saved models and weights
├── utils/
│   ├── config.py          # Configuration management
│   └── file_scanner.py    # Device file scanning
├── static/               # Static assets (CSS, JS)
├── templates/            # HTML templates
└── requirements.txt      # Python dependencies
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Building for Production

The application can be deployed using Docker:

```bash
docker build -t visual-search-engine .
docker run -p 5000:5000 -v /your/image/path:/data visual-search-engine
```

## Performance

- **Indexing Speed**: ~10-20 images/second (CPU), ~50-100 images/second (GPU)
- **Search Speed**: <100ms for databases up to 100k images
- **OCR Speed**: ~1-2 seconds per image

## Limitations

- Large image collections (>1M images) may require more RAM for in-memory indexing
- OCR accuracy depends on image quality and text clarity
- Initial indexing can take time for large directories

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Pre-trained models from TensorFlow/Keras
- EasyOCR for text recognition
- FAISS for efficient similarity search
