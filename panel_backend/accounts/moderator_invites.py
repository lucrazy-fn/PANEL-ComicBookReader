from __future__ import annotations

import hashlib
import secrets
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from panel_backend.accounts.models import ModeratorInvite, User, _now


def token_hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def generate(db: Session, creator: User, *, max_uses: int, valid_hours: int) -> tuple[ModeratorInvite, str]:
    raw_secret = "pnl_admin_" + secrets.token_urlsafe(32)
    invite = ModeratorInvite(
        token_hash=token_hash(raw_secret),
        created_by_user_id=creator.id,
        max_uses=max_uses,
        expires_at=_now() + timedelta(hours=valid_hours),
    )
    db.add(invite)
    db.flush()
    return invite, raw_secret


def consume(db: Session, raw_secret: str) -> ModeratorInvite | None:
    invite = db.scalar(
        select(ModeratorInvite).where(
            ModeratorInvite.token_hash == token_hash(raw_secret)
        )
    )
    if invite is None or not invite.is_usable():
        return None
    invite.use_count += 1
    db.flush()
    return invite
