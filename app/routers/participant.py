from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.participant import ParticipantSubmitRequest, ParticipantResponse
from app.services.participant import submit_participant

router = APIRouter(
    prefix="/participants",
    tags=["Participants"]
)

@router.post("/submit", response_model=ParticipantResponse, status_code=status.HTTP_200_OK)
def submit(payload: ParticipantSubmitRequest, db: Session = Depends(get_db)):
    participant = submit_participant(db, payload)
    return participant