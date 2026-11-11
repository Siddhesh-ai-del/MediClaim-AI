import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.entities import RefreshToken, UserAccount


def create_access_token(user: UserAccount, tenant_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "tenant_id": str(tenant_id),
        "role": user.role.value,
        "email": user.email,
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)).timestamp()
        ),
        "jti": str(uuid.uuid4()),
        "iss": "mediclaim-ai",
        "aud": "mediclaim-api",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=["HS256"],
        audience="mediclaim-api",
        issuer="mediclaim-ai",
    )


def create_refresh_token_value() -> str:
    return uuid.uuid4().hex + uuid.uuid4().hex


def hash_refresh_token(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode()).hexdigest()


async def issue_refresh_token(
    session: AsyncSession,
    user: UserAccount,
    user_agent: str | None = None,
    ip: str | None = None,
) -> str:
    value = create_refresh_token_value()
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(value),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_DAYS),
        user_agent=user_agent,
        ip_address=ip,
    )
    session.add(rt)
    await session.flush()
    return value


async def rotate_refresh_token(
    session: AsyncSession, old_value: str
) -> tuple[UserAccount, str] | None:
    from app.common.errors import Unauthorized

    h = hash_refresh_token(old_value)
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == h)
    )
    rt = result.scalar_one_or_none()
    if (
        rt is None
        or rt.revoked_at is not None
        or rt.expires_at < datetime.now(timezone.utc)
    ):
        # reuse detection: if revoked token presented, revoke all user tokens
        if rt is not None and rt.revoked_at is not None:
            await session.execute(
                RefreshToken.__table__.update()
                .where(RefreshToken.user_id == rt.user_id)
                .values(revoked_at=datetime.now(timezone.utc))
            )
        raise Unauthorized("invalid refresh token")
    # revoke old
    rt.revoked_at = datetime.now(timezone.utc)
    user_result = await session.execute(
        select(UserAccount).where(UserAccount.id == rt.user_id)
    )
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise Unauthorized("user inactive")
    new_value = await issue_refresh_token(
        session, user, rt.user_agent, str(rt.ip_address) if rt.ip_address else None
    )
    rt.replaced_by = None
    return user, new_value


async def revoke_refresh_token(session: AsyncSession, value: str) -> None:
    h = hash_refresh_token(value)
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == h)
    )
    rt = result.scalar_one_or_none()
    if rt is not None and rt.revoked_at is None:
        rt.revoked_at = datetime.now(timezone.utc)
