import uuid
from datetime import datetime
from auth.security import decode_token
from passlib.context import CryptContext

from core.database import get_connection
from auth.security import create_token  # 🔥 ÚNICO JWT

# ======================================================
# PASSWORD
# ======================================================

pwd = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd.hash(password)


def verify_password(password: str, hashed: str):
    return pwd.verify(password, hashed)


# ======================================================
# USERS
# ======================================================

def create_user(
    username,
    password,
    role="user",
    tenant_id="default",
    workspace_id="main"
):

    conn = get_connection()
    cur = conn.cursor()

    user_id = str(uuid.uuid4())

    try:
        cur.execute("""
        INSERT INTO users
        (id, username, password_hash, role, tenant_id, workspace_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            username,
            hash_password(password),
            role,
            tenant_id,
            workspace_id,
            datetime.utcnow()
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


def get_user(username):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM users
        WHERE username = %s
    """, (username,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return dict(row)


def authenticate(username, password):

    user = get_user(username)

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


# ======================================================
# LOGIN (GENERA TOKEN)
# ======================================================

def login_user(user: dict):

    return create_token({
        "sub": user["id"],
        "username": user["username"],
        "role": user["role"],
        "tenant_id": user["tenant_id"],
        "workspace_id": user["workspace_id"]
    })