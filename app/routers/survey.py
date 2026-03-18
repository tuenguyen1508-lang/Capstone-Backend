from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.survey import (
    SurveyCreateRequest,
    SurveyCreateResponse,
    SurveyShowByTokenResponse,
    GenerateTokenResponse,
)


#e them cai nay
from app.services.auth import get_current_user
from app.services.survey import (
    create_survey,
    get_survey_by_token_show,
    get_survey_detail_by_id,
    get_surveys_by_current_user,
    generate_survey_token,
)

router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"],
)


@router.post("", response_model=SurveyCreateResponse, status_code=status.HTTP_201_CREATED)
def create(payload: SurveyCreateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    survey = create_survey(db=db, payload=payload, current_user=current_user)
    return survey


@router.get("", response_model=List[SurveyCreateResponse])
def get_my_surveys(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    surveys = get_surveys_by_current_user(db=db, current_user=current_user)
    return surveys


@router.get("/{survey_id}", response_model=SurveyCreateResponse)
def get_survey_detail(survey_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    survey = get_survey_detail_by_id(db=db, survey_id=survey_id, current_user=current_user)
    return survey

#them cai nay nua a
@router.post("/{survey_id}/token", response_model=GenerateTokenResponse, status_code=status.HTTP_201_CREATED)
def generate_token(
    survey_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    survey = generate_survey_token(db=db, survey_id=survey_id, current_user=current_user)
    return survey


@router.get("/{token}/show", response_model=SurveyShowByTokenResponse)
def show_by_token(token: str, db: Session = Depends(get_db)):
    survey = get_survey_by_token_show(db=db, token=token)
    return survey

