from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.survey import Survey, Participant
from app.schemas.participant import ParticipantSubmitRequest


def get_participant_by_survey_and_code(db: Session, survey_id, code: str):
    return (
        db.query(Participant)
        .filter(
            Participant.survey_id == survey_id,
            Participant.code == code
        )
        .first()
    )


def submit_participant(db: Session, payload: ParticipantSubmitRequest):
    survey = db.query(Survey).filter(Survey.id == payload.survey_id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    participant = get_participant_by_survey_and_code(db, payload.survey_id, payload.code)

    if participant:
        participant.name = payload.name
        participant.school = payload.school
        participant.grade = payload.grade
        participant.dob = payload.dob
    else:
        participant = Participant(
            survey_id=payload.survey_id,
            code=payload.code,
            name=payload.name,
            school=payload.school,
            grade=payload.grade,
            dob=payload.dob
        )
        db.add(participant)

    db.commit()
    db.refresh(participant)
    return participant