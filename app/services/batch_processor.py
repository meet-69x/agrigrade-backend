import os
import uuid
from datetime import datetime

import cv2
from sqlalchemy.orm import Session

from app.config import settings
from app.models.batch import Batch, BatchStatus
from app.models.onion import Onion
from app.services.cv_pipeline import segment_onions
from app.services.defect_model import detect_defects
from app.services.grading import grade_onion, summarize_batch


def process_batch(batch_id: uuid.UUID, db: Session) -> None:
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        return

    try:
        batch.status = BatchStatus.processing
        db.commit()

        detections = segment_onions(batch.image_path)
        grades = []

        for det in detections:
            defect_tags, confidence = detect_defects(det["crop"])
            grade = grade_onion(
                size_mm=det["size_mm"],
                shape_score=det["shape_score"],
                color_uniformity=det["color_uniformity"],
                defect_tags=defect_tags,
            )
            grades.append(grade)

            onion = Onion(
                batch_id=batch.id,
                bbox=det["bbox"],
                size_mm=det["size_mm"],
                shape_score=det["shape_score"],
                color_uniformity=det["color_uniformity"],
                predicted_grade=grade,
                final_grade=grade,
                defect_tags=defect_tags,
                confidence=confidence,
            )
            db.add(onion)

        summary = summarize_batch(grades)
        batch.onion_count = len(grades)
        batch.avg_size_mm = (
            round(sum(d["size_mm"] for d in detections) / len(detections), 1)
            if detections else None
        )
        batch.overall_grade = summary["overall_grade"]
        batch.percent_defective = summary["percent_defective"]
        batch.status = BatchStatus.completed
        batch.completed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        batch.status = BatchStatus.failed
        db.commit()
        raise e


def save_upload(batch_id: uuid.UUID, file_bytes: bytes, filename: str) -> str:
    os.makedirs(settings.storage_dir, exist_ok=True)
    ext = os.path.splitext(filename)[1] or ".jpg"
    path = os.path.join(settings.storage_dir, f"{batch_id}{ext}")
    with open(path, "wb") as f:
        f.write(file_bytes)
    return path
