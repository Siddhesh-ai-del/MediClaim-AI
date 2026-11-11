from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(
    schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def validate_password_policy(password: str) -> bool:
    if len(password) < 10:
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c.isalpha() for c in password):
        return False
    return True
