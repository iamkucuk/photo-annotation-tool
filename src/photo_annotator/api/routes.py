import os
from typing import List
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import FileResponse

from photo_annotator.models.schemas import (
    AnnotationRequest,
    AnnotationResponse,
    ImageUploadResponse,
    ImageListResponse,
    AnnotationListResponse,
    StatisticsResponse
)
from photo_annotator.services.csv_service import CSVService
from photo_annotator.services.file_handler import FileHandler
from photo_annotator.services.image_service import ImageService

router = APIRouter()

# Initialize services (these will be dependency injected in production)
UPLOAD_DIR = Path("uploads")
csv_service = CSVService("annotations.csv")
file_handler = FileHandler(str(UPLOAD_DIR))
image_service = ImageService(str(UPLOAD_DIR))

def get_uploaded_images() -> List[dict]:
    """Get list of uploaded images with their thumbnails"""
    images = []
    if UPLOAD_DIR.exists():
        for image_file in UPLOAD_DIR.glob("*.jpg"):
            if not image_file.name.startswith("thumb_") and not image_file.name.startswith("web_"):
                thumbnail_path = image_service.get_thumbnail_path(str(image_file))
                images.append({
                    "filename": image_file.name,
                    "path": str(image_file),
                    "thumbnail": thumbnail_path if Path(thumbnail_path).exists() else None
                })
        
        # Include other image formats
        for ext in [".png", ".gif", ".bmp", ".webp", ".jpeg"]:
            for image_file in UPLOAD_DIR.glob(f"*{ext}"):
                if not image_file.name.startswith("thumb_") and not image_file.name.startswith("web_"):
                    thumbnail_path = image_service.get_thumbnail_path(str(image_file))
                    images.append({
                        "filename": image_file.name,
                        "path": str(image_file),
                        "thumbnail": thumbnail_path if Path(thumbnail_path).exists() else None
                    })
    
    return sorted(images, key=lambda x: x["filename"])

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload a single image file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Upload file
    upload_result = await file_handler.upload_single_file(file)
    
    if not upload_result["success"]:
        return ImageUploadResponse(
            success=False,
            message=upload_result["error"]
        )
    
    # Create thumbnail
    thumbnail_result = image_service.create_thumbnail(upload_result["file_path"])
    
    return ImageUploadResponse(
        success=True,
        message="Image uploaded successfully",
        filename=upload_result["filename"],
        file_path=upload_result["file_path"],
        thumbnail_path=thumbnail_result.get("thumbnail_path") if thumbnail_result["success"] else None
    )

@router.post("/upload-multiple")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """Upload multiple image files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Upload files
    upload_results = await file_handler.upload_multiple_files(files)
    
    # Create thumbnails for successful uploads
    file_paths = [result["file_path"] for result in upload_results if result["success"]]
    thumbnail_results = image_service.batch_create_thumbnails(file_paths)
    
    # Combine results
    combined_results = []
    for i, upload_result in enumerate(upload_results):
        if upload_result["success"]:
            thumbnail_path = thumbnail_results[i]["thumbnail_path"] if i < len(thumbnail_results) and thumbnail_results[i]["success"] else None
            combined_results.append({
                "success": True,
                "filename": upload_result["filename"],
                "file_path": upload_result["file_path"],
                "thumbnail_path": thumbnail_path
            })
        else:
            combined_results.append({
                "success": False,
                "error": upload_result["error"]
            })
    
    return combined_results

@router.post("/annotate", response_model=AnnotationResponse)
async def save_annotation(annotation: AnnotationRequest):
    """Save an annotation for an image"""
    result = csv_service.save_annotation(annotation.model_dump())
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return AnnotationResponse(
        success=True,
        message=result["message"]
    )

@router.get("/annotations", response_model=AnnotationListResponse)
async def get_annotations():
    """Get all annotations"""
    annotations = csv_service.read_annotations()
    
    return AnnotationListResponse(
        annotations=annotations,
        total_count=len(annotations)
    )

@router.get("/images", response_model=ImageListResponse)
async def get_images():
    """Get list of uploaded images"""
    images = get_uploaded_images()
    
    return ImageListResponse(
        images=images,
        total_count=len(images)
    )

@router.get("/images/{image_name}/annotations")
async def get_image_annotations(image_name: str):
    """Get annotations for a specific image"""
    annotations = csv_service.get_annotations_for_image(image_name)
    return annotations

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get annotation statistics"""
    stats = csv_service.get_statistics()
    
    return StatisticsResponse(
        total_annotations=stats["total_annotations"],
        total_images=stats["total_images"],
        most_common_tags=stats["most_common_tags"],
        most_common_labels=stats["most_common_labels"]
    )

@router.delete("/images/{image_name}")
async def delete_image(image_name: str):
    """Delete an image and its annotations"""
    # Delete the physical image file and thumbnail
    image_path = UPLOAD_DIR / image_name
    thumbnail_path = Path(image_service.get_thumbnail_path(str(image_path)))
    
    files_deleted = []
    errors = []
    
    # Delete main image file
    if image_path.exists():
        try:
            image_path.unlink()
            files_deleted.append(str(image_path))
        except Exception as e:
            errors.append(f"Failed to delete {image_path}: {str(e)}")
    
    # Delete thumbnail
    if thumbnail_path.exists():
        try:
            thumbnail_path.unlink()
            files_deleted.append(str(thumbnail_path))
        except Exception as e:
            errors.append(f"Failed to delete thumbnail {thumbnail_path}: {str(e)}")
    
    # Delete annotations from CSV
    csv_result = csv_service.delete_image_annotations(image_name)
    
    return {
        "success": len(errors) == 0,
        "message": f"Deleted image {image_name}",
        "files_deleted": files_deleted,
        "annotations_deleted": csv_result.get("deleted_count", 0),
        "errors": errors if errors else None
    }

@router.get("/export")
async def export_annotations():
    """Export annotations as CSV file"""
    export_path = "/tmp/annotations_export.csv"
    result = csv_service.export_to_file(export_path)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return FileResponse(
        export_path,
        media_type="text/csv",
        filename="annotations.csv"
    )