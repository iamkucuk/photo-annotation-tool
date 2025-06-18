import csv
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter


class CSVService:
    FIELDNAMES = ["image_name", "description", "tags", "labels", "timestamp"]

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        if not self.filepath.exists():
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def save_annotation(self, annotation: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Ensure timestamp is present
            if "timestamp" not in annotation or not annotation["timestamp"]:
                annotation["timestamp"] = datetime.now().isoformat()

            # Sanitize all field values
            sanitized_annotation = {}
            for field in self.FIELDNAMES:
                value = annotation.get(field, "")
                sanitized_annotation[field] = self.sanitize_field_value(str(value))

            # Append to CSV file
            with open(self.filepath, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writerow(sanitized_annotation)

            return {"success": True, "message": "Annotation saved successfully"}

        except Exception as e:
            return {"success": False, "error": f"Failed to save annotation: {str(e)}"}

    def read_annotations(self) -> List[Dict[str, Any]]:
        try:
            if not self.filepath.exists():
                return []

            annotations = []
            with open(self.filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    annotations.append(dict(row))

            return annotations

        except Exception:
            return []

    def get_annotations_for_image(self, image_name: str) -> List[Dict[str, Any]]:
        all_annotations = self.read_annotations()
        return [ann for ann in all_annotations if ann["image_name"] == image_name]

    def sanitize_field_value(self, value: str) -> str:
        if not value:
            return ""
        
        # Remove control characters and normalize whitespace
        value = re.sub(r'[\r\n\t]', ' ', value)
        value = re.sub(r'\s+', ' ', value)
        value = value.strip()
        
        return value

    def delete_image_annotations(self, image_name: str) -> Dict[str, Any]:
        try:
            if not self.filepath.exists():
                return {"success": True, "message": "No annotations to delete"}
            
            # Read all annotations
            annotations = self.read_annotations()
            
            # Filter out annotations for the specified image
            filtered_annotations = [ann for ann in annotations if ann["image_name"] != image_name]
            
            # Write back to file
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                writer.writerows(filtered_annotations)
            
            deleted_count = len(annotations) - len(filtered_annotations)
            
            return {
                "success": True,
                "message": f"Deleted {deleted_count} annotation(s) for {image_name}",
                "deleted_count": deleted_count
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to delete annotations: {str(e)}"}

    def export_to_file(self, export_path: str) -> Dict[str, Any]:
        try:
            export_path_obj = Path(export_path)
            export_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the current CSV file to the export location
            shutil.copy2(self.filepath, export_path)
            
            return {
                "success": True,
                "message": f"Annotations exported to {export_path}",
                "export_path": export_path
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to export annotations: {str(e)}"}

    def get_statistics(self) -> Dict[str, Any]:
        try:
            annotations = self.read_annotations()
            
            if not annotations:
                return {
                    "total_annotations": 0,
                    "total_images": 0,
                    "most_common_tags": [],
                    "most_common_labels": []
                }

            # Count total annotations and unique images
            total_annotations = len(annotations)
            unique_images = len(set(ann["image_name"] for ann in annotations))

            # Analyze tags
            all_tags = []
            for ann in annotations:
                if ann["tags"]:
                    tags = [tag.strip() for tag in ann["tags"].split(",")]
                    all_tags.extend(tags)

            # Analyze labels
            all_labels = []
            for ann in annotations:
                if ann["labels"]:
                    labels = [label.strip() for label in ann["labels"].split(",")]
                    all_labels.extend(labels)

            # Get most common tags and labels
            tag_counter = Counter(all_tags)
            label_counter = Counter(all_labels)

            return {
                "total_annotations": total_annotations,
                "total_images": unique_images,
                "most_common_tags": tag_counter.most_common(10),
                "most_common_labels": label_counter.most_common(10)
            }

        except Exception as e:
            return {
                "total_annotations": 0,
                "total_images": 0,
                "most_common_tags": [],
                "most_common_labels": [],
                "error": str(e)
            }