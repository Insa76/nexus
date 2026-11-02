from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

# ======================================================
# CONFIG
# ======================================================

SECRET = "nexus-super-secret"  # 🔥 MISMO QUE ANTES
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# ======================================================
# PASSWORDS
# ======================================================

def hash_password(password: str) -> str:
    return pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd.verify(password, hashed)


# ======================================================
# JWT
# ======================================================

def create_token(data: dict) -> str:

    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)

    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:

    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None