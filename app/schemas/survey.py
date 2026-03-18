from pydantic import BaseModel


class SurveyDeleteResponse(BaseModel):
    status: bool
    message: str