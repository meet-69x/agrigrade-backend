from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.centre import Centre
from app.models.user import User
from app.schemas.centre import CentreCreate, CentreResponse
from app.auth.security import get_current_user

router = APIRouter(prefix="/centres", tags=["centres"])


@router.post("", response_model=CentreResponse)
def create_centre(payload: CentreCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    centre = Centre(name=payload.name, location=payload.location)
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.get("", response_model=list[CentreResponse])
def list_centres(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Centre).order_by(Centre.name).all()
