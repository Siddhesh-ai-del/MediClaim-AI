import uuid
import secrets

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, require_role
from app.auth.passwords import hash_password, validate_password_policy
from app.common.errors import UserNotFound
from app.db import get_session
from app.models.entities import UserAccount

router = APIRouter(prefix="/admin", tags=["admin"])


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "officer"
    password: str | None = None


@router.get("/users")
async def list_users(
    user=Depends(require_role("admin")), session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(UserAccount).where(UserAccount.tenant_id == user.tenant_id)
    )
    users = list(result.scalars().all())
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value,
            "is_active": u.is_active,
        }
        for u in users
    ]


@router.post("/users", status_code=201)
async def create_user(
    body: UserCreate,
    user=Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    pwd = body.password or secrets.token_urlsafe(12)
    if not validate_password_policy(pwd):
        pwd = secrets.token_urlsafe(12) + "A1"
    nu = UserAccount(
        tenant_id=user.tenant_id,
        email=body.email,
        password_hash=hash_password(pwd),
        full_name=body.full_name,
        role=body.role,
    )
    session.add(nu)
    await session.commit()
    await session.refresh(nu)
    return {
        "id": str(nu.id),
        "email": nu.email,
        "role": nu.role.value,
        "temp_password": pwd if not body.password else None,
    }


@router.patch("/users/{user_id}")
async def update_user(
    user_id: uuid.UUID,
    role: str | None = None,
    is_active: bool | None = None,
    user=Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(UserAccount).where(
            UserAccount.id == user_id, UserAccount.tenant_id == user.tenant_id
        )
    )
    u = result.scalar_one_or_none()
    if u is None:
        raise UserNotFound("user not found")
    if role is not None:
        u.role = role
    if is_active is not None:
        u.is_active = is_active
    await session.commit()
    return {"status": "ok"}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    user=Depends(require_role("admin")),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(UserAccount).where(
            UserAccount.id == user_id, UserAccount.tenant_id == user.tenant_id
        )
    )
    u = result.scalar_one_or_none()
    if u is None:
        raise UserNotFound("user not found")
    u.is_active = False
    await session.commit()
    return None


@router.get("/usage")
async def usage(
    user=Depends(require_role("admin")), session: AsyncSession = Depends(get_session)
):
    from sqlalchemy import func

    from app.models.entities import Claim

    c = await session.execute(
        select(func.count(Claim.id)).where(Claim.tenant_id == user.tenant_id)
    )
    return {"users": 0, "claims": c.scalar_one()}


@router.post("/demo/reset")
async def demo_reset(
    user=Depends(require_role("admin")), session: AsyncSession = Depends(get_session)
):
    from app.config import settings

    if not settings.DEMO_MODE or settings.APP_ENV == "production":
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="not found")
    # purge synthetic claims
    from sqlalchemy import delete

    from app.models.entities import Claim

    await session.execute(delete(Claim).where(Claim.tenant_id == user.tenant_id))
    await session.commit()
    return {"status": "reset"}
