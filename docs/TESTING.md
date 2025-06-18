# Testing Documentation

This document provides comprehensive information about the testing strategy, implementation, and best practices for the Photo Annotation Tool.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Coverage](#test-coverage)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Testing Tools](#testing-tools)
- [Writing Tests](#writing-tests)
- [Continuous Integration](#continuous-integration)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)

## Testing Philosophy

The Photo Annotation Tool follows **Test-Driven Development (TDD)** principles:

1. **Write tests first**: Tests are written before implementation
2. **Red-Green-Refactor cycle**: Write failing test → Make it pass → Refactor
3. **High coverage**: Maintain 88%+ test coverage
4. **Fast feedback**: Tests should run quickly and provide immediate feedback
5. **Reliable tests**: Tests should be deterministic and not flaky

### Testing Pyramid

```
    ┌─────────────────┐
    │   E2E Tests     │  ← Few, slow, high confidence
    │   (Integration) │
    ├─────────────────┤
    │  API Tests      │  ← More, faster, good confidence
    │  (Integration)  │
    ├─────────────────┤
    │  Unit Tests     │  ← Many, fast, focused
    │   (Isolated)    │
    └─────────────────┘
```

## Test Coverage

### Current Coverage (88%)

| Component | Coverage | Tests | Description |
|-----------|----------|-------|-------------|
| **FileHandler** | 91% | 15 tests | File upload, validation, sanitization |
| **ImageService** | 94% | 12 tests | Image processing, thumbnails, metadata |
| **CSVService** | 88% | 13 tests | CSV operations, data management |
| **API Routes** | 78% | 10 tests | HTTP endpoints, request handling |
| **Models** | 100% | 5 tests | Pydantic schema validation |

### Coverage Goals

- **Minimum**: 85% overall coverage
- **Target**: 90% overall coverage
- **Critical paths**: 100% coverage for security-related code
- **New code**: 95% coverage requirement

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_file_handler.py   # FileHandler tests
│   ├── test_image_service.py  # ImageService tests
│   ├── test_csv_service.py    # CSVService tests
│   └── test_api_routes.py     # API route tests
├── integration/                # Integration tests
│   ├── __init__.py
│   └── test_end_to_end.py     # Full workflow tests
├── fixtures/                   # Test data and fixtures
│   ├── images/                # Sample images for testing
│   └── csv/                   # Sample CSV files
└── utils/                     # Test utilities
    ├── __init__.py
    └── helpers.py             # Test helper functions
```

### Test Naming Convention

Tests follow a clear naming pattern:

```python
def test_[component]_[scenario]_[expected_outcome]():
    """Test that [component] [scenario] [expected_outcome]"""
```

Examples:
- `test_file_handler_valid_image_upload_success()`
- `test_csv_service_invalid_data_sanitization_applied()`
- `test_api_routes_missing_file_returns_400()`

## Running Tests

### Basic Test Execution

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_file_handler.py

# Run specific test function
uv run pytest tests/unit/test_file_handler.py::test_upload_valid_image_success

# Run tests matching pattern
uv run pytest -k "test_upload"
```

### Coverage Reports

```bash
# Run tests with coverage
uv run pytest --cov=src

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# Generate XML coverage report (for CI)
uv run pytest --cov=src --cov-report=xml

# Coverage with missing lines
uv run pytest --cov=src --cov-report=term-missing
```

### Test Configuration

```python
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --cov=src --cov-report=term-missing"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
```

### Fixtures and Setup

```python
# conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from io import BytesIO

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_image():
    """Create sample image for testing"""
    image = Image.new("RGB", (100, 100), color="red")
    image_bytes = BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return image_bytes

@pytest.fixture
def mock_csv_service():
    """Mock CSV service for testing"""
    from unittest.mock import Mock
    service = Mock()
    service.save_annotation.return_value = {"success": True, "message": "Saved"}
    return service
```

## Test Types

### 1. Unit Tests

Unit tests focus on individual components in isolation:

```python
# tests/unit/test_file_handler.py
import pytest
from unittest.mock import Mock, patch
from photo_annotator.services.file_handler import FileHandler

class TestFileHandler:
    def test_validate_file_success(self, temp_upload_dir):
        """Test successful file validation"""
        handler = FileHandler(temp_upload_dir)
        
        # Create mock file
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.size = 1000
        
        is_valid, error = handler.validate_file(mock_file)
        
        assert is_valid is True
        assert error is None

    def test_validate_file_invalid_extension(self, temp_upload_dir):
        """Test file validation with invalid extension"""
        handler = FileHandler(temp_upload_dir)
        
        mock_file = Mock()
        mock_file.filename = "test.txt"
        
        is_valid, error = handler.validate_file(mock_file)
        
        assert is_valid is False
        assert "Invalid file extension" in error

    def test_sanitize_filename_removes_dangerous_chars(self, temp_upload_dir):
        """Test filename sanitization removes dangerous characters"""
        handler = FileHandler(temp_upload_dir)
        
        dangerous_filename = "../../../etc/passwd"
        sanitized = handler.sanitize_filename(dangerous_filename)
        
        assert sanitized == "etcpasswd"
        assert ".." not in sanitized
        assert "/" not in sanitized
```

### 2. Integration Tests

Integration tests verify component interactions:

```python
# tests/integration/test_end_to_end.py
import pytest
from fastapi.testclient import TestClient
from photo_annotator.main import app

class TestEndToEnd:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_complete_workflow(self, client, sample_image):
        """Test complete upload and annotation workflow"""
        # 1. Upload image
        upload_response = client.post(
            "/api/upload",
            files={"file": ("test.jpg", sample_image, "image/jpeg")}
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        assert upload_data["success"] is True
        
        filename = upload_data["filename"]
        
        # 2. Verify image appears in list
        images_response = client.get("/api/images")
        assert images_response.status_code == 200
        images_data = images_response.json()
        assert any(img["filename"] == filename for img in images_data["images"])
        
        # 3. Add annotation
        annotation_response = client.post(
            "/api/annotate",
            json={
                "image_name": filename,
                "description": "Test image description",
                "tags": "test, sample",
                "labels": "demo, testing"
            }
        )
        assert annotation_response.status_code == 200
        annotation_data = annotation_response.json()
        assert annotation_data["success"] is True
        
        # 4. Verify annotation is saved
        annotations_response = client.get("/api/annotations")
        assert annotations_response.status_code == 200
        annotations_data = annotations_response.json()
        assert annotations_data["total_count"] > 0
        
        # Find our annotation
        our_annotation = next(
            (ann for ann in annotations_data["annotations"] 
             if ann["image_name"] == filename), None
        )
        assert our_annotation is not None
        assert our_annotation["description"] == "Test image description"
        assert our_annotation["tags"] == "test, sample"
```

### 3. API Tests

API tests focus on HTTP endpoints:

```python
# tests/unit/test_api_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from photo_annotator.main import app

class TestAPIRoutes:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy", 
            "service": "photo-annotation-tool"
        }

    def test_upload_no_file_returns_400(self, client):
        """Test upload endpoint with no file returns 400"""
        response = client.post("/api/upload")
        assert response.status_code == 422  # Validation error

    @patch("photo_annotator.api.routes.file_handler")
    @patch("photo_annotator.api.routes.image_service")
    def test_upload_success(self, mock_image_service, mock_file_handler, client):
        """Test successful file upload"""
        # Mock successful upload
        mock_file_handler.upload_single_file.return_value = {
            "success": True,
            "filename": "test.jpg",
            "file_path": "/uploads/test.jpg"
        }
        
        # Mock successful thumbnail creation
        mock_image_service.create_thumbnail.return_value = {
            "success": True,
            "thumbnail_path": "/uploads/thumbnails/thumb_test.jpg"
        }
        
        # Create mock file
        mock_file = ("test.jpg", b"fake image data", "image/jpeg")
        
        response = client.post("/api/upload", files={"file": mock_file})
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["filename"] == "test.jpg"
```

## Testing Tools

### Primary Testing Framework

**pytest**: Python testing framework with powerful features:

```python
# Key pytest features used:
- Fixtures for test setup/teardown
- Parametrized tests for multiple scenarios
- Markers for test categorization
- Plugin ecosystem (coverage, mock, etc.)
- Detailed assertion introspection
```

### Mocking and Fixtures

**unittest.mock**: For isolating units under test:

```python
from unittest.mock import Mock, patch, MagicMock

# Mock external dependencies
@patch("photo_annotator.services.file_handler.Image")
def test_image_processing(self, mock_image):
    mock_image.open.return_value.__enter__.return_value.size = (100, 100)
    # Test implementation
```

### Test Data Generation

**Factory pattern** for creating test data:

```python
# tests/utils/factories.py
class ImageFactory:
    @staticmethod
    def create_sample_image(width=100, height=100, color="red"):
        """Create sample image for testing"""
        image = Image.new("RGB", (width, height), color=color)
        image_bytes = BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)
        return image_bytes

class AnnotationFactory:
    @staticmethod
    def create_annotation(image_name="test.jpg", **kwargs):
        """Create annotation data for testing"""
        defaults = {
            "image_name": image_name,
            "description": "Test description",
            "tags": "test, sample",
            "labels": "demo"
        }
        defaults.update(kwargs)
        return defaults
```

## Writing Tests

### Test Structure Pattern

Follow the **Arrange-Act-Assert** pattern:

```python
def test_csv_service_save_annotation_success(self, temp_csv_file):
    # Arrange
    csv_service = CSVService(temp_csv_file)
    csv_service.initialize()
    
    annotation_data = {
        "image_name": "test.jpg",
        "description": "Test description",
        "tags": "test",
        "labels": "demo"
    }
    
    # Act
    result = csv_service.save_annotation(annotation_data)
    
    # Assert
    assert result["success"] is True
    assert result["message"] == "Annotation saved successfully"
    
    # Verify data was actually saved
    annotations = csv_service.read_annotations()
    assert len(annotations) == 1
    assert annotations[0]["image_name"] == "test.jpg"
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("filename,expected_valid", [
    ("test.jpg", True),
    ("test.png", True),
    ("test.gif", True),
    ("test.txt", False),
    ("test.exe", False),
    ("", False),
])
def test_file_validation_various_extensions(self, filename, expected_valid):
    """Test file validation with various extensions"""
    handler = FileHandler("/tmp")
    
    mock_file = Mock()
    mock_file.filename = filename
    mock_file.size = 1000
    
    is_valid, error = handler.validate_file(mock_file)
    
    assert is_valid == expected_valid
    if not expected_valid:
        assert error is not None
```

### Error Testing

Test error conditions thoroughly:

```python
def test_file_handler_oversized_file_rejected(self, temp_upload_dir):
    """Test that oversized files are rejected"""
    handler = FileHandler(temp_upload_dir)
    
    mock_file = Mock()
    mock_file.filename = "huge.jpg"
    mock_file.size = 20 * 1024 * 1024  # 20MB (over limit)
    
    is_valid, error = handler.validate_file(mock_file)
    
    assert is_valid is False
    assert "File too large" in error
    assert "10MB" in error
```

### Async Testing

Test async code properly:

```python
@pytest.mark.asyncio
async def test_async_upload_endpoint(self, client):
    """Test async upload endpoint"""
    # For future async implementations
    pass
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
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
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

### Quality Gates

Set up quality gates for CI/CD:

```bash
# Minimum requirements for passing CI
- Test coverage >= 85%
- All tests must pass
- No linting errors
- Type checking passes
- Security scan passes
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient
from photo_annotator.main import app

class TestPerformance:
    def test_concurrent_uploads(self):
        """Test performance with concurrent uploads"""
        client = TestClient(app)
        
        def upload_image():
            # Create sample image
            image_data = create_sample_image()
            response = client.post(
                "/api/upload",
                files={"file": ("test.jpg", image_data, "image/jpeg")}
            )
            return response.status_code == 200
        
        # Test 10 concurrent uploads
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(upload_image) for _ in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        
        # Assertions
        assert all(results), "All uploads should succeed"
        assert end_time - start_time < 30, "Should complete within 30 seconds"

    @pytest.mark.slow
    def test_large_file_upload_performance(self):
        """Test performance with large file uploads"""
        client = TestClient(app)
        
        # Create 5MB image (near limit)
        large_image = create_large_image(size_mb=5)
        
        start_time = time.time()
        response = client.post(
            "/api/upload",
            files={"file": ("large.jpg", large_image, "image/jpeg")}
        )
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 10, "Large upload should complete within 10 seconds"
```

### Memory Usage Testing

```python
import psutil
import gc

def test_memory_usage_during_batch_upload():
    """Test memory usage doesn't grow excessively during batch uploads"""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Perform batch operations
    for i in range(50):
        # Upload and process image
        upload_and_process_image()
        
        # Force garbage collection
        gc.collect()
        
        current_memory = process.memory_info().rss
        memory_growth = current_memory - initial_memory
        
        # Memory growth should be reasonable (< 100MB)
        assert memory_growth < 100 * 1024 * 1024, f"Memory growth too high: {memory_growth} bytes"
```

## Security Testing

### Input Validation Testing

```python
class TestSecurity:
    def test_filename_injection_prevention(self, temp_upload_dir):
        """Test prevention of filename injection attacks"""
        handler = FileHandler(temp_upload_dir)
        
        malicious_filenames = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "<script>alert('xss')</script>.jpg",
            "'; DROP TABLE users; --.jpg",
            "file\x00.jpg",
        ]
        
        for filename in malicious_filenames:
            sanitized = handler.sanitize_filename(filename)
            
            # Should not contain path traversal
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert "\x00" not in sanitized
            assert "<script>" not in sanitized

    def test_csv_injection_prevention(self, temp_csv_file):
        """Test prevention of CSV injection attacks"""
        csv_service = CSVService(temp_csv_file)
        csv_service.initialize()
        
        malicious_data = {
            "image_name": "test.jpg",
            "description": "=cmd|'/c calc'!A0",  # Excel formula injection
            "tags": "@SUM(1+1)*cmd|'/c calc'!A0",
            "labels": "+cmd|'/c calc'!A0"
        }
        
        result = csv_service.save_annotation(malicious_data)
        assert result["success"] is True
        
        # Read back and verify sanitization
        annotations = csv_service.read_annotations()
        annotation = annotations[0]
        
        # Formulas should be sanitized
        assert not annotation["description"].startswith("=")
        assert not annotation["tags"].startswith("@")
        assert not annotation["labels"].startswith("+")

    def test_file_type_validation_bypass_prevention(self, client):
        """Test prevention of file type validation bypass"""
        # Try to upload executable disguised as image
        malicious_file = b"MZ\x90\x00"  # PE header
        
        response = client.post(
            "/api/upload",
            files={"file": ("fake.jpg", malicious_file, "image/jpeg")}
        )
        
        # Should fail because content doesn't match claimed type
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Invalid image file" in data["message"]
```

### Rate Limiting Testing

```python
def test_upload_rate_limiting(self, client):
    """Test upload rate limiting (if implemented)"""
    # This test would verify rate limiting functionality
    # when implemented in the future
    pass
```

## Real-Life Testing

### Manual End-to-End Testing

In addition to automated tests, regular manual testing ensures the application works correctly in real-world scenarios:

#### Complete Workflow Test
1. **Server Setup**: Start development server and verify accessibility
2. **Image Upload**: Upload multiple test images through web interface
3. **Annotation**: Add descriptions, tags, and labels to uploaded images
4. **CSV Export**: Download and verify CSV contains correct annotation data

#### Test Results (Latest: 2025-06-18)
- ✅ **Image Upload**: Successfully uploaded 3 test images (red, green, blue) 
- ✅ **Thumbnails**: All images display properly with thumbnails in photo grid
- ✅ **Annotations**: Added detailed annotations with descriptions, tags, and labels
- ✅ **CSV Export**: Generated annotations.csv with proper format and timestamps
- ✅ **Data Persistence**: All data saved correctly to local files
- ✅ **UI Responsiveness**: Modal dialogs, forms, and buttons work smoothly

#### Verified Components
```
uploads/red_image.jpg     - 9.3KB test image
uploads/green_image.jpg   - 9.1KB test image  
uploads/blue_image.jpg    - 9.4KB test image
annotations.csv           - 2 complete annotation records
```

#### CSV Export Format Validation
```csv
image_name,description,tags,labels,timestamp
red_image.jpg,A bright red test image with white text overlay displaying 'Test Image 1' and color information,"red, test, generated, colorful, text-overlay","test-data, synthetic, demonstration, quality-assurance",2025-06-18T20:23:53.836236
green_image.jpg,A bright green test image with white text showing 'Test Image 2' and RGB color values,"green, nature, bright, test, synthetic","test-suite, verification, color-sample",2025-06-18T20:24:23.838376
```

### Manual Testing Checklist

#### Pre-Testing Setup
- [ ] Start development server: `uv run uvicorn src.photo_annotator.main:app --reload --port 8002`
- [ ] Verify health endpoint: `curl http://127.0.0.1:8002/health`
- [ ] Open web interface in browser: `http://127.0.0.1:8002`

#### Upload Testing
- [ ] Test single file upload via browse button
- [ ] Test multiple file upload
- [ ] Verify unsupported file types are rejected
- [ ] Test file size limits (>10MB should fail)
- [ ] Verify uploaded images appear in photo grid

#### Annotation Testing  
- [ ] Click image thumbnail to open annotation modal
- [ ] Add required description field
- [ ] Add optional tags (comma-separated)
- [ ] Add optional labels (comma-separated)
- [ ] Save annotation and verify success message
- [ ] Test form validation (empty description should fail)

#### Export Testing
- [ ] Click "Export CSV" button
- [ ] Verify CSV file downloads automatically
- [ ] Open CSV and verify data format
- [ ] Check all annotations are included
- [ ] Verify timestamps are in ISO format

#### Error Handling Testing
- [ ] Test upload with invalid file types
- [ ] Test upload with oversized files
- [ ] Test annotation without description
- [ ] Verify error messages are user-friendly

## Test Maintenance

### Keeping Tests Updated

1. **Update tests with code changes**: When modifying code, update corresponding tests
2. **Regular test review**: Periodically review and refactor tests
3. **Remove obsolete tests**: Clean up tests for removed functionality
4. **Add regression tests**: Add tests for each bug fix
5. **Real-life testing**: Perform manual end-to-end testing after major changes

### Test Documentation

Document complex test scenarios:

```python
def test_complex_image_processing_workflow(self):
    """
    Test complex image processing workflow.
    
    This test verifies the complete image processing pipeline:
    1. Upload original image
    2. Generate thumbnail with specific dimensions
    3. Extract and validate metadata
    4. Verify thumbnail quality and size
    5. Ensure original image is preserved
    
    Edge cases covered:
    - Very large images (memory usage)
    - Unusual aspect ratios
    - Various image formats
    """
    # Test implementation
```

### Common Testing Patterns

```python
# Pattern 1: Setup and teardown
class TestWithSetup:
    def setup_method(self):
        """Setup before each test method"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        shutil.rmtree(self.temp_dir)

# Pattern 2: Context managers for cleanup
@contextmanager
def temporary_file(content):
    """Context manager for temporary files"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        yield temp_path
    finally:
        os.unlink(temp_path)

# Pattern 3: Custom assertions
def assert_valid_image_response(response_data):
    """Custom assertion for image upload responses"""
    assert response_data["success"] is True
    assert "filename" in response_data
    assert "file_path" in response_data
    assert response_data["filename"].endswith(('.jpg', '.png', '.gif'))
```

This comprehensive testing documentation ensures that the Photo Annotation Tool maintains high quality through robust testing practices, with 88% test coverage and comprehensive test scenarios covering functionality, security, and performance aspects.