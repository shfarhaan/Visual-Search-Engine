# Visual Search Engine - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│                    (User Interface - HTML/CSS/JS)                │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Web Server                             │
│                        (app.py)                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              REST API Endpoints                          │   │
│  │  • /api/index       - Build search index                │   │
│  │  • /api/search/visual - Visual similarity search        │   │
│  │  • /api/search/text   - OCR text search                 │   │
│  │  • /api/search/hybrid - Combined search                 │   │
│  │  • /api/status      - System status                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Components                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Search Engine (search_engine.py)                │   │
│  │  • Visual Search      • Text Search                     │   │
│  │  • Hybrid Search      • Similarity Ranking              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                        │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │                                                           │   │
│  │  ┌────────────────────┐        ┌────────────────────┐   │   │
│  │  │  Feature Extractor │        │    OCR Engine      │   │   │
│  │  │ (feature_extract)  │        │  (ocr_engine.py)   │   │   │
│  │  │                    │        │                    │   │   │
│  │  │ • VGG16/ResNet50   │        │ • EasyOCR          │   │   │
│  │  │ • Image embeddings │        │ • Text extraction  │   │   │
│  │  └────────────────────┘        └────────────────────┘   │   │
│  │                                                           │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │          Image Indexer (indexer.py)                     │   │
│  │  • Build index        • Save/Load index                 │   │
│  │  • Metadata storage   • OCR text index                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Utilities                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  File Scanner (file_scanner.py)                          │   │
│  │  • Scan directories    • Find images                    │   │
│  │  • Validate files      • Filter by extension            │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Config Manager (config.py)                              │   │
│  │  • Load YAML config    • Manage settings                │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                 │
│  • data/embeddings.npy      - Feature vectors                   │
│  • data/metadata.json       - Image metadata                    │
│  • data/ocr_index.pkl       - OCR text index                    │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Indexing Flow

```
User → Web UI → POST /api/index
  ↓
Flask Server receives directories list
  ↓
File Scanner → Scan directories for images
  ↓
Feature Extractor → Extract visual features (VGG16/ResNet)
  ↓
OCR Engine → Extract text from images (EasyOCR)
  ↓
Indexer → Build searchable index
  ↓
Storage → Save embeddings, metadata, OCR index
  ↓
Response → Status and statistics
```

### 2. Visual Search Flow

```
User → Upload image → POST /api/search/visual
  ↓
Flask Server receives image file
  ↓
Feature Extractor → Extract features from query image
  ↓
Search Engine → Compute similarity with all indexed images
  ↓
Ranking → Sort by cosine similarity
  ↓
Filter → Apply similarity threshold
  ↓
Response → Top-K similar images with scores
```

### 3. Text Search Flow

```
User → Enter text query → POST /api/search/text
  ↓
Flask Server receives text query
  ↓
Search Engine → Query OCR index
  ↓
Word Matching → Find images containing query words
  ↓
Phrase Matching → Search full OCR text
  ↓
Response → Matching images with OCR text
```

## Key Components

### Frontend (templates/index.html, static/)
- **HTML Interface**: Single-page application with tabs
- **JavaScript**: Handles API calls, file uploads, result display
- **CSS**: Responsive design with modern styling

### Backend (backend/)
- **Feature Extractor**: Uses pre-trained CNNs for image embeddings
  - VGG16: Fast, 512-dimensional features
  - ResNet50: More accurate, deeper network
  
- **OCR Engine**: Text extraction from images
  - EasyOCR: Primary OCR engine (GPU support)
  - Pytesseract: Fallback option
  
- **Indexer**: Manages the searchable database
  - Stores embeddings as NumPy arrays
  - Maintains metadata as JSON
  - Creates inverted index for text search
  
- **Search Engine**: Coordinates search operations
  - Visual search using cosine similarity
  - Text search using inverted index
  - Hybrid search combining both

### Utilities (utils/)
- **File Scanner**: Discovers images in directories
- **Config Manager**: Handles YAML configuration

## Performance Characteristics

### Indexing
- **Speed**: 10-20 images/sec (CPU), 50-100 images/sec (GPU)
- **Memory**: ~2MB per 1000 images for features
- **Disk**: Minimal (compressed features + metadata)

### Search
- **Latency**: <100ms for 100k images
- **Scalability**: Linear with number of indexed images
- **Accuracy**: Depends on model (VGG16 vs ResNet50)

### OCR
- **Speed**: 1-2 seconds per image
- **Accuracy**: High for clear, well-lit text
- **Languages**: Supports multiple languages

## Security Considerations

1. **File Upload Validation**: Only allowed image extensions
2. **Path Sanitization**: Prevents directory traversal
3. **Size Limits**: 16MB max upload size
4. **Input Validation**: Query parameters validated

## Scalability Options

1. **Horizontal Scaling**: Run multiple instances behind load balancer
2. **Database**: Replace file storage with PostgreSQL/MongoDB
3. **Vector Database**: Use Pinecone, Milvus, or FAISS for large scale
4. **Caching**: Add Redis for frequent queries
5. **CDN**: Serve images from CDN for better performance

## Future Enhancements

1. **Advanced Features**:
   - Face recognition
   - Object detection
   - Scene classification
   
2. **Performance**:
   - GPU acceleration
   - Batch processing
   - Async indexing
   
3. **Features**:
   - Multi-modal search
   - Fuzzy text matching
   - Duplicate detection
   
4. **UI**:
   - Drag-and-drop upload
   - Real-time preview
   - Advanced filters

## Technology Stack

- **Backend**: Python 3.8+, Flask
- **ML/CV**: TensorFlow, Keras, OpenCV
- **OCR**: EasyOCR, Tesseract
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Storage**: File system (NumPy, JSON, Pickle)
- **Deployment**: Docker, Docker Compose
