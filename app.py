"""
Flask application for Visual Search Engine.
Main entry point for the web server.
"""
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import logging
from pathlib import Path
import traceback
from werkzeug.utils import secure_filename
import threading

# Import our backend modules
from backend import FeatureExtractor, OCREngine, ImageIndexer, SearchEngine
from utils import Config, FileScanner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load configuration
config = Config('config.yaml')

# Setup upload folder
UPLOAD_FOLDER = './uploads'
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# Global variables for our components
feature_extractor = None
ocr_engine = None
indexer = None
search_engine = None
indexing_status = {
    'is_indexing': False,
    'progress': 0,
    'total': 0,
    'message': 'Not indexed'
}
indexing_lock = threading.Lock()  # Thread-safe lock for indexing status


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_components():
    """Initialize all backend components."""
    global feature_extractor, ocr_engine, indexer, search_engine
    
    try:
        logger.info("Initializing components...")
        
        # Initialize feature extractor
        model_config = config.get_model_config()
        feature_extractor = FeatureExtractor(
            model_name=model_config.get('name', 'vgg16'),
            embedding_size=model_config.get('embedding_size', 512)
        )
        
        # Initialize OCR engine
        ocr_config = config.get_ocr_config()
        if ocr_config.get('enabled', True):
            ocr_engine = OCREngine(
                languages=ocr_config.get('languages', ['en']),
                use_gpu=ocr_config.get('gpu', False)
            )
        
        # Initialize indexer
        storage_config = config.get_storage_config()
        indexer = ImageIndexer(storage_config)
        
        # Try to load existing index
        if indexer.load_index():
            logger.info("Loaded existing index")
            indexing_status['message'] = f'Loaded {len(indexer.metadata)} images'
        else:
            logger.info("No existing index found")
            indexing_status['message'] = 'No index found - please index images'
        
        # Initialize search engine
        search_config = config.get_search_config()
        search_engine = SearchEngine(feature_extractor, indexer, search_config)
        
        logger.info("All components initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        logger.error(traceback.format_exc())
        return False


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current indexing status and statistics."""
    try:
        stats = {
            'indexing_status': indexing_status,
            'is_ready': indexer is not None and indexer.is_indexed
        }
        
        if indexer and indexer.is_indexed:
            stats['index_stats'] = indexer.get_statistics()
        
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/index', methods=['POST'])
def build_index():
    """Build index from specified directories."""
    global indexing_status
    
    try:
        data = request.get_json()
        directories = data.get('directories', config.get_scan_directories())
        
        # Thread-safe check for concurrent indexing
        with indexing_lock:
            if indexing_status['is_indexing']:
                return jsonify({'error': 'Indexing already in progress'}), 400
            indexing_status['is_indexing'] = True
        
        
        indexing_status['progress'] = 0
        indexing_status['message'] = 'Starting indexing...'
        
        # Scan for images
        logger.info(f"Scanning directories: {directories}")
        file_scanner = FileScanner(config.get_image_extensions())
        image_paths = file_scanner.scan_multiple_directories(directories)
        
        if not image_paths:
            indexing_status['is_indexing'] = False
            indexing_status['message'] = 'No images found'
            return jsonify({'error': 'No images found in specified directories'}), 404
        
        indexing_status['total'] = len(image_paths)
        indexing_status['message'] = f'Found {len(image_paths)} images'
        
        # Extract features
        logger.info("Extracting features...")
        indexing_status['message'] = 'Extracting features...'
        features = feature_extractor.extract_features_batch(
            image_paths,
            batch_size=config.get('model.batch_size', 32)
        )
        
        # Extract OCR text if enabled
        ocr_results = None
        if ocr_engine and config.get('ocr.enabled', True):
            logger.info("Extracting text with OCR...")
            indexing_status['message'] = 'Extracting text from images...'
            ocr_results = ocr_engine.extract_text_batch(image_paths)
        
        # Build index
        logger.info("Building index...")
        indexing_status['message'] = 'Building index...'
        indexer.build_index(image_paths, features, ocr_results)
        
        # Save index
        logger.info("Saving index...")
        indexing_status['message'] = 'Saving index...'
        indexer.save_index()
        
        indexing_status['is_indexing'] = False
        indexing_status['progress'] = len(image_paths)
        indexing_status['message'] = f'Indexed {len(image_paths)} images successfully'
        
        return jsonify({
            'success': True,
            'indexed_images': len(image_paths),
            'stats': indexer.get_statistics()
        }), 200
        
    except Exception as e:
        logger.error(f"Error building index: {e}")
        logger.error(traceback.format_exc())
        indexing_status['is_indexing'] = False
        indexing_status['message'] = f'Error: {str(e)}'
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/visual', methods=['POST'])
def search_visual():
    """Search for visually similar images."""
    try:
        if not indexer or not indexer.is_indexed:
            return jsonify({'error': 'Index not built. Please index images first.'}), 400
        
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Get top_k parameter
            top_k = request.form.get('top_k', config.get('search.top_k', 20))
            top_k = int(top_k)
            
            # Perform search
            results = search_engine.search_by_image(filepath, top_k=top_k)
        finally:
            # Always clean up uploaded file, even if search fails
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in visual search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/text', methods=['POST'])
def search_text():
    """Search for text in images using OCR."""
    try:
        if not indexer or not indexer.is_indexed:
            return jsonify({'error': 'Index not built. Please index images first.'}), 400
        
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Get max_results parameter
        max_results = data.get('max_results', config.get('search.top_k', 20))
        
        # Perform text search
        results = search_engine.search_by_text(query, max_results=max_results)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in text search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/search/hybrid', methods=['POST'])
def search_hybrid():
    """Hybrid search using both visual and text queries."""
    try:
        if not indexer or not indexer.is_indexed:
            return jsonify({'error': 'Index not built. Please index images first.'}), 400
        
        query_text = request.form.get('query', '')
        query_image = None
        
        # Check for uploaded image
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                query_image = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(query_image)
        
        if not query_text and not query_image:
            return jsonify({'error': 'No query provided'}), 400
        
        # Get top_k parameter
        top_k = int(request.form.get('top_k', config.get('search.top_k', 20)))
        
        try:
            # Perform hybrid search
            results = search_engine.hybrid_search(
                query_image_path=query_image,
                query_text=query_text if query_text else None,
                top_k=top_k
            )
        finally:
            # Clean up uploaded file
            if query_image and os.path.exists(query_image):
                os.remove(query_image)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in hybrid search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/image/<path:filepath>')
def serve_image(filepath):
    """Serve an indexed image."""
    try:
        # Security: normalize path to prevent directory traversal
        filepath = os.path.normpath(filepath)
        
        if os.path.exists(filepath) and os.path.isfile(filepath):
            directory = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            return send_from_directory(directory, filename)
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Initialize components on startup
    if initialize_components():
        # Get server config
        server_config = config.get_server_config()
        host = server_config.get('host', '0.0.0.0')
        port = server_config.get('port', 5000)
        debug = server_config.get('debug', True)
        
        logger.info(f"Starting Visual Search Engine on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    else:
        logger.error("Failed to initialize components. Exiting.")
