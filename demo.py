"""
Demo script to test the Visual Search Engine functionality.
This script creates sample images and demonstrates the search capabilities.
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

def create_sample_images():
    """Create sample images with text for testing."""
    sample_dir = Path('./sample_images')
    sample_dir.mkdir(exist_ok=True)
    
    print("🎨 Creating sample images for testing...")
    
    # Define sample images with text
    samples = [
        ('Hello World', (255, 100, 100)),
        ('Python Programming', (100, 255, 100)),
        ('Machine Learning', (100, 100, 255)),
        ('Computer Vision', (255, 255, 100)),
        ('Data Science', (255, 100, 255)),
        ('Artificial Intelligence', (100, 255, 255)),
        ('Deep Learning', (200, 150, 100)),
        ('Neural Networks', (150, 200, 100)),
        ('Image Processing', (100, 150, 200)),
        ('Pattern Recognition', (200, 100, 150)),
    ]
    
    for i, (text, color) in enumerate(samples, 1):
        # Create image
        img = Image.new('RGB', (400, 300), color=color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((400 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        # Add some random shapes
        for _ in range(5):
            x1 = random.randint(0, 350)
            y1 = random.randint(0, 250)
            x2 = x1 + random.randint(20, 50)
            y2 = y1 + random.randint(20, 50)
            shape_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.rectangle([x1, y1, x2, y2], outline=shape_color, width=2)
        
        # Save image
        filename = f'sample_{i:02d}_{text.lower().replace(" ", "_")}.jpg'
        img.save(sample_dir / filename, 'JPEG')
        print(f"  ✓ Created {filename}")
    
    print(f"\n✅ Created {len(samples)} sample images in {sample_dir}")
    print(f"📁 You can now use these images to test the search engine!")


def print_usage():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("📚 USAGE INSTRUCTIONS")
    print("="*60)
    print("\n1. Start the server:")
    print("   ./start.sh  (Linux/Mac)")
    print("   start.bat   (Windows)")
    print("   OR: python app.py")
    
    print("\n2. Open your browser:")
    print("   http://localhost:5000")
    
    print("\n3. Build the index:")
    print("   - Click 'Build Index' button")
    print("   - Wait for indexing to complete")
    
    print("\n4. Try searching:")
    print("   - Visual Search: Upload one of the sample images")
    print("   - Text Search: Search for 'Python', 'Learning', etc.")
    print("   - Hybrid Search: Combine both!")
    
    print("\n5. Add your own images:")
    print("   - Copy images to ./sample_images")
    print("   - Or add your directory in the web interface")
    print("   - Rebuild the index")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    print("\n🚀 Visual Search Engine - Demo Setup\n")
    
    try:
        create_sample_images()
        print_usage()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
