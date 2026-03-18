from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.survey import SurveyDeleteResponse
from app.services.survey import delete_survey

router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"]
)


@router.delete("/{id}", response_model=SurveyDeleteResponse, status_code=status.HTTP_200_OK)
def remove_survey(id: UUID, db: Session = Depends(get_db)):
    return delete_survey(db, id)