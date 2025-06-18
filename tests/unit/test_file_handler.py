import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image

from photo_annotator.services.file_handler import FileHandler


class TestFileHandler:
    @pytest.fixture
    def file_handler(self, tmp_path):
        upload_dir = tmp_path / "uploads"
        upload_dir.mkdir()
        return FileHandler(str(upload_dir))

    @pytest.fixture
    def mock_image_file(self):
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)
        
        mock_file = Mock()
        mock_file.filename = "test_image.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.size = len(image_bytes.getvalue())
        mock_file.read = Mock(return_value=image_bytes.getvalue())
        return mock_file

    @pytest.fixture
    def mock_invalid_file(self):
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = Mock(return_value=b"Not an image")
        return mock_file

    def test_upload_single_file_success(self, file_handler, mock_image_file):
        result = file_handler.upload_single_file(mock_image_file)
        
        assert result["success"] is True
        assert result["filename"] == "test_image.jpg"
        assert result["file_path"] is not None
        assert Path(result["file_path"]).exists()

    def test_upload_single_file_invalid_type(self, file_handler, mock_invalid_file):
        result = file_handler.upload_single_file(mock_invalid_file)
        
        assert result["success"] is False
        assert "Invalid file extension" in result["error"]

    def test_upload_single_file_too_large(self, file_handler, mock_image_file):
        mock_image_file.size = 11 * 1024 * 1024  # 11MB
        
        result = file_handler.upload_single_file(mock_image_file)
        
        assert result["success"] is False
        assert "File too large" in result["error"]

    def test_upload_multiple_files(self, file_handler, mock_image_file):
        files = [mock_image_file, mock_image_file]
        
        results = file_handler.upload_multiple_files(files)
        
        assert len(results) == 2
        assert all(result["success"] for result in results)

    def test_file_validation_valid_image(self, file_handler, mock_image_file):
        is_valid, error = file_handler.validate_file(mock_image_file)
        
        assert is_valid is True
        assert error is None

    def test_file_validation_invalid_extension(self, file_handler):
        mock_file = Mock()
        mock_file.filename = "test.exe"
        mock_file.content_type = "application/octet-stream"
        mock_file.size = 1000
        
        is_valid, error = file_handler.validate_file(mock_file)
        
        assert is_valid is False
        assert "Invalid file extension" in error

    def test_file_validation_no_filename(self, file_handler):
        mock_file = Mock()
        mock_file.filename = None
        
        is_valid, error = file_handler.validate_file(mock_file)
        
        assert is_valid is False
        assert "No filename provided" in error

    def test_filename_sanitization(self, file_handler):
        test_cases = [
            ("image with spaces.jpg", "image_with_spaces.jpg"),
            ("image@#$%^&*().jpg", "image.jpg"),
            ("très_beau_été.jpg", "tres_beau_ete.jpg"),
            ("../../../etc/passwd.jpg", "etcpasswd.jpg")
        ]
        
        for original, expected in test_cases:
            sanitized = file_handler.sanitize_filename(original)
            assert sanitized == expected

    def test_get_file_extension(self, file_handler):
        assert file_handler.get_file_extension("image.jpg") == ".jpg"
        assert file_handler.get_file_extension("image.JPEG") == ".jpeg"
        assert file_handler.get_file_extension("image") == ""

    def test_is_allowed_file_type(self, file_handler):
        assert file_handler.is_allowed_file_type("image.jpg") is True
        assert file_handler.is_allowed_file_type("image.png") is True
        assert file_handler.is_allowed_file_type("image.gif") is True
        assert file_handler.is_allowed_file_type("document.pdf") is False
        assert file_handler.is_allowed_file_type("script.js") is False