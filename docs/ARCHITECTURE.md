# Architecture Documentation

This document provides a comprehensive overview of the Photo Annotation Tool architecture, design patterns, and technical decisions.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [File Structure](#file-structure)
- [Design Decisions](#design-decisions)
- [Security Architecture](#security-architecture)
- [Performance Considerations](#performance-considerations)
- [Scalability](#scalability)

## System Overview

The Photo Annotation Tool is a web-based application that follows a modern, layered architecture pattern. It's built with Python and FastAPI for the backend, with a lightweight frontend using Alpine.js and Tailwind CSS.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Storage       │
│                 │    │                 │    │                 │
│ Alpine.js       │◄──►│ FastAPI         │◄──►│ File System     │
│ Tailwind CSS    │    │ Python 3.11+    │    │ CSV Files       │
│ HTML5           │    │ Pydantic        │    │ Image Files     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Backend Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and serialization using Python type hints
- **Pillow (PIL)**: Python Imaging Library for image processing
- **Uvicorn**: Lightning-fast ASGI server implementation

#### Frontend Stack
- **Alpine.js**: Minimal framework for composing JavaScript behavior in HTML
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **HTML5**: Modern web standards with semantic markup

#### Development Stack
- **pytest**: Testing framework with extensive plugin ecosystem
- **Black**: Uncompromising code formatter
- **Ruff**: Extremely fast Python linter
- **mypy**: Static type checker for Python

## Architecture Patterns

### 1. Layered Architecture

The application follows a clean layered architecture pattern:

```
┌─────────────────────────────────────────┐
│             Presentation Layer          │
│  (FastAPI Routes + HTML Templates)      │
├─────────────────────────────────────────┤
│             Business Logic Layer        │
│           (Service Classes)             │
├─────────────────────────────────────────┤
│             Data Access Layer           │
│        (File System Operations)         │
└─────────────────────────────────────────┘
```

### 2. Service Layer Pattern

Business logic is encapsulated in dedicated service classes:

- **FileHandler**: Manages file upload, validation, and sanitization
- **ImageService**: Handles image processing and thumbnail generation
- **CSVService**: Manages CSV data operations and export functionality

### 3. Dependency Injection

Services are instantiated and injected at the application level, promoting loose coupling and testability.

### 4. Repository Pattern (Simplified)

The CSVService acts as a simplified repository for data persistence, abstracting the underlying storage mechanism.

## Component Architecture

### Backend Components

#### 1. FastAPI Application (`main.py`)

```python
# Application setup and configuration
app = FastAPI(
    title="Photo Annotation Tool",
    description="A web application for manual photo annotation with CSV export",
    version="1.0.0"
)

# Middleware configuration
app.add_middleware(CORSMiddleware, ...)

# Service initialization
csv_service = CSVService("annotations.csv")
file_handler = FileHandler("uploads")
image_service = ImageService("uploads")
```

**Responsibilities:**
- Application configuration and setup
- Middleware configuration (CORS, etc.)
- Service instantiation and dependency injection
- Static file serving configuration
- Route registration

#### 2. API Routes (`api/routes.py`)

```python
router = APIRouter()

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    # Async route implementation with proper file handling
    upload_result = await file_handler.upload_single_file(file)
    # ... rest of implementation
```

**Responsibilities:**
- HTTP request handling
- Request validation using Pydantic models
- Async service orchestration
- Response formatting
- Error handling and HTTP status codes
- Proper async/await handling for file operations

#### 3. Data Models (`models/schemas.py`)

```python
class AnnotationRequest(BaseModel):
    image_name: str = Field(..., description="Name of the image file")
    description: str = Field(..., min_length=1, description="Description of the image")
    tags: str = Field(default="", description="Comma-separated tags")
    labels: str = Field(default="", description="Comma-separated labels")
```

**Responsibilities:**
- Data validation and serialization
- API contract definition
- Type safety and documentation
- Request/response schema definitions

#### 4. Service Layer

##### FileHandler Service (`services/file_handler.py`)

```python
class FileHandler:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    async def upload_single_file(self, file) -> Dict[str, Any]:
        # Async implementation for proper FastAPI UploadFile handling
        await file.seek(0)
        content = await file.read()
        # ... rest of implementation
```

**Responsibilities:**
- Async file upload processing
- File upload validation
- File type and size checking
- Filename sanitization
- Duplicate filename handling
- File system operations
- Proper handling of FastAPI UploadFile objects

##### ImageService (`services/image_service.py`)

```python
class ImageService:
    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (200, 200)) -> Dict[str, Any]:
        # Implementation
    
    def get_image_metadata(self, image_path: str) -> Dict[str, Any]:
        # Implementation
```

**Responsibilities:**
- Thumbnail generation
- Image metadata extraction
- Image validation and processing
- Batch processing operations
- Image format optimization

##### CSVService (`services/csv_service.py`)

```python
class CSVService:
    FIELDNAMES = ["image_name", "description", "tags", "labels", "timestamp"]
    
    def save_annotation(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
        
    def read_annotations(self) -> List[Dict[str, Any]]:
        # Implementation
```

**Responsibilities:**
- CSV file operations (read/write/delete)
- Data sanitization and validation
- Statistics generation
- Export functionality
- Data persistence management
- Annotation cleanup and removal

### Frontend Components

#### 1. Main Template (`templates/index.html`)

The frontend is built as a Single Page Application (SPA) using Alpine.js:

```html
<div x-data="photoApp()" class="min-h-screen">
    <!-- Application content -->
</div>

<script>
function photoApp() {
    return {
        // Application state and methods
    };
}
</script>
```

**Responsibilities:**
- User interface rendering
- Client-side state management
- API communication
- File upload handling
- User interaction management
- Visual annotation indicators (green checkmarks)
- Dynamic form population for editing existing annotations
- Real-time UI updates after data changes

## Data Flow

### Image Upload Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │   FastAPI   │    │ FileHandler │    │ ImageService│
│             │    │   Routes    │    │             │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │ POST /api/upload │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ validate_file()  │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ upload_file()    │
       │                  │                  ├─────────────────►│
       │                  │                  │                  │ create_thumbnail()
       │                  │                  │                  ├──────────────────┐
       │                  │                  │                  │                  │
       │                  │ Response         │                  │◄─────────────────┘
       │◄─────────────────┤                  │                  │
       │                  │                  │                  │
```

### Annotation Save Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │   FastAPI   │    │ CSVService  │
│             │    │   Routes    │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       │POST /api/annotate│                  │
       ├─────────────────►│                  │
       │                  │ validate_data()  │
       │                  ├──────────────────┤
       │                  │                  │ save_annotation()
       │                  │                  ├─────────────────►│
       │                  │                  │                  │ sanitize_data()
       │                  │                  │                  ├────────────────┐
       │                  │                  │                  │                │
       │                  │                  │                  │ write_to_csv() │
       │                  │                  │                  ├────────────────┤
       │                  │ Response         │                  │                │
       │◄─────────────────┤◄─────────────────┤◄────────────────┘
       │                  │                  │
```

### Image Delete Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browser   │    │   FastAPI   │    │ File System │    │ CSVService  │
│             │    │   Routes    │    │             │    │             │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
       │DELETE /api/images│                  │                  │
       ├─────────────────►│                  │                  │
       │                  │ delete_image()   │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │ unlink_files()   │
       │                  │                  ├─────────────────┐│
       │                  │                  │                 ││
       │                  │                  │◄────────────────┘│
       │                  │ delete_annotations()                │
       │                  ├─────────────────────────────────────►│
       │                  │                  │                  │ filter_csv()
       │                  │                  │                  ├─────────────────┐
       │                  │                  │                  │                 │
       │                  │                  │                  │ rewrite_csv()   │
       │                  │                  │                  ├─────────────────┤
       │                  │ Response         │                  │                 │
       │◄─────────────────┤◄─────────────────────────────────────┤◄────────────────┘
       │                  │                  │                  │
```

## File Structure

### Directory Organization

```
photo-annotation-tool/
├── src/photo_annotator/           # Main application package
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # FastAPI application setup
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── routes.py             # HTTP route handlers
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic models
│   └── services/                 # Business logic layer
│       ├── __init__.py
│       ├── file_handler.py       # File operations
│       ├── image_service.py      # Image processing
│       └── csv_service.py        # Data persistence
├── templates/                    # Frontend templates
│   └── index.html               # Main SPA template
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/             # Integration tests
├── uploads/                     # File storage (runtime)
│   └── thumbnails/              # Generated thumbnails
├── static/                      # Static assets
└── docs/                        # Documentation
```

### Package Organization Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Layered Structure**: Clear separation between API, business logic, and data layers
3. **Testability**: Structure supports easy unit testing and mocking
4. **Scalability**: Modular design allows for easy extension and modification

## Design Decisions

### 1. CSV vs Database

**Decision**: Use CSV files for data persistence
**Rationale**:
- Simplicity: No database setup or management required
- Portability: Easy to export, import, and manipulate data
- Lightweight: Minimal dependencies and infrastructure
- Suitable for small to medium datasets
- Easy to migrate to database later if needed

**Trade-offs**:
- Limited query capabilities
- No ACID transactions
- Performance limitations with large datasets
- No relational data support

### 2. File System Storage vs Cloud Storage

**Decision**: Use local file system for image storage
**Rationale**:
- Simplicity: No external service dependencies
- Development efficiency: Easy local development and testing
- Cost: No cloud storage costs
- Performance: Direct file access

**Trade-offs**:
- Scalability limitations
- No automatic backup/redundancy
- Server storage constraints
- Migration path available to cloud storage

### 3. Alpine.js vs React/Vue

**Decision**: Use Alpine.js for frontend
**Rationale**:
- Minimal complexity: No build process required
- Fast development: Direct HTML enhancement
- Small bundle size: Lightweight framework
- Suitable for simple SPAs
- Easy to understand and maintain

**Trade-offs**:
- Limited ecosystem compared to React/Vue
- Less suitable for complex state management
- Fewer community resources

### 4. FastAPI vs Flask/Django

**Decision**: Use FastAPI for backend
**Rationale**:
- Performance: High-performance ASGI framework
- Modern Python: Native async/await support
- Type safety: Built-in Pydantic integration
- Automatic documentation: OpenAPI/Swagger generation
- Developer experience: Excellent error messages and debugging

**Trade-offs**:
- Newer framework: Smaller ecosystem than Flask/Django
- Learning curve: Async programming concepts

## Security Architecture

### Input Validation

```python
# File validation at multiple layers
def validate_file(self, file) -> Tuple[bool, Optional[str]]:
    # 1. Filename validation
    if not file.filename:
        return False, "No filename provided"
    
    # 2. Extension validation
    if not self.is_allowed_file_type(file.filename):
        return False, f"Invalid file extension"
    
    # 3. Size validation
    if hasattr(file, 'size') and file.size > self.MAX_FILE_SIZE:
        return False, f"File too large"
    
    return True, None

# Content validation
with Image.open(file_path) as img:
    img.verify()  # Verify actual image content
```

### Data Sanitization

```python
def sanitize_field_value(self, value: str) -> str:
    if not value:
        return ""
    
    # Remove control characters and normalize whitespace
    value = re.sub(r'[\r\n\t]', ' ', value)
    value = re.sub(r'\s+', ' ', value)
    value = value.strip()
    
    return value
```

### Filename Security

```python
def sanitize_filename(self, filename: str) -> str:
    # Unicode normalization
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    return filename
```

### Security Measures

1. **File Type Validation**: Whitelist approach for allowed extensions
2. **Content Verification**: Actual image content validation, not just extension
3. **Size Limits**: Configurable maximum file size limits
4. **Path Traversal Protection**: Filename sanitization prevents directory traversal
5. **CSV Injection Prevention**: Field sanitization prevents CSV injection attacks
6. **Input Validation**: Pydantic models validate all input data
7. **Error Handling**: Secure error messages without information disclosure

## Performance Considerations

### Image Processing Optimization

```python
def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (200, 200)) -> Dict[str, Any]:
    with Image.open(image_path) as img:
        # Use high-quality resampling
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Optimize for web delivery
        img.save(thumbnail_path, format="JPEG", quality=85)
```

### Batch Processing

```python
def batch_create_thumbnails(self, image_paths: List[str]) -> List[Dict[str, Any]]:
    results = []
    for image_path in image_paths:
        result = self.create_thumbnail(image_path)
        results.append(result)
    return results
```

### File System Optimization

- **Separate thumbnail directory**: Organized file structure for better performance
- **Format standardization**: Thumbnails saved as JPEG for consistent performance
- **Size optimization**: Balanced quality/size ratio for web delivery

### Memory Management

- **Context managers**: Proper resource cleanup with `with` statements
- **Async stream processing**: File uploads handled as async streams with proper await handling
- **Garbage collection**: Explicit resource disposal in image processing
- **FastAPI UploadFile**: Proper handling of FastAPI's async file objects

## Scalability

### Current Limitations

1. **File system storage**: Limited by server storage capacity
2. **In-memory CSV operations**: Limited by available RAM
3. **No caching**: No caching layer for frequently accessed data
4. **Synchronous image processing**: While file uploads are async, image processing is still synchronous

### Scalability Improvements

#### Horizontal Scaling
```python
# Stateless design enables load balancing
# Services can be instantiated per request
# No shared state between requests
```

#### Database Migration Path
```python
# Easy migration from CSV to database
class DatabaseService:
    def save_annotation(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        # Database implementation
        pass
    
    def read_annotations(self) -> List[Dict[str, Any]]:
        # Database implementation
        pass
```

#### Cloud Storage Integration
```python
# Cloud storage adapter
class CloudImageService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
    
    def upload_image(self, file, filename: str) -> Dict[str, Any]:
        # Cloud storage implementation
        pass
```

#### Async Processing
```python
# Async image processing for better concurrency
async def create_thumbnail_async(self, image_path: str) -> Dict[str, Any]:
    # Async implementation using asyncio
    pass
```

### Performance Monitoring

Recommended monitoring points:
- File upload duration
- Image processing time
- CSV operations performance
- Memory usage during processing
- Disk space utilization

### Caching Strategy

Potential caching layers:
- **Thumbnail caching**: Cache generated thumbnails
- **Metadata caching**: Cache image metadata
- **Statistics caching**: Cache computed statistics
- **Query result caching**: Cache frequently accessed data

## Future Architecture Considerations

### Microservices Migration

The current monolithic architecture can be evolved to microservices:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │    │  Image Service  │    │  Data Service   │
│                 │    │                 │    │                 │
│ FastAPI         │◄──►│ Image Processing│◄──►│ Database/API    │
│ Templates       │    │ Thumbnail Gen   │    │ Annotations     │
│ File Upload     │    │ Metadata        │    │ Statistics      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Event-Driven Architecture

For high-scale deployments:

```
Upload Event → Queue → Image Processing → Thumbnail Generated → Notification
Annotation Event → Queue → Data Processing → Statistics Updated → Webhook
```

### Container Architecture

Docker deployment strategy:

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - uploads:/app/uploads
      - data:/app/data
  
  redis:
    image: redis:alpine
    # Caching layer
    
  postgres:
    image: postgres:13
    # Database for annotations
```

This architecture provides a solid foundation for the current requirements while maintaining flexibility for future enhancements and scaling needs.