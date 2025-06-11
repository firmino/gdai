from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Annotated
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = "REPLACE_ME_WITH_A_SECURE_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()

# --- Schemas ---
class LoginSchema(BaseModel):
    username: str
    password: str

class RegisterSchema(BaseModel):
    username: str
    password: str
    tenant_id: str
    role: str = "user"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# --- Mock DB (substitua por integração real) ---
mock_users_db = {}

# --- Utils ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def get_token(token: str = Depends(oauth2_scheme)):
    return token

def get_current_user_payload(token: str = Depends(get_token)):
    payload = decode_token(token)
    if payload.get("type") == "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type for this endpoint")
    return payload

# --- Rotas ---
@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginSchema):
    user = mock_users_db.get(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"], "tenant_id": user["tenant_id"], "role": user["role"]})
    refresh_token = create_refresh_token({"sub": user["username"]})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/logout")
def logout(token: Annotated[str, Depends(get_token)]):
    # Em JWT puro, logout é feito no client. Para blacklist, implemente um store de tokens inválidos.
    return {"msg": "Logout efetuado (stateless JWT, apenas remova o token do client)"}

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str):
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    username = payload.get("sub")
    user = mock_users_db.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token = create_access_token({"sub": user["username"], "tenant_id": user["tenant_id"], "role": user["role"]})
    new_refresh_token = create_refresh_token({"sub": user["username"]})
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)

@router.post("/register")
def register(user_data: RegisterSchema):
    if user_data.username in mock_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    mock_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": hash_password(user_data.password),
        "tenant_id": user_data.tenant_id,
        "role": user_data.role,
    }
    return {"msg": "User registered successfully"}

# --- Anotação para validar token e extrair payload ---
def require_jwt_user():
    def dependency(payload=Depends(get_current_user_payload)):
        return payload
    return dependency

# Exemplo de uso:
# @router.get("/protected")
# def protected_route(user_payload=Depends(require_jwt_user())):
#     return {"user": user_payload}
