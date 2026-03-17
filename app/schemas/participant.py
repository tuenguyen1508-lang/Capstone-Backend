from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional

class ParticipantSubmitRequest(BaseModel):
    survey_id: UUID
    code: str
    name: str
    school: str
    grade: str
    dob: date


class ParticipantResponse(BaseModel):
    id: UUID
    survey_id: UUID
    code: str
    name: str
    school: str
    grade: str
    dob: date

    class Config:
        from_attributes = True


class AttemptResponse(BaseModel):
    id: UUID
    survey_id: UUID
    participant_id: UUID
    status: str
    completion_percentage: float

    class Config:
        from_attributes = True


class ParticipantSubmitStartResponse(BaseModel):
    participant: ParticipantResponse
    attempt: AttemptResponse


class ParticipantAnswerSubmitRequest(BaseModel):
    question_id: UUID
    selected_option_id: Optional[UUID] = None
    user_angle: Optional[float] = None


class ParticipantAnswerSubmitResponse(BaseModel):
    attempt_id: UUID
    answer_id: UUID
    completion_percentage: float
    answered_count: int
    total_questions: int
    status: str


class AttemptDoneResponse(BaseModel):
    attempt_id: UUID
    completion_percentage: float
    answered_count: int
    total_questions: int
    status: str