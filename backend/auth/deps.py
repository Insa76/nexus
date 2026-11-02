from fastapi import Header, HTTPException, Depends
from jose import JWTError

from auth.security import decode_token


def get_current_user(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Token requerido")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token inválido")

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
def require_admin(user=Depends(get_current_user)):

    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return user    
    
def get_current_tenant(user=Depends(get_current_user)):
    return user["tenant_id"]    
