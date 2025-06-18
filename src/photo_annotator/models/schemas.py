from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AnnotationRequest(BaseModel):
    image_name: str = Field(..., description="Name of the image file")
    description: str = Field(..., min_length=1, description="Description of the image")
    tags: str = Field(default="", description="Comma-separated tags")
    labels: str = Field(default="", description="Comma-separated labels")


class AnnotationResponse(BaseModel):
    success: bool
    message: str
    annotation_id: Optional[str] = None


class ImageUploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    file_path: Optional[str] = None
    thumbnail_path: Optional[str] = None


class ImageListResponse(BaseModel):
    images: List[dict]
    total_count: int


class AnnotationListResponse(BaseModel):
    annotations: List[dict]
    total_count: int


class StatisticsResponse(BaseModel):
    total_annotations: int
    total_images: int
    most_common_tags: List[tuple]
    most_common_labels: List[tuple]