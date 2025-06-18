# Development Guide

This guide provides comprehensive information for developers working on the Photo Annotation Tool, including setup, workflows, coding standards, and contribution guidelines.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Development Tools](#development-tools)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)
- [Feature Development](#feature-development)
- [Performance Guidelines](#performance-guidelines)
- [Security Guidelines](#security-guidelines)
- [Contributing](#contributing)

## Development Environment Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.11+**: Required for modern Python features
- **uv**: Fast Python package installer and resolver (recommended)
- **Git**: Version control
- **VS Code** or **PyCharm**: Recommended IDEs
- **Docker**: For containerized development (optional)

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd photo-annotation-tool

# Install dependencies using uv (recommended)
uv sync --dev

# Alternative: using pip
pip install -e ".[dev]"

# Verify installation
uv run pytest --version
uv run black --version
uv run ruff --version
```

### IDE Configuration

#### VS Code Setup

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Dev Server",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "src.photo_annotator.main:app",
                "--reload",
                "--port",
                "8001"
            ],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "tests/",
                "-v"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

#### PyCharm Setup

1. **Interpreter Setup**:
   - File → Settings → Project → Python Interpreter
   - Add → Existing environment → Select `.venv/bin/python`

2. **Code Style**:
   - File → Settings → Editor → Code Style → Python
   - Set line length to 88
   - Enable Black integration

3. **Testing**:
   - File → Settings → Tools → Python Integrated Tools
   - Set default test runner to pytest

### Environment Variables

Create `.env` file for development:

```bash
# .env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=debug
HOST=127.0.0.1
PORT=8001
UPLOAD_DIR=./uploads
CSV_FILE=./annotations.csv
MAX_FILE_SIZE=10485760
ALLOWED_ORIGINS=*
```

### Pre-commit Hooks

Set up pre-commit hooks for code quality:

```bash
# Install pre-commit
uv add --dev pre-commit

# Install git hooks
uv run pre-commit install

# Run on all files (optional)
uv run pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.261
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.1.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-pillow]

  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

## Project Structure

### Code Organization

```
src/photo_annotator/
├── __init__.py                 # Package initialization
├── main.py                     # FastAPI app setup and configuration
├── api/                        # HTTP API layer
│   ├── __init__.py
│   ├── routes.py              # Route handlers
│   └── dependencies.py        # Dependency injection (future)
├── models/                     # Data models and schemas
│   ├── __init__.py
│   └── schemas.py             # Pydantic models
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── file_handler.py        # File operations
│   ├── image_service.py       # Image processing
│   └── csv_service.py         # Data persistence
├── core/                       # Core utilities (future expansion)
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── exceptions.py          # Custom exceptions
└── utils/                      # Utility functions
    ├── __init__.py
    └── helpers.py             # Common utilities
```

### Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Services are injected rather than imported directly
3. **Layered Architecture**: Clear separation between API, business logic, and data layers
4. **Type Safety**: Comprehensive type hints throughout the codebase
5. **Testability**: All components are easily testable in isolation

### Module Dependencies

```
┌─────────────┐    ┌─────────────┐
│   main.py   │───►│ api/routes  │
└─────────────┘    └─────┬───────┘
                         │
                         ▼
                ┌─────────────┐    ┌─────────────┐
                │  services/  │───►│   models/   │
                └─────────────┘    └─────────────┘
```

## Development Workflow

### Daily Development

1. **Start Development Session**:
   ```bash
   # Activate environment
   source .venv/bin/activate  # or use uv automatically
   
   # Pull latest changes
   git pull origin main
   
   # Install any new dependencies
   uv sync --dev
   
   # Run tests to ensure everything works
   uv run pytest
   ```

2. **Feature Development**:
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature-name
   
   # Make changes following TDD
   # 1. Write failing test
   # 2. Make test pass
   # 3. Refactor
   
   # Run tests frequently
   uv run pytest tests/unit/test_new_feature.py
   ```

3. **Code Quality Checks**:
   ```bash
   # Format code
   uv run black src tests
   
   # Lint code
   uv run ruff check src tests
   
   # Type checking
   uv run mypy src
   
   # Run all tests with coverage
   uv run pytest --cov=src --cov-report=term-missing
   ```

### Git Workflow

We follow **Git Flow** with the following branches:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Feature development branches
- **hotfix/***: Emergency fixes for production
- **release/***: Release preparation branches

#### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

Examples:
```
feat(api): add batch image upload endpoint

- Implement POST /api/upload-multiple endpoint
- Add validation for multiple files
- Include progress tracking

Closes #123
```

```
fix(csv): prevent CSV injection in annotation fields

- Sanitize special characters in CSV fields
- Add tests for injection prevention
- Update security documentation

Fixes #456
```

### Branch Protection

Configure branch protection rules:

- **Require pull request reviews**: At least 1 reviewer
- **Require status checks**: All CI checks must pass
- **Require up-to-date branches**: Branch must be current with base
- **Include administrators**: Apply rules to admins too

## Coding Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

#### Formatting
- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings, single quotes for single characters
- **Imports**: Organized by isort/ruff

#### Naming Conventions
```python
# Variables and functions: snake_case
def upload_image_file():
    file_path = get_upload_path()

# Classes: PascalCase
class FileHandler:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024

# Private members: leading underscore
class ImageService:
    def _create_thumbnail_internal(self):
        pass
```

#### Type Hints

Use comprehensive type hints:

```python
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

def process_upload(
    file: UploadFile, 
    upload_dir: Path
) -> Dict[str, Union[bool, str, Optional[str]]]:
    """Process uploaded file with comprehensive type hints."""
    pass

# For complex return types, use TypedDict
from typing import TypedDict

class UploadResult(TypedDict):
    success: bool
    message: str
    filename: Optional[str]
    file_path: Optional[str]
```

#### Docstrings

Use Google-style docstrings:

```python
def upload_single_file(self, file: UploadFile) -> Dict[str, Any]:
    """Upload a single file to the server.
    
    Args:
        file: The uploaded file object from FastAPI.
        
    Returns:
        Dictionary containing upload result with keys:
        - success: Whether upload succeeded
        - filename: Sanitized filename if successful
        - file_path: Full path to uploaded file
        - error: Error message if unsuccessful
        
    Raises:
        ValueError: If file validation fails.
        IOError: If file cannot be saved.
        
    Example:
        >>> handler = FileHandler("/uploads")
        >>> result = handler.upload_single_file(uploaded_file)
        >>> if result["success"]:
        ...     print(f"Uploaded: {result['filename']}")
    """
    pass
```

### FastAPI Best Practices

#### Route Organization
```python
# Group related routes
@router.post("/upload", response_model=ImageUploadResponse)
@router.post("/upload-multiple")
async def upload_multiple_images():
    pass

@router.get("/images", response_model=ImageListResponse)
@router.get("/images/{image_name}/annotations")
async def get_image_annotations():
    pass
```

#### Error Handling
```python
from fastapi import HTTPException

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        result = file_handler.upload_single_file(file)
        if not result["success"]:
            raise HTTPException(
                status_code=400, 
                detail=result["error"]
            )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Dependency Injection
```python
# For future expansion
from fastapi import Depends

def get_file_handler() -> FileHandler:
    return FileHandler(settings.UPLOAD_DIR)

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    file_handler: FileHandler = Depends(get_file_handler)
):
    # Use injected dependency
    pass
```

### Testing Standards

#### Test Organization
```python
class TestFileHandler:
    """Test suite for FileHandler service."""
    
    @pytest.fixture
    def handler(self, temp_upload_dir):
        """Create FileHandler instance for testing."""
        return FileHandler(temp_upload_dir)
    
    def test_upload_valid_image_success(self, handler, sample_image):
        """Test successful upload of valid image file."""
        # Arrange
        mock_file = create_mock_file("test.jpg", sample_image)
        
        # Act
        result = handler.upload_single_file(mock_file)
        
        # Assert
        assert result["success"] is True
        assert result["filename"] == "test.jpg"
        assert Path(result["file_path"]).exists()
```

#### Test Data Management
```python
# Use factories for test data
@pytest.fixture
def sample_annotation():
    """Create sample annotation data."""
    return AnnotationFactory.create(
        image_name="test.jpg",
        description="Test description",
        tags="test, sample",
        labels="demo"
    )
```

## Development Tools

### Code Quality Tools

#### Black (Code Formatting)
```bash
# Format specific files
uv run black src/photo_annotator/main.py

# Format entire project
uv run black src tests

# Check formatting without changes
uv run black --check src tests
```

#### Ruff (Linting)
```bash
# Lint and show violations
uv run ruff check src tests

# Auto-fix violations
uv run ruff check --fix src tests

# Check specific rules
uv run ruff check --select E,W src
```

#### MyPy (Type Checking)
```bash
# Type check source code
uv run mypy src

# Type check with specific options
uv run mypy --strict src

# Generate type checking report
uv run mypy --html-report mypy-report src
```

### Development Scripts

Create development scripts in `scripts/` directory:

```bash
# scripts/dev.sh
#!/bin/bash
# Start development server with auto-reload
uv run uvicorn src.photo_annotator.main:app --reload --port 8001

# scripts/test.sh
#!/bin/bash
# Run comprehensive test suite
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# scripts/quality.sh
#!/bin/bash
# Run all quality checks
set -e
echo "Formatting code..."
uv run black src tests
echo "Linting..."
uv run ruff check src tests
echo "Type checking..."
uv run mypy src
echo "Testing..."
uv run pytest
echo "All checks passed!"
```

### Database Tools (Future)

When migrating from CSV to database:

```bash
# Alembic for migrations
uv add alembic

# Database inspection
uv add sqlalchemy[postgresql]
```

## Debugging and Troubleshooting

### Logging Configuration

Set up comprehensive logging:

```python
# src/photo_annotator/core/logging.py
import logging
import sys
from typing import Dict, Any

def setup_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", mode="a")
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

# Usage in main.py
from photo_annotator.core.logging import setup_logging

setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
```

### Debug Mode

Enable debug mode for development:

```python
# In main.py
import os

DEBUG = os.getenv("ENVIRONMENT") == "development"

app = FastAPI(
    debug=DEBUG,
    title="Photo Annotation Tool",
    description="Development mode" if DEBUG else "Production mode"
)

if DEBUG:
    # Add debug middleware
    @app.middleware("http")
    async def debug_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.debug(f"Request {request.url} took {process_time:.3f}s")
        return response
```

### Common Issues

#### Import Errors
```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Or use editable install
pip install -e .
```

#### Port Conflicts
```bash
# Find process using port
lsof -i :8001

# Kill process
kill -9 <PID>

# Use different port
uvicorn src.photo_annotator.main:app --port 8002
```

#### File Permission Issues
```bash
# Fix upload directory permissions
chmod 755 uploads/
chown $USER:$USER uploads/
```

#### File Upload Issues (RESOLVED in v1.0.1)

**Issue**: Empty files created during upload and `/uploads/undefined` 404 errors

**Root Causes**: 
1. `UploadFile.read()` returns a coroutine but was called synchronously
2. Frontend JavaScript accessing null thumbnail paths without proper null checks

**Symptoms**: 
- Files uploaded but with 0 bytes
- Browser console errors: `GET /uploads/undefined 404 Not Found`
- `Upload failed: a bytes-like object is required, not 'coroutine'` error

**Resolution Applied**:
```python
# 1. Made file upload methods async in file_handler.py
async def upload_single_file(self, file: UploadFile) -> Dict[str, Any]:
    try:
        # Reset file position and await async operations
        await file.seek(0)
        content = await file.read()
        # Save file content properly
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return {"success": False, "error": f"Upload failed: {str(e)}"}

# 2. Updated API routes to await async calls
@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    upload_result = await file_handler.upload_single_file(file)
    # ... rest of implementation
```

```html
<!-- 3. Added null checks in frontend template -->
<img x-show="image.thumbnail" 
     :src="`/uploads/thumbnails/${image.thumbnail ? image.thumbnail.split('/').pop() : ''}`" 
     :alt="image.filename" class="w-full h-full object-cover">
```

**Testing**: Upload functionality now works correctly with proper file content and no browser errors.

### Profiling

Profile application performance:

```python
# Add profiling middleware
import cProfile
import pstats
from io import StringIO

@app.middleware("http")
async def profile_middleware(request, call_next):
    if request.query_params.get("profile"):
        profiler = cProfile.Profile()
        profiler.enable()
        
        response = await call_next(request)
        
        profiler.disable()
        stats_stream = StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats("cumulative").print_stats(20)
        
        logger.info(f"Profile for {request.url}:\n{stats_stream.getvalue()}")
        return response
    
    return await call_next(request)
```

## Feature Development

### Adding New Features

Follow this process for new features:

1. **Design Phase**:
   - Write design document
   - Define API contracts
   - Plan database changes (if any)
   - Identify testing scenarios

2. **Implementation Phase**:
   - Write tests first (TDD)
   - Implement core logic
   - Add API endpoints
   - Update documentation

3. **Testing Phase**:
   - Unit tests for all components
   - Integration tests for workflows
   - Performance tests if needed
   - Security review

4. **Documentation Phase**:
   - Update API documentation
   - Add usage examples
   - Update deployment guides

### Example: Adding Image Metadata Extraction

```python
# 1. Define model (schemas.py)
class ImageMetadata(BaseModel):
    width: int
    height: int
    format: str
    size_bytes: int
    exif_data: Optional[Dict[str, Any]] = None

# 2. Add service method (image_service.py)
def extract_metadata(self, image_path: str) -> ImageMetadata:
    """Extract comprehensive image metadata."""
    with Image.open(image_path) as img:
        exif_data = None
        if hasattr(img, '_getexif'):
            exif_data = img._getexif()
        
        return ImageMetadata(
            width=img.width,
            height=img.height,
            format=img.format,
            size_bytes=os.path.getsize(image_path),
            exif_data=exif_data
        )

# 3. Add API endpoint (routes.py)
@router.get("/images/{image_name}/metadata", response_model=ImageMetadata)
async def get_image_metadata(image_name: str):
    """Get detailed image metadata."""
    image_path = UPLOAD_DIR / image_name
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    metadata = image_service.extract_metadata(str(image_path))
    return metadata

# 4. Add tests (test_image_service.py)
def test_extract_metadata_success(self, sample_image_path):
    """Test successful metadata extraction."""
    service = ImageService("/tmp")
    
    metadata = service.extract_metadata(sample_image_path)
    
    assert metadata.width > 0
    assert metadata.height > 0
    assert metadata.format in ["JPEG", "PNG", "GIF"]
    assert metadata.size_bytes > 0
```

## Performance Guidelines

### Code Performance

#### Efficient File Handling
```python
# Use context managers for file operations
def process_image_efficiently(image_path: str) -> Dict[str, Any]:
    """Process image with efficient resource management."""
    try:
        with Image.open(image_path) as img:
            # Process image while file is open
            thumbnail = img.copy()
            thumbnail.thumbnail((200, 200))
            
            # Extract metadata
            metadata = {
                "size": img.size,
                "format": img.format,
                "mode": img.mode
            }
            
        return {"success": True, "metadata": metadata}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

#### Async Operations
```python
# Use async for I/O operations
import asyncio
import aiofiles

async def save_file_async(file_content: bytes, file_path: str) -> bool:
    """Save file asynchronously."""
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        return True
    except Exception:
        return False

# Batch operations
async def process_multiple_images(image_paths: List[str]) -> List[Dict[str, Any]]:
    """Process multiple images concurrently."""
    tasks = [process_image_async(path) for path in image_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

#### Memory Management
```python
# Use generators for large datasets
def read_annotations_generator(csv_path: str) -> Iterator[Dict[str, str]]:
    """Read annotations as generator to save memory."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Process images in chunks
def process_images_in_chunks(image_paths: List[str], chunk_size: int = 10) -> None:
    """Process images in chunks to manage memory usage."""
    for i in range(0, len(image_paths), chunk_size):
        chunk = image_paths[i:i + chunk_size]
        process_image_chunk(chunk)
        # Force garbage collection between chunks
        gc.collect()
```

### Database Performance (Future)

When migrating to database:

```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Batch operations
def batch_insert_annotations(annotations: List[Dict[str, Any]]) -> None:
    """Insert annotations in batches for better performance."""
    with engine.begin() as conn:
        conn.execute(
            annotations_table.insert(),
            annotations
        )

# Use indexes for common queries
CREATE INDEX idx_annotations_image_name ON annotations(image_name);
CREATE INDEX idx_annotations_timestamp ON annotations(timestamp);
```

## Security Guidelines

### Input Validation

Always validate and sanitize inputs:

```python
def validate_filename(filename: str) -> bool:
    """Validate filename for security."""
    # Check for path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    
    # Check for null bytes
    if "\x00" in filename:
        return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True

def sanitize_csv_field(value: str) -> str:
    """Sanitize CSV field to prevent injection."""
    if not value:
        return ""
    
    # Remove CSV injection characters
    dangerous_chars = ["=", "+", "-", "@"]
    for char in dangerous_chars:
        if value.startswith(char):
            value = "'" + value  # Prefix with quote
    
    # Remove control characters
    value = re.sub(r'[\r\n\t]', ' ', value)
    
    return value.strip()
```

### Secure File Handling

```python
def secure_file_upload(file: UploadFile, upload_dir: str) -> Dict[str, Any]:
    """Secure file upload with comprehensive validation."""
    # Validate file type by content, not just extension
    file_header = file.read(16)
    file.seek(0)
    
    if not is_valid_image_header(file_header):
        return {"success": False, "error": "Invalid image file"}
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Use secure path joining
    file_path = Path(upload_dir) / safe_filename
    
    # Ensure path is within upload directory
    if not str(file_path.resolve()).startswith(str(Path(upload_dir).resolve())):
        return {"success": False, "error": "Invalid file path"}
    
    # Save with limited permissions
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    os.chmod(file_path, 0o644)  # Read-only for others
    
    return {"success": True, "file_path": str(file_path)}
```

### Environment Security

```python
# Secure configuration loading
import os
from typing import Optional

class SecureConfig:
    """Secure configuration management."""
    
    @staticmethod
    def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment with validation."""
        value = os.getenv(key, default)
        
        if value and key.endswith("_SECRET"):
            # Validate secret format
            if len(value) < 32:
                raise ValueError(f"Secret {key} too short")
        
        return value
    
    @staticmethod
    def get_allowed_origins() -> List[str]:
        """Get CORS allowed origins securely."""
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        
        if origins == "*":
            # Warn about permissive CORS in production
            if os.getenv("ENVIRONMENT") == "production":
                logging.warning("Using permissive CORS in production")
        
        return origins.split(",")
```

## Contributing

### Contribution Process

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `develop`
3. **Make your changes** following coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with detailed description

### Pull Request Guidelines

#### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated existing tests as needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

#### Review Checklist

Reviewers should check:

- [ ] **Functionality**: Does the code work as intended?
- [ ] **Tests**: Are there adequate tests with good coverage?
- [ ] **Style**: Does code follow project standards?
- [ ] **Security**: Are there any security concerns?
- [ ] **Performance**: Are there performance implications?
- [ ] **Documentation**: Is documentation updated?

### Code Review Standards

#### What to Look For

**Functionality**:
- Code solves the stated problem
- Edge cases are handled
- Error conditions are managed appropriately

**Design**:
- Code follows established patterns
- Appropriate abstraction levels
- Good separation of concerns

**Testing**:
- Comprehensive test coverage
- Tests are readable and maintainable
- Both positive and negative cases tested

**Security**:
- Input validation present
- No hardcoded secrets
- Secure file handling

#### Providing Feedback

Use constructive feedback:

```
# Good feedback
"Consider using a context manager here to ensure file cleanup"

# Better feedback with suggestion
"Consider using a context manager here to ensure file cleanup:
```python
with open(file_path, 'rb') as f:
    return f.read()
```

# Best feedback with reasoning
"Consider using a context manager here to ensure file cleanup and proper resource management, especially important for image processing where files might be large:
```python
with open(file_path, 'rb') as f:
    return f.read()
```
This also makes the code more readable and follows Python best practices."
```

### Issue Reporting

When reporting bugs or requesting features:

#### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.11.0]
- Browser: [e.g. Chrome 90.0]

**Additional context**
Any other context about the problem.
```

#### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions you've considered.

**Additional context**
Any other context about the feature request.
```

This comprehensive development guide ensures that all contributors can effectively work on the Photo Annotation Tool while maintaining high code quality, security, and performance standards.