import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image

from photo_annotator.services.image_service import ImageService


class TestImageService:
    @pytest.fixture
    def image_service(self, tmp_path):
        return ImageService(str(tmp_path))

    @pytest.fixture
    def sample_image_path(self, tmp_path):
        image = Image.new("RGB", (800, 600), color="blue")
        image_path = tmp_path / "sample.jpg"
        image.save(image_path, "JPEG")
        return str(image_path)

    @pytest.fixture
    def large_image_path(self, tmp_path):
        image = Image.new("RGB", (2000, 1500), color="green")
        image_path = tmp_path / "large.jpg"
        image.save(image_path, "JPEG")
        return str(image_path)

    @pytest.fixture
    def invalid_image_path(self, tmp_path):
        invalid_file = tmp_path / "invalid.jpg"
        invalid_file.write_text("This is not an image")
        return str(invalid_file)

    def test_create_thumbnail_success(self, image_service, sample_image_path):
        result = image_service.create_thumbnail(sample_image_path, (150, 150))
        
        assert result["success"] is True
        assert result["thumbnail_path"] is not None
        assert Path(result["thumbnail_path"]).exists()
        
        # Verify thumbnail dimensions
        with Image.open(result["thumbnail_path"]) as thumb:
            assert thumb.size[0] <= 150
            assert thumb.size[1] <= 150

    def test_create_thumbnail_with_default_size(self, image_service, sample_image_path):
        result = image_service.create_thumbnail(sample_image_path)
        
        assert result["success"] is True
        with Image.open(result["thumbnail_path"]) as thumb:
            assert thumb.size[0] <= 200
            assert thumb.size[1] <= 200

    def test_create_thumbnail_invalid_image(self, image_service, invalid_image_path):
        result = image_service.create_thumbnail(invalid_image_path)
        
        assert result["success"] is False
        assert "Failed to create thumbnail" in result["error"]

    def test_create_thumbnail_nonexistent_file(self, image_service):
        result = image_service.create_thumbnail("/nonexistent/file.jpg")
        
        assert result["success"] is False
        assert "Image file not found" in result["error"]

    def test_get_image_metadata(self, image_service, sample_image_path):
        metadata = image_service.get_image_metadata(sample_image_path)
        
        assert metadata["success"] is True
        assert metadata["width"] == 800
        assert metadata["height"] == 600
        assert metadata["format"] == "JPEG"
        assert metadata["mode"] == "RGB"
        assert "file_size" in metadata
        assert "created_at" in metadata

    def test_get_image_metadata_invalid_file(self, image_service, invalid_image_path):
        metadata = image_service.get_image_metadata(invalid_image_path)
        
        assert metadata["success"] is False
        assert "Failed to read image metadata" in metadata["error"]

    def test_validate_image_valid(self, image_service, sample_image_path):
        is_valid, error = image_service.validate_image(sample_image_path)
        
        assert is_valid is True
        assert error is None

    def test_validate_image_invalid(self, image_service, invalid_image_path):
        is_valid, error = image_service.validate_image(invalid_image_path)
        
        assert is_valid is False
        assert "Invalid image file" in error

    def test_validate_image_nonexistent(self, image_service):
        is_valid, error = image_service.validate_image("/nonexistent/file.jpg")
        
        assert is_valid is False
        assert "Image file not found" in error

    def test_get_thumbnail_path(self, image_service):
        original_path = "/path/to/image.jpg"
        thumb_path = image_service.get_thumbnail_path(original_path)
        
        assert "thumb_image.jpg" in thumb_path
        assert str(image_service.thumbnail_dir) in thumb_path

    def test_resize_image_for_web(self, image_service, large_image_path):
        result = image_service.resize_image_for_web(large_image_path, max_width=1200)
        
        assert result["success"] is True
        with Image.open(result["resized_path"]) as img:
            assert img.width <= 1200
            assert img.height <= 900  # Proportional resize

    def test_batch_create_thumbnails(self, image_service, sample_image_path, large_image_path):
        image_paths = [sample_image_path, large_image_path]
        results = image_service.batch_create_thumbnails(image_paths)
        
        assert len(results) == 2
        assert all(result["success"] for result in results)
        assert all(Path(result["thumbnail_path"]).exists() for result in results)