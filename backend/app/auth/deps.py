import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import Forbidden, Unauthorized
from app.db import get_session
from app.models.entities import UserAccount


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> UserAccount:
    user_id = getattr(request.state, "user_id", None)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not user_id or not tenant_id:
        raise HTTPException(status_code=401, detail="unauthorized")
    result = await session.execute(
        select(UserAccount).where(UserAccount.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise Unauthorized("user not found or inactive")
    if str(user.tenant_id) != str(tenant_id):
        raise Unauthorized("tenant mismatch")
    request.state.user = user
    return user


def require_role(*roles: str):
    async def checker(user: UserAccount = Depends(get_current_user)) -> UserAccount:
        allowed = set(roles)
        if "admin" in allowed and user.role.value == "admin":
            return user
        if "manager" in allowed and user.role.value in ("manager", "admin"):
            return user
        if user.role.value in allowed:
            return user
        raise Forbidden("insufficient role")

    return checker


def tenant_id_from_request(request: Request) -> str:
    tid = getattr(request.state, "tenant_id", None)
    if not tid:
        raise Unauthorized("missing tenant")
    return tid
