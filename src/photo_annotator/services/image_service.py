import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from PIL import Image, ImageOps
from datetime import datetime


class ImageService:
    def __init__(self, base_directory: str):
        self.base_directory = Path(base_directory)
        self.thumbnail_dir = self.base_directory / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def create_thumbnail(
        self, image_path: str, size: Tuple[int, int] = (200, 200)
    ) -> Dict[str, Any]:
        try:
            if not Path(image_path).exists():
                return {"success": False, "error": "Image file not found"}

            with Image.open(image_path) as img:
                # Create thumbnail maintaining aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail path
                thumbnail_path = self.get_thumbnail_path(image_path)
                
                # Save thumbnail
                img.save(thumbnail_path, format="JPEG", quality=85)
                
                return {
                    "success": True,
                    "thumbnail_path": str(thumbnail_path),
                    "original_size": self.get_image_metadata(image_path)["width"] if self.get_image_metadata(image_path)["success"] else None,
                    "thumbnail_size": img.size
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to create thumbnail: {str(e)}"}

    def get_thumbnail_path(self, original_path: str) -> str:
        original_file = Path(original_path)
        thumb_name = f"thumb_{original_file.name}"
        return str(self.thumbnail_dir / thumb_name)

    def get_image_metadata(self, image_path: str) -> Dict[str, Any]:
        try:
            if not Path(image_path).exists():
                return {"success": False, "error": "Image file not found"}

            with Image.open(image_path) as img:
                file_stats = os.stat(image_path)
                
                return {
                    "success": True,
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "file_size": file_stats.st_size,
                    "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to read image metadata: {str(e)}"}

    def validate_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        try:
            if not Path(image_path).exists():
                return False, "Image file not found"

            with Image.open(image_path) as img:
                img.verify()
                return True, None

        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

    def resize_image_for_web(
        self, image_path: str, max_width: int = 1200, max_height: int = 900
    ) -> Dict[str, Any]:
        try:
            if not Path(image_path).exists():
                return {"success": False, "error": "Image file not found"}

            with Image.open(image_path) as img:
                # Calculate new size maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Generate resized image path
                original_file = Path(image_path)
                resized_name = f"web_{original_file.name}"
                resized_path = self.base_directory / resized_name
                
                # Save resized image
                img.save(resized_path, format="JPEG", quality=90, optimize=True)
                
                return {
                    "success": True,
                    "resized_path": str(resized_path),
                    "new_size": img.size
                }

        except Exception as e:
            return {"success": False, "error": f"Failed to resize image: {str(e)}"}

    def batch_create_thumbnails(
        self, image_paths: List[str], size: Tuple[int, int] = (200, 200)
    ) -> List[Dict[str, Any]]:
        results = []
        for image_path in image_paths:
            result = self.create_thumbnail(image_path, size)
            results.append(result)
        return results