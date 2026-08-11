import bcrypt
from jose import jwt
from datetime import datetime, timedelta, UTC

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

from config import SECRET_KEY, ALGORITHMS


security = HTTPBearer()


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )
    return hashed_password.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )


def create_access_token(username: str, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(hours=1)

    payload = {
        "username": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHMS
    )

    return token


def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHMS]
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )