import uuid
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.database import get_db
from app.models.batch import Batch, BatchStatus
from app.models.user import User
from app.schemas.batch import BatchSummary, BatchDetail
from app.auth.security import get_current_user
from app.services.batch_processor import save_upload, process_batch

router = APIRouter(prefix="/batches", tags=["batches"])


@router.post("", response_model=BatchDetail)
async def create_batch(
    centre_id: uuid.UUID = Form(...),
    label: str | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a batch and immediately process the uploaded image:
    segmentation -> feature extraction -> defect detection -> grading.
    Processing is synchronous here for simplicity; move to a background
    task/queue (Celery/RQ) if images are large or volume is high.
    """
    batch = Batch(
        centre_id=centre_id,
        operator_id=current_user.id,
        label=label,
        status=BatchStatus.pending,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    file_bytes = await image.read()
    image_path = save_upload(batch.id, file_bytes, image.filename)
    batch.image_path = image_path
    db.commit()

    try:
        process_batch(batch.id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    db.refresh(batch)
    return batch


@router.get("", response_model=list[BatchSummary])
def list_batches(
    centre_id: uuid.UUID | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Batch)
    if centre_id:
        query = query.filter(Batch.centre_id == centre_id)
    if from_date:
        query = query.filter(Batch.created_at >= from_date)
    if to_date:
        query = query.filter(Batch.created_at <= to_date)
    return query.order_by(Batch.created_at.desc()).all()


@router.get("/{batch_id}", response_model=BatchDetail)
def get_batch(batch_id: uuid.UUID, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.get("/{batch_id}/image")
def get_batch_image(batch_id: uuid.UUID, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch or not batch.image_path:
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(batch.image_path)


@router.get("/{batch_id}/report")
def get_batch_report(batch_id: uuid.UUID, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 60, "AgriGrade AI - Batch Quality Report")

    p.setFont("Helvetica", 11)
    y = height - 100
    lines = [
        f"Batch ID: {batch.id}",
        f"Label: {batch.label or '-'}",
        f"Created: {batch.created_at}",
        f"Onion count: {batch.onion_count}",
        f"Average size: {batch.avg_size_mm} mm",
        f"Overall grade: {batch.overall_grade}",
        f"Percent defective: {batch.percent_defective}%",
        "",
        "Per-onion breakdown:",
    ]
    for line in lines:
        p.drawString(50, y, line)
        y -= 18

    for onion in batch.onions:
        if y < 60:
            p.showPage()
            y = height - 60
        text = (
            f"  Size {onion.size_mm}mm | Grade {onion.final_grade} | "
            f"Defects: {', '.join(onion.defect_tags) if onion.defect_tags else 'none'} | "
            f"Confidence {onion.confidence}"
        )
        p.drawString(50, y, text)
        y -= 16

    p.save()
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=batch_{batch.id}_report.pdf"},
    )
