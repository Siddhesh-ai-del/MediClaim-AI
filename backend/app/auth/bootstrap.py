import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.passwords import hash_password, validate_password_policy
from app.config import settings
from app.models.entities import Tenant, UserAccount


async def bootstrap(session: AsyncSession) -> None:
    # tenant
    result = await session.execute(select(Tenant).where(Tenant.slug == "demo"))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(id=uuid.uuid4(), name="Demo Tenant", slug="demo")
        session.add(tenant)
        await session.flush()

    # admin
    result = await session.execute(
        select(UserAccount).where(
            UserAccount.tenant_id == tenant.id, UserAccount.role == "admin"
        )
    )
    admin = result.scalars().first()
    if admin is None:
        password = settings.ADMIN_PASSWORD
        if not password:
            password = secrets.token_urlsafe(16)
            print(
                f"[bootstrap] Generated admin password (change on first login): {password}",
                flush=True,
            )
        if not validate_password_policy(password):
            raise ValueError("ADMIN_PASSWORD does not meet policy")
        admin = UserAccount(
            tenant_id=tenant.id,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(password),
            full_name="Demo Admin",
            role="admin",
        )
        session.add(admin)

    if settings.DEMO_MODE and settings.APP_ENV != "production":
        for email, role, name in [
            ("officer@demo.med", "officer", "Demo Officer"),
            ("manager@demo.med", "manager", "Demo Manager"),
        ]:
            r = await session.execute(
                select(UserAccount).where(
                    UserAccount.tenant_id == tenant.id, UserAccount.email == email
                )
            )
            if r.scalar_one_or_none() is None:
                session.add(
                    UserAccount(
                        tenant_id=tenant.id,
                        email=email,
                        password_hash=hash_password("DemoPass123!"),
                        full_name=name,
                        role=role,
                    )
                )

    await session.commit()
