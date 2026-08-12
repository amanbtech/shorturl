from apscheduler.schedulers.background import BackgroundScheduler

from database import get_cursor, conn
from redis_client import r


def update_top_urls():

    cursor = get_cursor()
    cursor.execute("SELECT short_code,original_url FROM url_shortener ORDER BY clicks DESC LIMIT 100")
    DATA = cursor.fetchall()
    for short_code, url in DATA:
        try:
             r.set(short_code, url)
        except Exception:
            pass
def sync_redis_clicks():

    cursor = get_cursor()
    cursor.execute("SELECT short_code FROM url_shortener ")
    syn_dta=cursor.fetchall()
    for (short_code,) in syn_dta:
        current_short_code=short_code
        try:
            click_data=r.get(f"clicks:{current_short_code}")
        except Exception:
            pass
        if click_data :
            cursor = conn.cursor()
            cursor.execute("UPDATE url_shortener SET clicks=? WHERE short_code=?",(int(click_data),current_short_code))
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