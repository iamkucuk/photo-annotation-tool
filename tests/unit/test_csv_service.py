import pytest
import csv
from pathlib import Path
from datetime import datetime

from photo_annotator.services.csv_service import CSVService


class TestCSVService:
    @pytest.fixture
    def csv_service(self, tmp_path):
        csv_file = tmp_path / "annotations.csv"
        return CSVService(str(csv_file))

    @pytest.fixture
    def sample_annotation(self):
        return {
            "image_name": "test_image.jpg",
            "description": "A beautiful sunset over the mountains",
            "tags": "nature,sunset,mountains",
            "labels": "landscape,outdoor",
            "timestamp": "2023-01-01T12:00:00"
        }

    def test_initialize_creates_csv_with_headers(self, csv_service):
        csv_service.initialize()
        
        assert Path(csv_service.filepath).exists()
        
        with open(csv_service.filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)
            expected_headers = ["image_name", "description", "tags", "labels", "timestamp"]
            assert headers == expected_headers

    def test_initialize_does_not_overwrite_existing_file(self, csv_service, sample_annotation):
        csv_service.initialize()
        csv_service.save_annotation(sample_annotation)
        
        csv_service.initialize()
        
        annotations = csv_service.read_annotations()
        assert len(annotations) == 1

    def test_save_annotation_success(self, csv_service, sample_annotation):
        csv_service.initialize()
        result = csv_service.save_annotation(sample_annotation)
        
        assert result["success"] is True
        assert "Annotation saved successfully" in result["message"]

    def test_save_annotation_without_timestamp(self, csv_service):
        csv_service.initialize()
        annotation = {
            "image_name": "test.jpg",
            "description": "Test description",
            "tags": "test",
            "labels": "test"
        }
        
        result = csv_service.save_annotation(annotation)
        
        assert result["success"] is True
        # Check that timestamp was added
        annotations = csv_service.read_annotations()
        assert len(annotations) == 1
        assert annotations[0]["timestamp"] is not None

    def test_save_annotation_with_special_characters(self, csv_service):
        csv_service.initialize()
        annotation = {
            "image_name": "test.jpg",
            "description": "Description with \"quotes\" and, commas",
            "tags": "tag1,tag2,tag3",
            "labels": "label with spaces, another label"
        }
        
        result = csv_service.save_annotation(annotation)
        
        assert result["success"] is True
        
        annotations = csv_service.read_annotations()
        assert len(annotations) == 1
        assert annotations[0]["description"] == "Description with \"quotes\" and, commas"

    def test_read_annotations_empty_file(self, csv_service):
        csv_service.initialize()
        
        annotations = csv_service.read_annotations()
        
        assert annotations == []

    def test_read_annotations_with_data(self, csv_service, sample_annotation):
        csv_service.initialize()
        csv_service.save_annotation(sample_annotation)
        
        annotations = csv_service.read_annotations()
        
        assert len(annotations) == 1
        assert annotations[0]["image_name"] == sample_annotation["image_name"]
        assert annotations[0]["description"] == sample_annotation["description"]

    def test_read_annotations_multiple_entries(self, csv_service):
        csv_service.initialize()
        
        annotations_data = [
            {"image_name": "img1.jpg", "description": "First image", "tags": "tag1", "labels": "label1"},
            {"image_name": "img2.jpg", "description": "Second image", "tags": "tag2", "labels": "label2"},
            {"image_name": "img3.jpg", "description": "Third image", "tags": "tag3", "labels": "label3"}
        ]
        
        for annotation in annotations_data:
            csv_service.save_annotation(annotation)
        
        annotations = csv_service.read_annotations()
        
        assert len(annotations) == 3
        assert annotations[0]["image_name"] == "img1.jpg"
        assert annotations[2]["image_name"] == "img3.jpg"

    def test_get_annotations_for_image(self, csv_service):
        csv_service.initialize()
        
        annotations_data = [
            {"image_name": "img1.jpg", "description": "First description", "tags": "tag1", "labels": "label1"},
            {"image_name": "img2.jpg", "description": "Second description", "tags": "tag2", "labels": "label2"},
            {"image_name": "img1.jpg", "description": "Another description", "tags": "tag3", "labels": "label3"}
        ]
        
        for annotation in annotations_data:
            csv_service.save_annotation(annotation)
        
        img1_annotations = csv_service.get_annotations_for_image("img1.jpg")
        
        assert len(img1_annotations) == 2
        assert all(ann["image_name"] == "img1.jpg" for ann in img1_annotations)

    def test_sanitize_field_value(self, csv_service):
        test_cases = [
            ("Simple text", "Simple text"),
            ("Text with \"quotes\"", "Text with \"quotes\""),
            ("Text with\nnewlines\r\n", "Text with newlines"),
            ("Text\twith\ttabs", "Text with tabs"),
            ("", "")
        ]
        
        for input_value, expected in test_cases:
            result = csv_service.sanitize_field_value(input_value)
            assert result == expected

    def test_export_to_file(self, csv_service, tmp_path):
        csv_service.initialize()
        
        annotations_data = [
            {"image_name": "img1.jpg", "description": "First", "tags": "tag1", "labels": "label1"},
            {"image_name": "img2.jpg", "description": "Second", "tags": "tag2", "labels": "label2"}
        ]
        
        for annotation in annotations_data:
            csv_service.save_annotation(annotation)
        
        export_path = tmp_path / "export.csv"
        result = csv_service.export_to_file(str(export_path))
        
        assert result["success"] is True
        assert Path(export_path).exists()
        
        # Verify exported content
        with open(export_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "img1.jpg" in content
            assert "img2.jpg" in content

    def test_get_statistics(self, csv_service):
        csv_service.initialize()
        
        annotations_data = [
            {"image_name": "img1.jpg", "description": "First", "tags": "nature,landscape", "labels": "outdoor"},
            {"image_name": "img2.jpg", "description": "Second", "tags": "portrait", "labels": "indoor"},
            {"image_name": "img3.jpg", "description": "Third", "tags": "nature", "labels": "outdoor"}
        ]
        
        for annotation in annotations_data:
            csv_service.save_annotation(annotation)
        
        stats = csv_service.get_statistics()
        
        assert stats["total_annotations"] == 3
        assert stats["total_images"] == 3
        assert stats["most_common_tags"] is not None
        assert stats["most_common_labels"] is not None