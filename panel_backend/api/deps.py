"""
Dependências injetadas nas rotas via FastAPI Depends(). Centralizar aqui
evita cada rota reimplementar "como pegar uma sessão de banco" ou "como
validar o token" do próprio jeito.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from panel_backend.accounts import service as accounts
from panel_backend.accounts.models import User
from panel_backend.db import get_session
from panel_backend.moderation.service import ModerationService
from panel_backend.moderation.storage import SqlAlchemyModerationStore


def get_db():
    with get_session() as session:
        yield session


def get_moderation_service(db: Session = Depends(get_db)) -> ModerationService:
    # A mesma sessão é reutilizada pelo FastAPI na requisição. Isso coloca
    # Comic, decisão de moderação e Publication na mesma transação.
    return ModerationService(store=SqlAlchemyModerationStore(db))


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Uso: `user: User = Depends(get_current_user)` em qualquer rota.
    O FastAPI resolve get_db() automaticamente por baixo — não precisa
    passar db manualmente.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou inválido.")
    token = authorization.removeprefix("Bearer ").strip()

    user = accounts.get_user_by_token(db, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Sessão expirada ou inválida.")
    return user


def require_moderator(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"moderator", "admin", "owner"} and not user.is_moderator:
        raise HTTPException(status_code=403, detail="Acesso exclusivo para moderadores.")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin", "owner"}:
        raise HTTPException(status_code=403, detail="Acesso exclusivo para administradores.")
    return user
