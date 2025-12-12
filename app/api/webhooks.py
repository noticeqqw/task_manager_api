from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps_auth import get_current_user
from app.db.deps import get_db
from app.schemas.webhook import WebhookCreate, WebhookRead
from app.services.webhook_service import create_webhook, get_user_webhooks
from app.models.user import User

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/", response_model=WebhookRead)
def create(
    data: WebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return create_webhook(db, user.id, data)


@router.get("/", response_model=list[WebhookRead])
def list_webhooks(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_user_webhooks(db, user.id)
