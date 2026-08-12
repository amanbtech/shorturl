
from datetime import datetime, timedelta
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from schemas import Urls, UpdateUrl
from database import get_cursor, conn
from auth import get_current_user
from redis_client import r
from utils import short_coder, validate_custom_code
router = APIRouter()
@router.post("/data_save")
def create_short_url(
    url: Urls,
    current_user=Depends(get_current_user)
):
    username = current_user["username"]
    try:
        count = r.incr(f"rate_limit:{username}")

        if count == 1:
            r.expire(
                f"rate_limit:{username}",
                60
            )
    except redis.ConnectionError:
        count = 1

    if count > 5:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    if url.custom_code:

        valid, error_message = validate_custom_code(
            url.custom_code
        )

        if not valid:
            raise HTTPException(
                status_code=400,
                detail=error_message
            )

        cursor = get_cursor()

        cursor.execute(
            """
            SELECT 1
            FROM url_shortener
            WHERE short_code=?
            """,
            (url.custom_code,)
        )

        existing_code = cursor.fetchone()

        if existing_code:
            raise HTTPException(
                status_code=400,
                detail="Custom code already exists"
            )

        short_code = url.custom_code

    else:

        short_code = short_coder()
    creating_time = datetime.now().date()

    expiry = datetime.now() + timedelta(
        days=url.expiry_days
    )
    try:

        cursor = get_cursor()

        cursor.execute(
            """
            INSERT INTO url_shortener(
                original_url,
                short_code,
                creating_time,
                username,
                expires_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                str(url.original_url),
                short_code,
                str(creating_time),
                username,
                expiry.isoformat()
            )
        )

        conn.commit()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return {
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:8000/{short_code}"
    }
@router.get("/{short_code}")
def redirect_url(short_code: str):
    try:

        redis_result = r.get(short_code)

    except redis.ConnectionError:

        redis_result = None
    if redis_result:

        try:
            r.incr(
                f"clicks:{short_code}"
            )
        except redis.ConnectionError:
            pass

        return RedirectResponse(
            url=str(redis_result)
        )

    # -----------------------------------------------------
    # Redis miss → check database
    # -----------------------------------------------------

    cursor = get_cursor()

    cursor.execute(
        """
        SELECT original_url, expires_at
        FROM url_shortener
        WHERE short_code=?
        """,
        (short_code,)
    )

    data = cursor.fetchone()

    if data is None:

        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    expiry = datetime.fromisoformat(
        data[1]
    )

    if datetime.now() > expiry:

        raise HTTPException(
            status_code=404,
            detail="URL expired"
        )
    try:

        r.incr(
            f"clicks:{short_code}"
        )

    except redis.ConnectionError:
        pass
    try:

        r.set(
            short_code,
            str(data[0]),
            ex=86400
        )

    except redis.ConnectionError:
        pass

    return RedirectResponse(
        url=data[0]
    )
@router.get("/status/{short_code}")
def get_stats(short_code: str):

    cursor = get_cursor()

    cursor.execute(
        """
        SELECT
            original_url,
            short_code,
            clicks,
            creating_time
        FROM url_shortener
        WHERE short_code=?
        """,
        (short_code,)
    )

    data = cursor.fetchone()

    if not data:

        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    return {
        "original_url": data[0],
        "short_code": data[1],
        "clicks": data[2],
        "clicktime": data[3]
    }
@router.get("/top-search")
def top_url():

    cursor = get_cursor()

    cursor.execute(
        """
        SELECT
            original_url,
            short_code,
            clicks,
            creating_time
        FROM url_shortener
        ORDER BY clicks DESC
        LIMIT 1
        """
    )

    top_data = cursor.fetchone()

    if not top_data:

        raise HTTPException(
            status_code=404,
            detail="No URL found"
        )

    return {
        "original_url": top_data[0],
        "short_code": top_data[1],
        "clicks": top_data[2],
        "creating_time": top_data[3]
    }
@router.delete("/delete/{short_code}")
def delete_url(
    short_code: str,
    current_user=Depends(get_current_user)
):

    username = current_user["username"]

    cursor = get_cursor()
    cursor.execute(
        """
        SELECT username
        FROM url_shortener
        WHERE short_code=?
        """,
        (short_code,)
    )

    data = cursor.fetchone()

    if data is None:

        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    owner = data[0]

    # -----------------------------------------------------
    # Check ownership
    # -----------------------------------------------------

    if owner != username:

        raise HTTPException(
            status_code=403,
            detail="You are not the owner of this URL"
        )
    try:

        cursor.execute(
            """
            DELETE FROM url_shortener
            WHERE short_code=?
            """,
            (short_code,)
        )

        conn.commit()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    try:

        r.delete(short_code)

    except redis.ConnectionError:
        pass

    return {
        "status": "success",
        "message": "URL deleted"
    }

@router.put("/update/{short_code}")
def update_url(
    short_code: str,
    new_url: UpdateUrl,
    current_user=Depends(get_current_user)
):

    username = current_user["username"]

    cursor = get_cursor()
    cursor.execute(
        """
        SELECT username
        FROM url_shortener
        WHERE short_code=?
        """,
        (short_code,)
    )

    data = cursor.fetchone()

    if data is None:

        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    owner = data[0]
    if owner != username:

        raise HTTPException(
            status_code=403,
            detail="You are not the owner"
        )
    try:

        cursor.execute(
            """
            UPDATE url_shortener
            SET original_url=?
            WHERE short_code=?
            """,
            (
                new_url.original_url,
                short_code
            )
        )

        conn.commit()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    try:

        r.delete(short_code)

    except redis.ConnectionError:
        pass

    return {
        "original_url": new_url.original_url
    }
@router.delete("/cleanup")
def cleanup():

    try:

        cursor = get_cursor()

        cursor.execute(
            """
            DELETE FROM url_shortener
            WHERE expires_at < ?
            """,
            (datetime.now().isoformat(),)
        )
        conn.commit()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

    return {
        "status": "success",
        "message": "Expired URL deleted"
    }