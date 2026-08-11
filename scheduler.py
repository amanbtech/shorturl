from apscheduler.schedulers.background import BackgroundScheduler

from database import get_cursor, conn
from redis_client import r


def update_top_urls():

    cursor = get_cursor()

    cursor.execute("""
        SELECT short_code
        FROM url_shortener
        ORDER BY clicks DESC
        LIMIT 100
    """)

    top_urls = cursor.fetchall()

    for url in top_urls:
        short_code = url[0]

        try:
            r.zadd(
                "top_urls",
                {
                    short_code: 1
                }
            )
        except Exception:
            pass


def sync_redis_clicks():

    cursor = get_cursor()

    cursor.execute("""
        SELECT short_code
        FROM url_shortener
    """)

    urls = cursor.fetchall()

    for url in urls:

        short_code = url[0]

        try:
            clicks = r.get(
                f"clicks:{short_code}"
            )

            if clicks is not None:

                cursor.execute(
                    """
                    UPDATE url_shortener
                    SET clicks = clicks + ?
                    WHERE short_code=?
                    """,
                    (
                        int(clicks),
                        short_code
                    )
                )

                r.delete(
                    f"clicks:{short_code}"
                )

        except Exception:
            pass

    conn.commit()


scheduler = BackgroundScheduler()


scheduler.add_job(
    sync_redis_clicks,
    "interval",
    minutes=5
)


scheduler.add_job(
    update_top_urls,
    "interval",
    minutes=10
)


def start_scheduler():
    scheduler.start()