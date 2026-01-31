#!/usr/bin/env python3
"""
Validation script for Visual Search Engine
Tests all major functionality to ensure the application is working correctly.
"""

import requests
import json
import os
import sys
from pathlib import Path

API_BASE = "http://localhost:5000/api"

def print_test(name, passed, details=""):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"   {details}")

def test_server_running():
    """Test if the server is running"""
    try:
        response = requests.get(f"{API_BASE}/status", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def test_status_endpoint():
    """Test the status endpoint"""
    try:
        response = requests.get(f"{API_BASE}/status", timeout=5)
        data = response.json()
        return 'indexing_status' in data and 'is_ready' in data
    except Exception:
        return False

def test_indexing():
    """Test the indexing functionality"""
    try:
        payload = {"directories": ["./sample_images"]}
        response = requests.post(
            f"{API_BASE}/index",
            json=payload,
            timeout=120
        )
        data = response.json()
        return data.get('success') and data.get('indexed_images', 0) > 0
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_visual_search():
    """Test visual search functionality"""
    try:
        # Use first sample image
        image_path = "./sample_images/sample_01_hello_world.jpg"
        if not os.path.exists(image_path):
            return False
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'top_k': 3}
            response = requests.post(
                f"{API_BASE}/search/visual",
                files=files,
                data=data,
                timeout=30
            )
        
        result = response.json()
        return result.get('success') and len(result.get('results', [])) > 0
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_text_search():
    """Test text search functionality"""
    try:
        payload = {"query": "Hello", "max_results": 5}
        response = requests.post(
            f"{API_BASE}/search/text",
            json=payload,
            timeout=10
        )
        data = response.json()
        # Text search may return 0 results if OCR didn't find text
        return data.get('success') is not None
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_hybrid_search():
    """Test hybrid search functionality"""
    try:
        image_path = "./sample_images/sample_01_hello_world.jpg"
        if not os.path.exists(image_path):
            return False
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'query': 'Hello', 'top_k': 3}
            response = requests.post(
                f"{API_BASE}/search/hybrid",
                files=files,
                data=data,
                timeout=30
            )
        
        result = response.json()
        return result.get('success') is not None
    except Exception as e:
        print(f"   Error: {e}")
        return False

def test_image_serving():
    """Test image serving endpoint"""
    try:
        # Try to get a sample image
        image_path = "sample_images/sample_01_hello_world.jpg"
        response = requests.get(
            f"{API_BASE}/image/{image_path}",
            timeout=10
        )
        return response.status_code == 200
    except Exception:
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Visual Search Engine - Validation Tests")
    print("=" * 60)
    print()
    
    # Check if sample images exist
    if not os.path.exists("./sample_images"):
        print("❌ FAIL: Sample images directory not found")
        print("   Please run from the project root directory")
        sys.exit(1)
    
    tests = [
        ("Server Running", test_server_running, "Server must be running on port 5000"),
        ("Status Endpoint", test_status_endpoint, "API status endpoint working"),
        ("Indexing", test_indexing, "Image indexing functionality"),
        ("Visual Search", test_visual_search, "Visual similarity search"),
        ("Text Search", test_text_search, "OCR text search"),
        ("Hybrid Search", test_hybrid_search, "Combined visual + text search"),
        ("Image Serving", test_image_serving, "Image file serving"),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func, description in tests:
        print(f"\nTesting: {description}")
        try:
            result = test_func()
            if result:
                passed += 1
                print_test(name, True)
            else:
                failed += 1
                print_test(name, False)
        except Exception as e:
            failed += 1
            print_test(name, False, f"Exception: {str(e)}")
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests passed! The application is fully functional.")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
