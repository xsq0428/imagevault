from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import (
    CAPTCHA_COOKIE,
    CAPTCHA_MAX_AGE,
    SESSION_COOKIE,
    clear_session_cookie,
    consume_captcha,
    create_session,
    generate_captcha,
    hash_password,
    require_admin,
    set_session_cookie,
    store_captcha,
    verify_password,
)
from ..database import get_db
from ..models import AdminSession, AdminUser
from ..schemas import AccountUpdate, AdminOut, LoginIn

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])


def serialize(user: AdminUser) -> AdminOut:
    return AdminOut(id=user.id, username=user.username)


@router.get("/captcha")
def captcha() -> Response:
    answer, png = generate_captcha()
    captcha_id = store_captcha(answer)
    response = Response(content=png, media_type="image/png")
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(
        CAPTCHA_COOKIE,
        captcha_id,
        max_age=CAPTCHA_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/api/admin",
    )
    return response


@router.post("/login", response_model=AdminOut)
def login(
    payload: LoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AdminOut:
    if not consume_captcha(request.cookies.get(CAPTCHA_COOKIE), payload.captcha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="验证码错误或已过期"
        )

    user = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误"
        )

    token = create_session(db, user)
    set_session_cookie(response, token)
    response.delete_cookie(CAPTCHA_COOKIE, path="/api/admin")
    return serialize(user)


@router.post("/logout")
def logout(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        session = db.scalar(select(AdminSession).where(AdminSession.token == token))
        if session is not None:
            db.delete(session)
            db.commit()
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=AdminOut)
def me(user: AdminUser = Depends(require_admin)) -> AdminOut:
    return serialize(user)


@router.patch("/account", response_model=AdminOut)
def update_account(
    payload: AccountUpdate,
    user: AdminUser = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminOut:
    if payload.new_password is not None:
        if not payload.current_password or not verify_password(
            payload.current_password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="当前密码不正确"
            )
        user.password_hash = hash_password(payload.new_password)

    if payload.username is not None:
        username = payload.username.strip()
        duplicate = db.scalar(
            select(AdminUser).where(AdminUser.username == username, AdminUser.id != user.id)
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在"
            )
        user.username = username

    db.commit()
    db.refresh(user)
    return serialize(user)
