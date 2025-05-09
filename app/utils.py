import hashlib
import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status
from jose import JWTError, jwt
from typing import Optional

# 🔐 Hash a plain password using SHA-256
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# 🔐 Verify that the given plain password matches the hashed one
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Try bcrypt first
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to SHA-256 for legacy users
        sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        if sha256_hash == hashed_password:
            return True
        # Fallback to plain text (for initial dev only)
        return plain_password == hashed_password

# 🔑 Generate a secure random session token
def generate_token(length: int = 32) -> str:
    return secrets.token_hex(length)

# ⏰ Return a UTC expiry datetime (default: 60 minutes from now)
def get_expiry_time(minutes: int = 60) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)

# 🧾 Format a log entry for user activity
def format_log(user: str, action: str) -> str:
    return f"[{datetime.utcnow()}] User: {user} - Action: {action}"

# 📧 Simple email format checker
def is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
