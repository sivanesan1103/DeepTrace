from datetime import datetime, timedelta
from typing import Optional, Any
from passlib.context import CryptContext
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(
    subject: str,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[dict[str, Any]] = None,
) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)
    
    to_encode = {"sub": str(subject)}
    if extra_data:
        to_encode.update(extra_data)
    
    expire = datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.utcnow()
    
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def verify_token(token: str, secret_key: str, algorithms: list[str] = None) -> Optional[dict[str, Any]]:
    if algorithms is None:
        algorithms = ["HS256"]
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except JWTError:
        return None