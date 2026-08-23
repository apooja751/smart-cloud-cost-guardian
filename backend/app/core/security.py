import datetime
from datetime import timezone
from typing import Any, Dict, Optional, Union
import jwt
import bcrypt
from cryptography.fernet import Fernet
from app.core.config import settings

# Key derivation / Fernet instance for encrypting connection credentials
try:
    _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
except Exception:
    # Fallback to deterministic valid 32-byte key if custom key is invalid
    import base64, hashlib
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.JWT_SECRET.encode()).digest())
    _fernet = Fernet(key)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: Union[str, Any], role: str = 'USER', expires_delta: Optional[datetime.timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        'exp': expire,
        'sub': str(subject),
        'role': role,
        'iat': datetime.datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None

def encrypt_secret(secret_text: str) -> str:
    if not secret_text:
        return ''
    return _fernet.encrypt(secret_text.encode('utf-8')).decode('utf-8')

def decrypt_secret(encrypted_text: str) -> str:
    if not encrypted_text:
        return ''
    try:
        return _fernet.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return ''
