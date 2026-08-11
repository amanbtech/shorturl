from fastapi import APIRouter, HTTPException

from schemas import Signup, Login
from database import get_cursor, conn
from auth import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter()


@router.post("/signup")
def signup(user: Signup):

    cursor = get_cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(
        user.password_hash
    )

    try:
        cursor.execute(
            """
            INSERT INTO users(username, email, password_hash)
            VALUES(?,?,?)
            """,
            (
                user.username,
                user.email,
                hashed_password
            )
        )

        conn.commit()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return {
        "message": "signup completed"
    }


@router.post("/login")
def login(user: Login):

    cursor = get_cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    )

    data = cursor.fetchone()

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db_password = data[3]

    if not verify_password(
        user.password_hash,
        db_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )

    token = create_access_token(
        username=data[1],
        role=data[4]
    )

    return {
        "token": token
    }