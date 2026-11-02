from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid

from auth.security import create_token
from auth.service import authenticate, create_user
from auth.deps import require_admin, get_current_user
from core.database import get_connection
from audit.service import log_event

router = APIRouter(prefix="/auth", tags=["auth"])


# =========================
# REGISTER (MULTI-TENANT REAL)
# =========================
@router.post("/register")
def register(data: dict):

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(400, "Username y password requeridos")

    tenant_id = str(uuid.uuid4())

    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Crear tenant
        cur.execute("""
            INSERT INTO tenants (id, name, created_at)
            VALUES (%s, %s, %s)
        """, (
            tenant_id,
            username,
            datetime.utcnow()
        ))

        # 2️⃣ Crear usuario admin del tenant
        create_user(
            username=username,
            password=password,
            role="admin",
            tenant_id=tenant_id,
            workspace_id="main"
        )

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(400, f"Error creando usuario: {str(e)}")

    finally:
        conn.close()

    return {
        "ok": True,
        "tenant_id": tenant_id
    }


# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: dict):

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(400, "Username y password requeridos")

    user = authenticate(username, password)

    if not user:
        raise HTTPException(401, "Credenciales inválidas")

    token = create_token({
        "sub": user["id"],
        "username": user["username"],
        "role": user["role"],
        "tenant_id": user["tenant_id"],
        "workspace_id": user["workspace_id"]
    })

    # audit seguro
    try:
        log_event(
            user,
            action="login",
            entity="user",
            entity_id=user["id"]
        )
    except Exception:
        pass

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"],
            "tenant_id": user["tenant_id"],
            "workspace_id": user["workspace_id"]
        }
    }


# =========================
# LIST USERS (ADMIN SOLO SU TENANT)
# =========================
@router.get("/users")
def list_users(admin=Depends(require_admin)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, role
        FROM users
        WHERE tenant_id = %s
    """, (admin["tenant_id"],))

    users = cur.fetchall()
    conn.close()

    return [dict(u) for u in users]


# =========================
# CREATE USER (ADMIN DEL MISMO TENANT)
# =========================
@router.post("/users")
def create_user_admin(data: dict, admin=Depends(require_admin)):

    create_user(
        username=data["username"],
        password=data["password"],
        role=data.get("role", "user"),
        tenant_id=admin["tenant_id"],
        workspace_id=admin["workspace_id"]
    )

    return {"ok": True}


# =========================
# DELETE USER (MISMO TENANT)
# =========================
@router.delete("/users/{username}")
def delete_user(username: str, admin=Depends(require_admin)):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM users
        WHERE username = %s
        AND tenant_id = %s
    """, (username, admin["tenant_id"]))

    conn.commit()
    conn.close()

    return {"ok": True}


# =========================
# CURRENT USER
# =========================
@router.get("/me")
def me(user=Depends(get_current_user)):
    return user