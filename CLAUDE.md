# Photo Annotation Tool

A manual photo annotation tool built with Python, FastAPI, and test-driven development (TDD). This web application allows users to upload photos and add descriptions, tags, and labels that are saved to a CSV file for export.

## Features

- **Web Interface**: Upload single or multiple photos via drag-and-drop
- **Photo Grid**: View uploaded photos as thumbnails with visual annotation indicators
- **Annotation**: Click thumbnails to add descriptions, tags, and labels
- **Visual Indicators**: Green checkmarks show which photos have been annotated
- **Annotation Editing**: Click annotated photos to edit existing annotations
- **Image Management**: Delete images and their associated annotations
- **CSV Export**: Download annotations as CSV file at any time
- **Validation**: Client and server-side validation
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: HTML, Tailwind CSS, Alpine.js
- **Image Processing**: Pillow (PIL)
- **File Storage**: Local filesystem with CSV data persistence
- **Testing**: pytest with 88% coverage
- **Package Management**: uv

## Development Approach

This project was built following **Test-Driven Development (TDD)**:
1. Write failing tests first
2. Implement minimal code to make tests pass
3. Refactor while keeping tests green
4. Achieve 88% test coverage with 45 passing tests

## Directory Structure

```
photo-annotation-tool/
├── src/photo_annotator/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI route handlers
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── csv_service.py     # CSV data management
│   │   ├── file_handler.py    # File upload handling
│   │   └── image_service.py   # Image processing
│   ├── __init__.py
│   └── main.py                # FastAPI application
├── tests/
│   ├── unit/                  # Unit tests for all services
│   └── integration/           # Integration tests
├── templates/
│   └── index.html             # Frontend UI
├── static/                    # Static assets
├── uploads/                   # Image storage
├── pyproject.toml             # Project configuration
└── CLAUDE.md                  # This file
```

## Setup and Installation

1. **Clone and navigate to the project**:
   ```bash
   cd photo-annotation-tool
   ```

2. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

3. **Run tests** (recommended):
   ```bash
   uv run pytest -v
   ```

4. **Start the development server**:
   ```bash
   uv run uvicorn src.photo_annotator.main:app --reload --port 8001
   ```

5. **Open your browser** and navigate to `http://localhost:8001`

## Usage

### Uploading Photos
- Drag and drop image files onto the upload zone
- Or click "browse" to select files manually
- Supported formats: JPG, PNG, GIF, BMP, WEBP (max 10MB each)

### Annotating Photos
1. Click on any thumbnail in the photo grid
2. Add a description (required)
3. Add tags (comma-separated, optional)
4. Add labels (comma-separated, optional)
5. Click "Save Annotation"

**Visual Indicators:**
- Photos with annotations display a green checkmark in the top-left corner
- Clicking on an annotated photo will pre-populate the form with existing data
- You can edit existing annotations by clicking on annotated photos

### Deleting Images
1. Hover over any image thumbnail in the photo grid
2. Click the red delete button that appears in the top-right corner
3. Confirm deletion in the dialog box
4. The image file, thumbnail, and all associated annotations are permanently removed

### Exporting Data
- Click "Export CSV" to download all annotations
- CSV includes: image_name, description, tags, labels, timestamp

## API Endpoints

- `GET /` - Main web interface
- `GET /health` - Health check
- `POST /api/upload` - Upload single image
- `POST /api/upload-multiple` - Upload multiple images
- `POST /api/annotate` - Save annotation
- `GET /api/annotations` - Get all annotations
- `GET /api/images` - Get image list
- `DELETE /api/images/{image_name}` - Delete image and annotations
- `GET /api/statistics` - Get annotation statistics
- `GET /api/export` - Export CSV file

## Development Commands

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Code formatting
uv run black src tests

# Linting
uv run ruff check src tests

# Type checking
uv run mypy src

# Start development server
uv run uvicorn src.photo_annotator.main:app --reload --port 8001
```

## Test Coverage

- **Total**: 88% coverage with 45 passing tests
- **FileHandler**: 91% coverage (upload, validation, sanitization)
- **ImageService**: 94% coverage (thumbnails, metadata, validation)
- **CSVService**: 88% coverage (create, append, read, sanitize)
- **API Routes**: 78% coverage (all endpoints tested)

## Architecture

### Services Layer
- **FileHandler**: Handles file uploads, validation, and sanitization
- **ImageService**: Creates thumbnails and processes image metadata
- **CSVService**: Manages CSV data persistence and export

### API Layer
- **FastAPI**: RESTful API with automatic OpenAPI documentation
- **Pydantic**: Request/response validation and serialization

### Frontend
- **Alpine.js**: Reactive data binding and component state
- **Tailwind CSS**: Utility-first styling framework
- **Visual Indicators**: Green checkmarks for annotated photos
- **Form Auto-population**: Existing annotations automatically load when editing
- **Responsive Design**: Mobile-friendly interface

## Security Features

- File type validation (whitelist approach)
- File size limits (10MB maximum)
- Filename sanitization (removes dangerous characters)
- Image content verification (not just extension checking)
- CSV field sanitization (prevents injection attacks)

## Future Enhancements

- Database storage (PostgreSQL/SQLite)
- User authentication and authorization
- Batch annotation features
- Image annotation with bounding boxes
- Machine learning integration for auto-tagging
- RESTful API versioning
- Docker containerization

## Documentation

For comprehensive documentation, see the `docs/` directory:

- **[API.md](docs/API.md)** - Complete API reference with all endpoints, request/response schemas, and examples
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, design patterns, and technical decisions
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guides for various platforms (Docker, Cloud, etc.)
- **[TESTING.md](docs/TESTING.md)** - Testing strategy, TDD approach, and 88% coverage details
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Developer setup, coding standards, and contribution guidelines

## License

This project was built as a demonstration of test-driven development practices with modern Python web technologies.