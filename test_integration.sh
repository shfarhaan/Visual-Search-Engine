#!/bin/bash
# Integration test script for Visual Search Engine

echo "🧪 Running Integration Tests for Visual Search Engine"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track test results
PASSED=0
FAILED=0

# Function to run a test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Testing: ${test_name}${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Check Python version
run_test "Python Version (3.8+)" "python3 --version | grep -E 'Python 3\.(8|9|10|11|12)'"

# Test 2: Check directory structure
run_test "Directory Structure" "test -d backend && test -d utils && test -d static && test -d templates"

# Test 3: Check required files
run_test "Required Files" "test -f app.py && test -f config.yaml && test -f requirements.txt"

# Test 4: Check sample images
run_test "Sample Images" "test -d sample_images && ls sample_images/*.jpg | wc -l | grep -E '[1-9][0-9]*'"

# Test 5: Config module
run_test "Config Module" "python3 -c 'from utils import Config; c = Config(); print(c.get_scan_directories())'"

# Test 6: File Scanner module
run_test "File Scanner Module" "python3 -c 'from utils import FileScanner; s = FileScanner(); images = s.scan_directory(\"./sample_images\"); print(len(images))'"

# Test 7: Unit tests
run_test "Unit Tests" "python3 -m unittest discover tests/ -q 2>&1 | grep -q 'OK'"

# Test 8: Check imports
run_test "Backend Imports" "python3 -c 'import sys; sys.path.insert(0, \".\"); from backend import ImageIndexer, SearchEngine' 2>&1 | grep -v 'tensorflow'"

echo ""
echo "======================================================"
echo -e "Test Results: ${GREEN}${PASSED} passed${NC}, ${RED}${FAILED} failed${NC}"
echo "======================================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC} ✨"
    echo ""
    echo "You can now start the application:"
    echo "  ./start.sh  (or start.bat on Windows)"
    echo "  OR: python app.py"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC} Please check the errors above."
    exit 1
fi
