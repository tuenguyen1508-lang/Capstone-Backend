from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.survey import Answer, Attempt, Participant, Question, QuestionOption, Survey
from app.schemas.participant import ParticipantAnswerSubmitRequest, ParticipantSubmitRequest


def get_participant_by_survey_and_code(db: Session, survey_id, code: str):
    return (
        db.query(Participant)
        .filter(
            Participant.survey_id == survey_id,
            Participant.code == code
        )
        .first()
    )


def _get_survey_or_404(db: Session, survey_id: UUID):
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found",
        )
    return survey


def _ensure_survey_active(survey: Survey):
    if survey.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey is not active",
        )


def _ensure_survey_answer_window_open(survey: Survey):
    now = datetime.utcnow()
    if survey.start_time and now < survey.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey has not started yet",
        )
    if survey.end_time and now > survey.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey has expired",
        )


def _get_attempt_or_404(db: Session, attempt_id: UUID):
    attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attempt not found",
        )
    return attempt


def _get_visible_question_or_404(db: Session, survey_id: UUID, question_id: UUID):
    question = (
        db.query(Question)
        .filter(
            Question.id == question_id,
            Question.survey_id == survey_id,
            Question.is_visible.is_(True),
        )
        .first()
    )
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found or not visible",
        )
    return question


def _validate_payload_for_question_type(question: Question, payload: ParticipantAnswerSubmitRequest):
    if question.type == "mcq":
        if payload.selected_option_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selected_option_id is required for mcq question",
            )
        if payload.user_angle is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_angle must be null for mcq question",
            )

    elif question.type == "arrow":
        if payload.user_angle is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_angle is required for arrow question",
            )
        if payload.selected_option_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="selected_option_id must be null for arrow question",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported question type",
        )


def _validate_option_belongs_to_question(db: Session, question: Question, selected_option_id: UUID):
    option = (
        db.query(QuestionOption)
        .filter(
            QuestionOption.id == selected_option_id,
            QuestionOption.question_id == question.id,
        )
        .first()
    )
    if not option:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selected_option_id does not belong to the question",
        )


def _upsert_answer(db: Session, attempt_id: UUID, payload: ParticipantAnswerSubmitRequest):
    answer = (
        db.query(Answer)
        .filter(
            Answer.attempt_id == attempt_id,
            Answer.question_id == payload.question_id,
        )
        .first()
    )

    if answer:
        answer.selected_option_id = payload.selected_option_id
        answer.user_angle = payload.user_angle
        return answer

    answer = Answer(
        attempt_id=attempt_id,
        question_id=payload.question_id,
        selected_option_id=payload.selected_option_id,
        user_angle=payload.user_angle,
    )
    db.add(answer)
    db.flush()
    return answer


def _calculate_attempt_progress(db: Session, attempt_id: UUID, survey_id: UUID):
    total_questions = (
        db.query(func.count(Question.id))
        .filter(
            Question.survey_id == survey_id,
            Question.is_visible.is_(True),
        )
        .scalar()
    ) or 0

    answered_count = (
        db.query(func.count(func.distinct(Answer.question_id)))
        .join(Question, Question.id == Answer.question_id)
        .filter(
            Answer.attempt_id == attempt_id,
            Question.survey_id == survey_id,
            Question.is_visible.is_(True),
        )
        .scalar()
    ) or 0

    completion_percentage = round((answered_count / total_questions) * 100, 2) if total_questions > 0 else 0.0
    return answered_count, total_questions, completion_percentage


def submit_participant(db: Session, payload: ParticipantSubmitRequest):
    survey = _get_survey_or_404(db, payload.survey_id)
    _ensure_survey_active(survey)

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
            dob=payload.dob,
        )
        db.add(participant)
        db.flush()

    attempt = Attempt(
        survey_id=payload.survey_id,
        participant_id=participant.id,
        start_time=datetime.utcnow(),
        status="in_progress",
        completion_percentage=0,
    )
    db.add(attempt)

    db.commit()
    db.refresh(participant)
    db.refresh(attempt)
    return {
        "participant": participant,
        "attempt": attempt,
    }


def submit_answer_one(db: Session, attempt_id: UUID, payload: ParticipantAnswerSubmitRequest):
    attempt = _get_attempt_or_404(db, attempt_id)
    if attempt.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attempt is already completed",
        )

    survey = _get_survey_or_404(db, attempt.survey_id)
    _ensure_survey_active(survey)
    _ensure_survey_answer_window_open(survey)

    question = _get_visible_question_or_404(db, survey.id, payload.question_id)
    _validate_payload_for_question_type(question, payload)

    if payload.selected_option_id is not None:
        _validate_option_belongs_to_question(db, question, payload.selected_option_id)

    answer = _upsert_answer(db, attempt.id, payload)
    answered_count, total_questions, completion_percentage = _calculate_attempt_progress(db, attempt.id, survey.id)

    attempt.completion_percentage = completion_percentage
    if attempt.status == "pending":
        attempt.status = "in_progress"

    db.commit()
    db.refresh(attempt)
    db.refresh(answer)

    return {
        "attempt_id": attempt.id,
        "answer_id": answer.id,
        "completion_percentage": attempt.completion_percentage,
        "answered_count": answered_count,
        "total_questions": total_questions,
        "status": attempt.status,
    }


def done_attempt(db: Session, attempt_id: UUID):
    attempt = _get_attempt_or_404(db, attempt_id)
    survey = _get_survey_or_404(db, attempt.survey_id)

    answered_count, total_questions, completion_percentage = _calculate_attempt_progress(db, attempt.id, survey.id)
    attempt.completion_percentage = completion_percentage
    attempt.status = "completed"
    if attempt.end_time is None:
        attempt.end_time = datetime.utcnow()

    db.commit()
    db.refresh(attempt)

    return {
        "attempt_id": attempt.id,
        "completion_percentage": attempt.completion_percentage,
        "answered_count": answered_count,
        "total_questions": total_questions,
        "status": attempt.status,
    }