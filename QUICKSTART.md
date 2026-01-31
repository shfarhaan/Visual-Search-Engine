# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create Sample Images (Optional)

```bash
python demo.py
```

This will create sample images with text in the `sample_images` directory.

### Step 3: Start the Server

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

**Or directly with Python:**
```bash
python app.py
```

### Step 4: Access the Web Interface

Open your browser and go to:
```
http://localhost:5000
```

## 📖 How to Use

### 1. Index Your Images

1. In the web interface, enter the directories you want to scan
2. Click "Build Index"
3. Wait for the indexing process to complete

Default directory: `./sample_images`

### 2. Search Images

#### Visual Search
- Upload an image
- The system will find visually similar images

#### Text Search
- Enter text to search for
- The system will find images containing that text (using OCR)

#### Hybrid Search
- Combine both image and text queries
- Get results matching both criteria

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
docker-compose up -d
```

The application will be available at `http://localhost:5000`

### Using Docker directly

```bash
# Build the image
docker build -t visual-search-engine .

# Run the container
docker run -p 5000:5000 -v $(pwd)/sample_images:/app/sample_images visual-search-engine
```

## 🔧 Configuration

Edit `config.yaml` to customize:

- Scan directories
- Image extensions
- Model settings (VGG16 or ResNet50)
- OCR languages
- Search parameters

## 📝 Examples

### Indexing Custom Directories

In the web interface, add your directories:
```
/path/to/your/photos
/path/to/documents
./my_images
```

### API Usage

You can also use the REST API directly:

**Build Index:**
```bash
curl -X POST http://localhost:5000/api/index \
  -H "Content-Type: application/json" \
  -d '{"directories": ["./sample_images"]}'
```

**Visual Search:**
```bash
curl -X POST http://localhost:5000/api/search/visual \
  -F "image=@query_image.jpg" \
  -F "top_k=20"
```

**Text Search:**
```bash
curl -X POST http://localhost:5000/api/search/text \
  -H "Content-Type: application/json" \
  -d '{"query": "Python", "max_results": 20}'
```

## 🐛 Troubleshooting

### TensorFlow Installation Issues

If you encounter issues with TensorFlow:

```bash
pip install tensorflow==2.15.0 --upgrade
```

### OCR Not Working

Install Tesseract OCR:

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Out of Memory

For large image collections, you may need to:
- Reduce batch size in `config.yaml`
- Use a machine with more RAM
- Process images in smaller batches

## 📊 Performance Tips

1. **Use GPU**: If you have a GPU, install tensorflow-gpu for faster processing
2. **Adjust Batch Size**: Increase for faster indexing (if you have enough RAM)
3. **Choose Model**: VGG16 is faster, ResNet50 is more accurate
4. **Disable OCR**: If you don't need text search, disable OCR for faster indexing

## 🎯 Next Steps

1. Index your own image collection
2. Experiment with different search queries
3. Customize the configuration for your needs
4. Integrate the API into your applications

## 💡 Tips

- For best OCR results, use high-quality images with clear text
- Visual search works best with similar image types (photos, logos, diagrams)
- You can re-index anytime to add new images
- The index is saved to disk and loaded on startup

## 🆘 Need Help?

Check the main README.md for more detailed information and troubleshooting.
