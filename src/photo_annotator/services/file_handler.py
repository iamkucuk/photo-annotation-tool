import os
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image


class FileHandler:
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, upload_directory: str):
        self.upload_directory = Path(upload_directory)
        self.upload_directory.mkdir(parents=True, exist_ok=True)

    async def upload_single_file(self, file) -> Dict[str, Any]:
        try:
            is_valid, error = self.validate_file(file)
            if not is_valid:
                return {"success": False, "error": error}

            sanitized_filename = self.sanitize_filename(file.filename)
            file_path = self.upload_directory / sanitized_filename
            
            # Handle duplicate filenames
            counter = 1
            original_path = file_path
            while file_path.exists():
                name = original_path.stem
                ext = original_path.suffix
                file_path = self.upload_directory / f"{name}_{counter}{ext}"
                counter += 1

            # Save file
            with open(file_path, "wb") as f:
                # Reset file position to beginning
                await file.seek(0)
                content = await file.read()
                f.write(content)

            # Verify it's actually an image by trying to open it
            try:
                with Image.open(file_path) as img:
                    img.verify()
            except Exception:
                os.unlink(file_path)
                return {"success": False, "error": "Invalid image file"}

            return {
                "success": True,
                "filename": file_path.name,
                "file_path": str(file_path),
                "original_filename": file.filename
            }

        except Exception as e:
            return {"success": False, "error": f"Upload failed: {str(e)}"}

    async def upload_multiple_files(self, files) -> List[Dict[str, Any]]:
        results = []
        for file in files:
            result = await self.upload_single_file(file)
            results.append(result)
        return results

    def validate_file(self, file) -> Tuple[bool, Optional[str]]:
        if not file.filename:
            return False, "No filename provided"

        if not self.is_allowed_file_type(file.filename):
            return False, f"Invalid file extension. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"

        if hasattr(file, 'size') and file.size > self.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size: {self.MAX_FILE_SIZE // 1024 // 1024}MB"

        return True, None

    def sanitize_filename(self, filename: str) -> str:
        # Remove unicode characters
        filename = unicodedata.normalize('NFKD', filename)
        filename = filename.encode('ascii', 'ignore').decode('ascii')
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Replace spaces with underscores
        filename = re.sub(r'\s+', '_', filename)
        
        # Remove leading/trailing dots and underscores
        filename = filename.strip('._')
        
        # Ensure we have at least something
        if not filename:
            filename = "unnamed_file"
            
        return filename

    def get_file_extension(self, filename: str) -> str:
        return Path(filename).suffix.lower()

    def is_allowed_file_type(self, filename: str) -> bool:
        ext = self.get_file_extension(filename)
        return ext in self.ALLOWED_EXTENSIONS