# API Documentation

This document provides comprehensive documentation for the Photo Annotation Tool API. The API is built with FastAPI and provides RESTful endpoints for image upload, annotation management, and data export.

## Base URL

```
http://localhost:8001/api
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Content Types

- **Request Content-Type**: `application/json` for JSON payloads, `multipart/form-data` for file uploads
- **Response Content-Type**: `application/json` for most endpoints, `text/csv` for export

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
    "detail": "Error message description"
}
```

Common status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `422`: Unprocessable Entity (validation errors)
- `500`: Internal Server Error

## Endpoints

### Health Check

#### GET `/health`

Health check endpoint to verify service availability.

**Response:**
```json
{
    "status": "healthy",
    "service": "photo-annotation-tool"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8001/health"
```

---

### Image Upload

#### POST `/api/upload`

Upload a single image file.

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (required)

**File Requirements:**
- Supported formats: JPG, JPEG, PNG, GIF, BMP, WEBP
- Maximum size: 10MB
- Must be a valid image file

**Response:**
```json
{
    "success": true,
    "message": "Image uploaded successfully",
    "filename": "sanitized_filename.jpg",
    "file_path": "/uploads/sanitized_filename.jpg",
    "thumbnail_path": "/uploads/thumbnails/thumb_sanitized_filename.jpg"
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Invalid file extension. Allowed: .jpg, .jpeg, .png, .gif, .bmp, .webp"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8001/api/upload" \
  -F "file=@/path/to/image.jpg"
```

#### POST `/api/upload-multiple`

Upload multiple image files in a single request.

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `files` (multiple files)

**Response:**
```json
[
    {
        "success": true,
        "filename": "image1.jpg",
        "file_path": "/uploads/image1.jpg",
        "thumbnail_path": "/uploads/thumbnails/thumb_image1.jpg"
    },
    {
        "success": false,
        "error": "File too large. Maximum size: 10MB"
    }
]
```

**Example:**
```bash
curl -X POST "http://localhost:8001/api/upload-multiple" \
  -F "files=@/path/to/image1.jpg" \
  -F "files=@/path/to/image2.png"
```

---

### Annotation Management

#### POST `/api/annotate`

Save an annotation for an uploaded image.

**Request Body:**
```json
{
    "image_name": "image1.jpg",
    "description": "A beautiful sunset over the mountains",
    "tags": "sunset, mountains, nature, landscape",
    "labels": "outdoor, scenery, golden hour"
}
```

**Request Schema:**
- `image_name` (string, required): Name of the image file
- `description` (string, required): Description of the image (min_length=1)
- `tags` (string, optional): Comma-separated tags
- `labels` (string, optional): Comma-separated labels

**Response:**
```json
{
    "success": true,
    "message": "Annotation saved successfully",
    "annotation_id": null
}
```

**Example:**
```bash
curl -X POST "http://localhost:8001/api/annotate" \
  -H "Content-Type: application/json" \
  -d '{
    "image_name": "sunset.jpg",
    "description": "Beautiful sunset over mountains",
    "tags": "nature, landscape",
    "labels": "outdoor, scenery"
  }'
```

#### GET `/api/annotations`

Retrieve all annotations.

**Response:**
```json
{
    "annotations": [
        {
            "image_name": "sunset.jpg",
            "description": "Beautiful sunset over mountains",
            "tags": "nature, landscape",
            "labels": "outdoor, scenery",
            "timestamp": "2024-01-15T10:30:00"
        }
    ],
    "total_count": 1
}
```

**Example:**
```bash
curl -X GET "http://localhost:8001/api/annotations"
```

#### GET `/api/images/{image_name}/annotations`

Get all annotations for a specific image.

**Parameters:**
- `image_name` (path parameter): Name of the image file

**Response:**
```json
[
    {
        "image_name": "sunset.jpg",
        "description": "Beautiful sunset over mountains",
        "tags": "nature, landscape",
        "labels": "outdoor, scenery",
        "timestamp": "2024-01-15T10:30:00"
    }
]
```

**Example:**
```bash
curl -X GET "http://localhost:8001/api/images/sunset.jpg/annotations"
```

---

### Image Management

#### GET `/api/images`

Get list of all uploaded images.

**Response:**
```json
{
    "images": [
        {
            "filename": "sunset.jpg",
            "path": "/uploads/sunset.jpg",
            "thumbnail": "/uploads/thumbnails/thumb_sunset.jpg"
        }
    ],
    "total_count": 1
}
```

**Example:**
```bash
curl -X GET "http://localhost:8001/api/images"
```

#### DELETE `/api/images/{image_name}`

Delete an image and all its associated annotations.

**Parameters:**
- `image_name` (path parameter): Name of the image file to delete

**Behavior:**
- Deletes the original image file from the uploads directory
- Deletes the thumbnail file from the thumbnails directory
- Removes all annotations for this image from the CSV file
- Returns details about what was deleted

**Response:**
```json
{
    "success": true,
    "message": "Deleted image sunset.jpg",
    "files_deleted": [
        "/uploads/sunset.jpg",
        "/uploads/thumbnails/thumb_sunset.jpg"
    ],
    "annotations_deleted": 2,
    "errors": null
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Deleted image sunset.jpg",
    "files_deleted": ["/uploads/sunset.jpg"],
    "annotations_deleted": 2,
    "errors": ["Failed to delete thumbnail /uploads/thumbnails/thumb_sunset.jpg: Permission denied"]
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8001/api/images/sunset.jpg"
```

**Security Considerations:**
- This operation is irreversible
- All annotations for the image will be permanently deleted
- Ensure proper backup procedures before implementing in production

---

### Statistics

#### GET `/api/statistics`

Get annotation statistics including counts and most common tags/labels.

**Response:**
```json
{
    "total_annotations": 25,
    "total_images": 20,
    "most_common_tags": [
        ["nature", 12],
        ["landscape", 8],
        ["outdoor", 6]
    ],
    "most_common_labels": [
        ["scenery", 10],
        ["wildlife", 7],
        ["architecture", 5]
    ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8001/api/statistics"
```

---

### Data Export

#### GET `/api/export`

Export all annotations as a CSV file.

**Response:**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="annotations.csv"`

**CSV Format:**
```csv
image_name,description,tags,labels,timestamp
sunset.jpg,"Beautiful sunset over mountains","nature, landscape","outdoor, scenery",2024-01-15T10:30:00
```

**Example:**
```bash
curl -X GET "http://localhost:8001/api/export" \
  -o annotations.csv
```

## Data Models

### AnnotationRequest

```python
class AnnotationRequest(BaseModel):
    image_name: str = Field(..., description="Name of the image file")
    description: str = Field(..., min_length=1, description="Description of the image")
    tags: str = Field(default="", description="Comma-separated tags")
    labels: str = Field(default="", description="Comma-separated labels")
```

### AnnotationResponse

```python
class AnnotationResponse(BaseModel):
    success: bool
    message: str
    annotation_id: Optional[str] = None
```

### ImageUploadResponse

```python
class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
```

### ImageListResponse

```python
class ImageListResponse(BaseModel):
    images: List[dict]
    total_count: int
```

### AnnotationListResponse

```python
class AnnotationListResponse(BaseModel):
    annotations: List[dict]
    total_count: int
```

### StatisticsResponse

```python
class StatisticsResponse(BaseModel):
    total_annotations: int
    total_images: int
    most_common_tags: List[tuple]
    most_common_labels: List[tuple]
```

## Implementation Details

### File Handling

The API implements several security and validation measures:

1. **File Type Validation**: Only allows specific image formats
2. **File Size Limits**: Maximum 10MB per file
3. **Content Validation**: Verifies actual image content, not just extension
4. **Filename Sanitization**: Removes dangerous characters and normalizes names
5. **Duplicate Handling**: Automatically handles duplicate filenames
6. **Async File Processing**: Uses asynchronous file I/O for better performance and proper handling of FastAPI's UploadFile objects

### Image Processing

- **Thumbnail Generation**: Automatic thumbnail creation (200x200px max)
- **Format Conversion**: Thumbnails are saved as JPEG for consistency
- **Quality Optimization**: Balanced quality/size ratio for thumbnails
- **Aspect Ratio**: Maintains original aspect ratio in thumbnails

### Data Storage

- **CSV Format**: Simple, portable data format
- **Field Sanitization**: Prevents CSV injection attacks
- **Timestamp Addition**: Automatic timestamp for each annotation
- **Data Validation**: Server-side validation of all input data

## Error Codes and Troubleshooting

### Upload Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No file provided" | Empty file upload | Ensure file is selected |
| "Invalid file extension" | Unsupported format | Use JPG, PNG, GIF, BMP, or WEBP |
| "File too large" | File exceeds 10MB | Reduce file size |
| "Invalid image file" | Corrupted image | Use valid image file |
| "Upload failed: a bytes-like object is required" | FastAPI async file handling issue | Fixed in v1.0.1 - ensure server is updated |

### Annotation Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Description is required" | Empty description | Provide description text |
| "Image not found" | Invalid image name | Use exact filename from upload |

### General Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "Failed to save annotation" | File system error | Check disk space and permissions |
| "Failed to create thumbnail" | Image processing error | Verify image integrity |

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing:

- Request rate limiting per IP
- File upload size/count limits per time period
- API key-based authentication and quotas

## OpenAPI Documentation

The API automatically generates OpenAPI (Swagger) documentation available at:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

## CORS Configuration

The API is configured with permissive CORS settings for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, configure specific origins:

```python
allow_origins=["https://yourdomain.com"]
```

## Testing the API

### Using cURL

See examples above for each endpoint.

### Using Python requests

```python
import requests

# Upload image
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/api/upload',
        files={'file': f}
    )

# Save annotation
response = requests.post(
    'http://localhost:8001/api/annotate',
    json={
        'image_name': 'image.jpg',
        'description': 'Test description',
        'tags': 'test, example',
        'labels': 'demo'
    }
)
```

### Using JavaScript fetch

```javascript
// Upload image
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData
});

// Save annotation
const response = await fetch('/api/annotate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        image_name: 'image.jpg',
        description: 'Test description',
        tags: 'test, example',
        labels: 'demo'
    })
});
```