# Photo Annotation Tool

A robust, test-driven web application for manual photo annotation with CSV export capabilities. Built with Python, FastAPI, and modern web technologies to provide a seamless experience for annotating images with descriptions, tags, and labels.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Test Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)

## ( Features

### Core Functionality
- **=� Image Upload**: Drag-and-drop or browse upload with support for multiple files
- **=� Rich Annotations**: Add descriptions, tags, and labels to each image
- **= Image Grid View**: Browse uploaded photos as responsive thumbnails
- **=� CSV Export**: Download all annotations as structured CSV data
- **=� Statistics**: View annotation statistics and most common tags/labels

### Technical Features
- **= Security**: File validation, sanitization, and size limits
- **=� Responsive Design**: Works seamlessly on desktop and mobile
- **� Fast Processing**: Optimized image handling and thumbnail generation
- **>� High Test Coverage**: 88% coverage with comprehensive test suite
- **=� Production Ready**: Built with modern Python web stack

### Supported Formats
- **Image Types**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **File Size**: Up to 10MB per image
- **Batch Upload**: Multiple files at once

## =� Quick Start

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/photo-annotation-tool.git
   cd photo-annotation-tool
   ```

2. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync --dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Run tests** (recommended):
   ```bash
   uv run pytest -v
   ```

4. **Start the application**:
   ```bash
   uv run uvicorn src.photo_annotator.main:app --reload --port 8001
   ```

5. **Open your browser**:
   Navigate to `http://localhost:8001`

## =� Usage Guide

### Uploading Photos

1. **Drag & Drop**: Simply drag image files onto the upload zone
2. **Browse Files**: Click "browse" to select files manually
3. **Batch Upload**: Select multiple files for simultaneous upload
4. **Progress Tracking**: Monitor upload progress with visual indicators

### Annotating Images

1. **Select Image**: Click any thumbnail in the photo grid
2. **Add Description**: Enter a detailed description (required)
3. **Add Tags**: Include comma-separated tags (optional)
4. **Add Labels**: Include comma-separated labels (optional)
5. **Save**: Click "Save Annotation" to persist the data

**Visual Indicators & Editing:**
- **Green Checkmarks**: Photos with annotations display a green checkmark in the top-left corner
- **Edit Existing**: Click on annotated photos to automatically load existing data for editing
- **Visual Feedback**: Instantly see which photos have been annotated without opening them

### Exporting Data

- Click **"Export CSV"** to download all annotations
- CSV includes: `image_name`, `description`, `tags`, `labels`, `timestamp`
- File is automatically named `annotations.csv`

## <� Architecture

### Project Structure
```
photo-annotation-tool/
   src/photo_annotator/           # Main application code
      api/                       # FastAPI routes and endpoints
         __init__.py
         routes.py              # All API route handlers
      models/                    # Data models and schemas
         __init__.py
         schemas.py             # Pydantic models
      services/                  # Business logic layer
         __init__.py
         csv_service.py         # CSV data management
         file_handler.py        # File upload handling
         image_service.py       # Image processing
      __init__.py
      main.py                    # FastAPI application setup
   templates/                     # Frontend templates
      index.html                 # Main UI (Alpine.js + Tailwind)
   tests/                         # Test suite
      unit/                      # Unit tests
      integration/               # Integration tests
   uploads/                       # Image storage (created at runtime)
   static/                        # Static assets (if any)
   docs/                          # Documentation
   pyproject.toml                 # Project configuration
   README.md                      # This file
   CLAUDE.md                      # Project instructions
```

### Technology Stack

#### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, fast web framework
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: Data validation and serialization
- **[Pillow (PIL)](https://python-pillow.org/)**: Image processing and manipulation
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI server for production

#### Frontend
- **[Alpine.js](https://alpinejs.dev/)**: Lightweight reactive framework
- **[Tailwind CSS](https://tailwindcss.com/)**: Utility-first CSS framework
- **Vanilla JavaScript**: For core functionality

#### Development & Testing
- **[pytest](https://pytest.org/)**: Testing framework
- **[Black](https://black.readthedocs.io/)**: Code formatting
- **[Ruff](https://docs.astral.sh/ruff/)**: Fast Python linter
- **[mypy](https://mypy.readthedocs.io/)**: Static type checking

## =' API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main web interface |
| `GET` | `/health` | Health check |
| `POST` | `/api/upload` | Upload single image |
| `POST` | `/api/upload-multiple` | Upload multiple images |
| `POST` | `/api/annotate` | Save annotation |
| `GET` | `/api/annotations` | Get all annotations |
| `GET` | `/api/images` | Get image list |
| `GET` | `/api/images/{image_name}/annotations` | Get annotations for specific image |
| `GET` | `/api/statistics` | Get annotation statistics |
| `GET` | `/api/export` | Export CSV file |

### Data Models

#### AnnotationRequest
```python
{
    "image_name": "string",      # Required
    "description": "string",     # Required, min_length=1
    "tags": "string",           # Optional, comma-separated
    "labels": "string"          # Optional, comma-separated
}
```

#### ImageUploadResponse
```python
{
    "success": "boolean",
    "message": "string",
    "filename": "string",       # Optional
    "file_path": "string",      # Optional
    "thumbnail_path": "string"  # Optional
}
```

For detailed API documentation, see [docs/API.md](docs/API.md).

## >� Testing

The project maintains high test coverage (88%) with comprehensive test suites:

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_file_handler.py

# Run with verbose output
uv run pytest -v
```

### Test Coverage by Component
- **FileHandler**: 91% coverage (upload, validation, sanitization)
- **ImageService**: 94% coverage (thumbnails, metadata, validation)
- **CSVService**: 88% coverage (create, append, read, sanitize)
- **API Routes**: 78% coverage (all endpoints tested)

### Test Structure
```
tests/
   unit/                      # Unit tests for individual components
      test_file_handler.py  # File upload and validation tests
      test_image_service.py # Image processing tests
      test_csv_service.py   # CSV operations tests
      test_api_routes.py    # API endpoint tests
   integration/               # Integration tests (end-to-end)
```

For detailed testing documentation, see [docs/TESTING.md](docs/TESTING.md).

## =' Development

### Development Setup
```bash
# Clone and install
git clone <repository-url>
cd photo-annotation-tool
uv sync --dev

# Pre-commit setup (recommended)
uv run pre-commit install
```

### Code Quality Tools
```bash
# Format code
uv run black src tests

# Lint code
uv run ruff check src tests

# Type checking
uv run mypy src

# Run all quality checks
uv run black src tests && uv run ruff check src tests && uv run mypy src
```

### Development Server
```bash
# Start with auto-reload
uv run uvicorn src.photo_annotator.main:app --reload --port 8001

# Start with different host/port
uv run uvicorn src.photo_annotator.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
The application can be configured using environment variables:

```bash
# Optional configuration
export UPLOAD_DIR="custom_uploads"     # Default: "uploads"
export CSV_FILE="custom_annotations.csv" # Default: "annotations.csv"
export MAX_FILE_SIZE="52428800"        # Default: 10MB (in bytes)
```

For detailed development guide, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## =� Deployment

### Production Deployment

#### Using Docker (Recommended)
```bash
# Build image
docker build -t photo-annotation-tool .

# Run container
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads photo-annotation-tool
```

#### Manual Deployment
```bash
# Install production dependencies
uv sync --no-dev

# Start with production server
uv run uvicorn src.photo_annotator.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Environment Considerations
- **File Storage**: Ensure `uploads/` directory is persistent
- **CSV Data**: Ensure `annotations.csv` is backed up
- **Security**: Configure reverse proxy (nginx) for HTTPS
- **Performance**: Use multiple workers for production load

For detailed deployment guide, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## = Security Features

### File Security
- **Type Validation**: Whitelist approach for file extensions
- **Content Validation**: Actual image content verification (not just extension)
- **Size Limits**: Configurable maximum file size (10MB default)
- **Filename Sanitization**: Removes dangerous characters and paths

### Data Security
- **CSV Sanitization**: Prevents injection attacks in CSV fields
- **Input Validation**: Pydantic models for request validation
- **Path Traversal Protection**: Secure file path handling
- **CORS Configuration**: Configurable cross-origin policies

### Best Practices
- No sensitive data logging
- Secure temporary file handling
- Input sanitization at multiple layers
- Error handling without information disclosure

## =� Performance

### Optimizations
- **Image Thumbnails**: Automatic thumbnail generation for fast loading
- **Batch Processing**: Efficient multiple file uploads
- **Static File Serving**: Optimized static asset delivery
- **Database-free**: Lightweight CSV storage for simplicity

### Scalability Considerations
- **Horizontal Scaling**: Stateless design for load balancing
- **Storage**: File-based storage can be replaced with cloud storage
- **Database Migration**: Easy migration path to PostgreSQL/SQLite
- **Caching**: Can add Redis for session/image caching

## > Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Ensure all tests pass: `uv run pytest`
6. Run code quality checks: `uv run black . && uv run ruff check . && uv run mypy src`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Coding Standards
- Follow PEP 8 (enforced by Black)
- Add type hints for all functions
- Write docstrings for public APIs
- Maintain test coverage above 85%
- Update documentation for new features

## =� Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## = Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Ensure proper installation
uv sync --dev
# Or reinstall
pip install -e ".[dev]"
```

#### Upload failures
- Check file size (max 10MB)
- Verify file format (JPG, PNG, GIF, BMP, WEBP)
- Ensure uploads/ directory is writable

#### Port already in use
```bash
# Use different port
uvicorn src.photo_annotator.main:app --port 8002
```

#### Permission errors
```bash
# Fix directory permissions
chmod 755 uploads/
```

### Getting Help
- Check the [documentation](docs/)
- Review [GitHub Issues](https://github.com/yourusername/photo-annotation-tool/issues)
- Create a new issue with detailed information

## =� License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## =O Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for the robust web framework
- Styled with [Tailwind CSS](https://tailwindcss.com/) for beautiful UI
- Made interactive with [Alpine.js](https://alpinejs.dev/) for reactive components
- Developed following Test-Driven Development (TDD) principles

---

**Built with d using modern Python web technologies**

For more detailed documentation, explore the `docs/` directory:
- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Development Guide](docs/DEVELOPMENT.md)