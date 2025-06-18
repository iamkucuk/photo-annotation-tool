import pytest
from fastapi.testclient import TestClient
from fastapi.responses import FileResponse
from unittest.mock import Mock, patch
from io import BytesIO
from PIL import Image

from photo_annotator.main import app
from photo_annotator.models.schemas import AnnotationRequest


class TestAPIRoutes:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_image_file(self):
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)
        return ("test_image.jpg", image_bytes, "image/jpeg")

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "photo-annotation-tool"}

    def test_upload_single_image_success(self, client, mock_image_file):
        with patch("photo_annotator.api.routes.file_handler") as mock_fh, \
             patch("photo_annotator.api.routes.image_service") as mock_is:
            
            mock_fh.upload_single_file.return_value = {
                "success": True,
                "filename": "test_image.jpg",
                "file_path": "/uploads/test_image.jpg"
            }
            mock_is.create_thumbnail.return_value = {
                "success": True,
                "thumbnail_path": "/uploads/thumbnails/thumb_test_image.jpg"
            }

            response = client.post(
                "/api/upload",
                files={"file": mock_image_file}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["filename"] == "test_image.jpg"

    def test_upload_single_image_failure(self, client, mock_image_file):
        with patch("photo_annotator.api.routes.file_handler") as mock_fh:
            mock_fh.upload_single_file.return_value = {
                "success": False,
                "error": "Invalid file type"
            }

            response = client.post(
                "/api/upload",
                files={"file": mock_image_file}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Invalid file type" in data["message"]

    def test_upload_multiple_images(self, client, mock_image_file):
        with patch("photo_annotator.api.routes.file_handler") as mock_fh, \
             patch("photo_annotator.api.routes.image_service") as mock_is:
            
            mock_fh.upload_multiple_files.return_value = [
                {"success": True, "filename": "img1.jpg", "file_path": "/uploads/img1.jpg"},
                {"success": True, "filename": "img2.jpg", "file_path": "/uploads/img2.jpg"}
            ]
            mock_is.batch_create_thumbnails.return_value = [
                {"success": True, "thumbnail_path": "/uploads/thumbnails/thumb_img1.jpg"},
                {"success": True, "thumbnail_path": "/uploads/thumbnails/thumb_img2.jpg"}
            ]

            files = [
                ("files", ("img1.jpg", BytesIO(b"fake image 1"), "image/jpeg")),
                ("files", ("img2.jpg", BytesIO(b"fake image 2"), "image/jpeg"))
            ]

            response = client.post("/api/upload-multiple", files=files)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert all(item["success"] for item in data)

    def test_save_annotation_success(self, client):
        with patch("photo_annotator.api.routes.csv_service") as mock_csv:
            mock_csv.save_annotation.return_value = {
                "success": True,
                "message": "Annotation saved successfully"
            }

            annotation_data = {
                "image_name": "test_image.jpg",
                "description": "A beautiful sunset",
                "tags": "nature,sunset",
                "labels": "landscape"
            }

            response = client.post("/api/annotate", json=annotation_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "successfully" in data["message"]

    def test_save_annotation_validation_error(self, client):
        annotation_data = {
            "image_name": "test_image.jpg",
            "description": "",  # Empty description should fail validation
            "tags": "nature",
            "labels": "landscape"
        }

        response = client.post("/api/annotate", json=annotation_data)

        assert response.status_code == 422  # Validation error

    def test_get_annotations(self, client):
        with patch("photo_annotator.api.routes.csv_service") as mock_csv:
            mock_csv.read_annotations.return_value = [
                {
                    "image_name": "img1.jpg",
                    "description": "First image",
                    "tags": "tag1",
                    "labels": "label1",
                    "timestamp": "2023-01-01T12:00:00"
                },
                {
                    "image_name": "img2.jpg",
                    "description": "Second image",
                    "tags": "tag2",
                    "labels": "label2",
                    "timestamp": "2023-01-01T12:01:00"
                }
            ]

            response = client.get("/api/annotations")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 2
            assert len(data["annotations"]) == 2

    def test_get_image_list(self, client):
        with patch("photo_annotator.api.routes.get_uploaded_images") as mock_get_images:
            mock_get_images.return_value = [
                {"filename": "img1.jpg", "path": "/uploads/img1.jpg", "thumbnail": "/uploads/thumbnails/thumb_img1.jpg"},
                {"filename": "img2.jpg", "path": "/uploads/img2.jpg", "thumbnail": "/uploads/thumbnails/thumb_img2.jpg"}
            ]

            response = client.get("/api/images")

            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 2
            assert len(data["images"]) == 2

    def test_get_statistics(self, client):
        with patch("photo_annotator.api.routes.csv_service") as mock_csv:
            mock_csv.get_statistics.return_value = {
                "total_annotations": 10,
                "total_images": 5,
                "most_common_tags": [("nature", 3), ("landscape", 2)],
                "most_common_labels": [("outdoor", 4), ("indoor", 1)]
            }

            response = client.get("/api/statistics")

            assert response.status_code == 200
            data = response.json()
            assert data["total_annotations"] == 10
            assert data["total_images"] == 5

    def test_export_csv(self, client):
        # Skip the actual file test since FileResponse is complex to mock
        # Just test that the service method would be called correctly
        with patch("photo_annotator.api.routes.csv_service") as mock_csv:
            mock_csv.export_to_file.return_value = {
                "success": False,
                "error": "Test error"
            }

            response = client.get("/api/export")

            assert response.status_code == 500  # Should return error when export fails

    def test_get_image_annotations(self, client):
        with patch("photo_annotator.api.routes.csv_service") as mock_csv:
            mock_csv.get_annotations_for_image.return_value = [
                {
                    "image_name": "test.jpg",
                    "description": "Test description",
                    "tags": "test",
                    "labels": "test",
                    "timestamp": "2023-01-01T12:00:00"
                }
            ]

            response = client.get("/api/images/test.jpg/annotations")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["image_name"] == "test.jpg"