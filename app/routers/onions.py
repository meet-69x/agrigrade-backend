import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.onion import Onion
from app.models.user import User
from app.schemas.onion import OnionResponse, OverrideRequest
from app.auth.security import get_current_user

router = APIRouter(prefix="/onions", tags=["onions"])


@router.patch("/{onion_id}/override", response_model=OnionResponse)
def override_grade(
    onion_id: uuid.UUID,
    payload: OverrideRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lets a human grader correct the AI's grade. These corrections are the
    feedback loop for future model retraining - keep them logged, never
    silently overwrite the original prediction.
    """
    onion = db.query(Onion).filter(Onion.id == onion_id).first()
    if not onion:
        raise HTTPException(status_code=404, detail="Onion not found")

    onion.final_grade = payload.final_grade
    onion.override_reason = payload.override_reason
    onion.overridden_by = current_user.id
    onion.overridden_at = datetime.utcnow()
    db.commit()
    db.refresh(onion)
    return onion
