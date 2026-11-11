import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.auth.jwt import (
    create_access_token,
    decode_access_token,
    issue_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token,
)
from app.auth.passwords import verify_password
from app.common.errors import Unauthorized
from app.db import get_session
from app.models.entities import UserAccount

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest, request: Request, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(UserAccount).where(UserAccount.email == body.email)
    )
    user = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if user is None or not user.is_active:
        raise Unauthorized("invalid credentials")
    if user.locked_until is not None and user.locked_until > now:
        raise Unauthorized("account locked")
    if not verify_password(body.password, user.password_hash):
        user.failed_login_count += 1
        if user.failed_login_count >= 5:
            user.locked_until = now.replace(microsecond=0)  # placeholder; set below
            from datetime import timedelta

            user.locked_until = now + timedelta(minutes=15)
        await session.flush()
        raise Unauthorized("invalid credentials")
    # success
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now
    tenant_id = user.tenant_id
    access = create_access_token(user, tenant_id)
    refresh = await issue_refresh_token(
        session,
        user,
        request.headers.get("user-agent"),
        request.client.host if request.client else None,
    )
    await session.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=900,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        user, new_refresh = await rotate_refresh_token(session, body.refresh_token)
    except Exception:
        raise Unauthorized("invalid refresh token")
    access = create_access_token(user, user.tenant_id)
    await session.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=900,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        },
    )


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, session: AsyncSession = Depends(get_session)):
    await revoke_refresh_token(session, body.refresh_token)
    await session.commit()
    return None


@router.get("/me")
async def me(user: UserAccount = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "tenant_id": str(user.tenant_id),
    }
