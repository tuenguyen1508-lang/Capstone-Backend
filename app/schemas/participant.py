from pydantic import BaseModel
from uuid import UUID
from datetime import date

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