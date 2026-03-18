from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.survey import Survey


def delete_survey(db: Session, survey_id: UUID):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    if survey.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending surveys can be deleted"
        )

    db.delete(survey)
    db.commit()

    return {
        "status": True,
        "message": "Survey deleted successfully"
    }