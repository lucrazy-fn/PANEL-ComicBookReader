from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from panel_backend.accounts.models import LibraryState, Notification, SessionToken, User, _now
from panel_backend.accounts.security import hash_password, verify_password
from panel_backend.accounts.security import new_totp_secret, verify_totp
from panel_backend.api.deps import get_current_user, get_db
from panel_backend.api.schemas import (LibraryStateItem, LibrarySyncRequest,
    NotificationPublic, PasswordChange, ProfileUpdate, TotpConfirm, UserPublic)

router = APIRouter(prefix="/account", tags=["account"])

@router.get("/profile")
def get_profile(user: User=Depends(get_current_user)):
    return {"username":user.username,"display_name":user.display_name or user.username,
        "email":user.email,"role":user.role}

@router.patch("/profile", response_model=UserPublic)
def profile(body: ProfileUpdate, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    email=body.email.strip().lower() if body.email else None
    if email and db.scalar(select(User).where(User.email==email, User.id!=user.id)):
        raise HTTPException(409,"Este e-mail já está cadastrado.")
    user.display_name=body.display_name.strip(); user.email=email; db.flush()
    return UserPublic(id=user.id,username=user.username,display_name=user.display_name,
        is_moderator=user.is_moderator,role=user.role)

@router.post("/password", status_code=204)
def change_password(body:PasswordChange,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if not verify_password(body.current_password,user.password_hash,user.password_salt):
        raise HTTPException(400,"A senha atual está incorreta.")
    user.password_hash,user.password_salt=hash_password(body.new_password)
    for session in db.scalars(select(SessionToken).where(SessionToken.user_id==user.id)).all(): db.delete(session)
    db.flush()

@router.post("/2fa/setup")
def setup_2fa(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if user.role not in {"admin","owner"}: raise HTTPException(403,"2FA obrigatório apenas para Administrador e Dono.")
    user.totp_secret=new_totp_secret();user.totp_enabled=False;db.flush()
    return {"secret":user.totp_secret,"otpauth_url":f"otpauth://totp/PANEL:{user.username}?secret={user.totp_secret}&issuer=PANEL"}

@router.post("/2fa/confirm",status_code=204)
def confirm_2fa(body:TotpConfirm,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if not user.totp_secret or not verify_totp(user.totp_secret,body.code): raise HTTPException(400,"Código inválido.")
    user.totp_enabled=True;db.flush()

@router.get("/notifications", response_model=list[NotificationPublic])
def notifications(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    return db.scalars(select(Notification).where(Notification.user_id==user.id)
        .order_by(Notification.created_at.desc()).limit(100)).all()

@router.post("/notifications/{notification_id}/read", status_code=204)
def read_notification(notification_id: str,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    item=db.get(Notification,notification_id)
    if not item or item.user_id!=user.id: raise HTTPException(404,"Notificação não encontrada.")
    item.read_at=_now(); db.flush()

@router.get("/library-state", response_model=list[LibraryStateItem])
def get_state(user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    return [LibraryStateItem(item_key=x.item_key,page=x.page,favorite=x.favorite,
            client_updated_at=float(x.client_updated_at or 0))
        for x in db.scalars(select(LibraryState).where(LibraryState.user_id==user.id)).all()]

@router.put("/library-state", response_model=list[LibraryStateItem])
def sync_state(body: LibrarySyncRequest,user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    existing={x.item_key:x for x in db.scalars(select(LibraryState).where(LibraryState.user_id==user.id)).all()}
    for incoming in body.items:
        row=existing.get(incoming.item_key)
        if row is None:
            row=LibraryState(user_id=user.id,item_key=incoming.item_key); db.add(row); existing[incoming.item_key]=row
        incoming_stamp = float(incoming.client_updated_at or 0)
        if (row.client_updated_at or 0) <= incoming_stamp:
            row.page=incoming.page; row.favorite=incoming.favorite
            row.client_updated_at=incoming_stamp; row.updated_at=_now()
    db.flush()
    return [LibraryStateItem(item_key=x.item_key,page=x.page,favorite=x.favorite,
            client_updated_at=float(x.client_updated_at or 0)) for x in existing.values()]
