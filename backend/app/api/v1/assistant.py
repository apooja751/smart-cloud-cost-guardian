from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.aws_account import AWSAccount
from app.schemas import AssistantQuestionRequest, AssistantAnswerResponse
from app.schemas.common import StandardResponse
from app.services.assistant.context import gather_finops_context
from app.services.assistant.llm_service import ask_finops_assistant
from app.api.deps import get_current_user

router = APIRouter(prefix='/assistant', tags=['AI FinOps Assistant'])

@router.post('/ask', response_model=StandardResponse[AssistantAnswerResponse])
def ask_assistant(
    req: AssistantQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    acc = db.query(AWSAccount).filter(AWSAccount.user_id == current_user.id)
    if req.aws_account_id:
        acc = acc.filter(AWSAccount.id == req.aws_account_id)
    account = acc.first()

    if not account:
        raise HTTPException(status_code=404, detail='No AWS account connected to analyze')

    context = gather_finops_context(db, account.id)
    result = ask_finops_assistant(req.question, context)
    return StandardResponse(data=AssistantAnswerResponse(**result), message='AI response generated')
