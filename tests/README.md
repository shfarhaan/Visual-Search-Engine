# Visual Search Engine Tests

This directory contains tests for the Visual Search Engine.

## Running Tests

To run all tests:

```bash
python -m pytest tests/
```

Or using unittest:

```bash
python -m unittest discover tests/
```

## Test Coverage

- `test_basic.py` - Basic functionality tests for configuration and file scanning
- More tests can be added as needed

## Note

Some tests require TensorFlow and other ML dependencies to be installed.
Tests will be skipped if dependencies are not available.
