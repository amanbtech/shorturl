
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi import Header
from fastapi.security import HTTPBearer
from fastapi import Depends
from fastapi.responses import RedirectResponse
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta,UTC
from apscheduler.schedulers.background import BackgroundScheduler
import  re
import sqlite3
import random
import string
import bcrypt
import redis
import  os
from dotenv import load_dotenv

load_dotenv()
app=FastAPI()
security = HTTPBearer()
SECRET_KEY=os.getenv("SECRET_KEYenv")
ALGORITHMS=os.getenv("ALGORITHMSenv")
conn=sqlite3.connect("project1.db",check_same_thread=False)
pool = redis.ConnectionPool(
    host=os.getenv("hostenv"),
    port=int(os.getenv("portenv","6379")),
    password=os.getenv("passwordenv"),
    username=os.getenv("usernameenv"),
    decode_responses=True,
    max_connections=20
)
r=redis.Redis(connection_pool=pool)
class Urls(BaseModel):
    original_url:HttpUrl
    custom_code:Optional[str]=None
    expiry_days:int =7
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS url_shortener(id INTEGER PRIMARY KEY AUTOINCREMENT,original_url TEXT ,short_code TEXT UNIQUE,clicks INTEGER DEFAULT 0,creating_time TEXT NOT NULL,username TEXT NOT NULL,expires_at TEXT)")
conn.commit()
def short_coder():
    return "".join(random.choices(string.ascii_letters+string.digits,k=6))
@app.post("/data_save")
def data(url:Urls,credentials=Depends(security)):

    token = credentials.credentials

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHMS]
    )
    username = payload["username"]
    try:
        count = r.incr(f"rate_limit:{username}")
        if count == 1:
            r.expire(f"rate_limit:{username}", 60)
    except redis.ConnectionError:
        count = 1  # Bypass rate limiting if Redis is down
    if count >5:
        raise HTTPException(status_code=429,detail="too many request")
    if url.custom_code:
        if url.custom_code.strip()=="":
            raise HTTPException(status_code=400,detail="short code cannot be empty")
        if len(url.custom_code)>20:
            raise HTTPException(status_code=400,detail="short code too long")

        if not re.match(r"^[a-zA-Z0-9_-]+$", url.custom_code, ):
            raise HTTPException(status_code=400,detail="not valid")
        print(9)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM url_shortener WHERE short_code=?", (url.custom_code,))
        edata = cursor.fetchone()
        if edata:
            raise HTTPException(status_code=400, detail="custom code already exits")
        short_code=url.custom_code
    else:
        short_code=short_coder()
    creating_time=datetime.now().date()
    expiry=datetime.now()+timedelta(days=url.expiry_days)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO url_shortener(original_url,short_code,creating_time,username,expires_at) VALUES(?,?,?,?,?)",(str(url.original_url),short_code,str(creating_time),username,expiry.isoformat()))
        conn.commit()
    except Exception as e:
        print("ERROR:", e)
        raise
    return {
        "short_code": short_code,
        "short_url": f"http://127.0.0.1:8000/{short_code}"
    }
@app.get("/{short_code}")
def redirect_url(short_code:str):
    try:
     redis_result=r.get(short_code)
    except redis.ConnectionError:
        redis_result=None
    if redis_result:
        r.incr(f"clicks:{short_code}")
        return RedirectResponse(url=str(redis_result))
    cursor = conn.cursor()
    cursor.execute("SELECT original_url,expires_at FROM url_shortener WHERE  short_code=?",(short_code,))

    data=cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=404,detail="url not found")
    expiry=datetime.fromisoformat(data[1])
    if datetime.now()>expiry:
        raise HTTPException(status_code=404,detail="Url expired")
    try:
        r.incr(f"clicks:{short_code}")
    except redis.ConnectionError:
        pass
    try:
       r.set(short_code, str(data[0]), ex=86400)
    except:
        pass
    return RedirectResponse(url=data[0])

@app.get("/status/{short_code}")
def get_stats(short_code:str):
    cursor = conn.cursor()
    cursor.execute("SELECT original_url,short_code,clicks,creating_time  FROM url_shortener WHERE short_code=?",(short_code,))

    data=cursor.fetchone()
    if not data:
        raise  HTTPException(status_code=404,detail=" url ont found")
    return {
        "original_url":data[0],
        "short_code":data[1],
        "clicks":data[2],
        "clicktime":data[3]
    }
@app.get("/top-search")
def  top_url():
   cursor = conn.cursor()
   cursor.execute("SELECT original_url,short_code,clicks,creating_time FROM url_shortener ORDER BY clicks DESC LIMIT 1")
   TOPdata=cursor.fetchone()
   return {
       "original_url":TOPdata[0],
       "short_code":TOPdata[1],
       "clicks":TOPdata[2],
       "creating_time":TOPdata[3]
   }
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users(id  INTEGER PRIMARY KEY AUTOINCREMENT ,username TEXT UNIQUE,email  TEXT UNIQUE , password_hash TEXT UNIQUE,role TEXT DEFAULT 'user')")
conn.commit()
class signup(BaseModel):
    username: str
    email: str
    password_hash: str

@app.post("/signup")
def signup(user:signup):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM  users WHERE username=?", (user.username,))
    exit1 = cursor.fetchone()
    if exit1:
        raise HTTPException(status_code=400, detail="alredy exixt")
    else:
        hased_passowrd=bcrypt.hashpw(user.password_hash.encode(),bcrypt.gensalt())
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(username,email,password_hash) VALUES(?,?,?) ",(user.username,user.email,hased_passowrd.decode()))
            conn.commit()
        except Exception:
            raise HTTPException(status_code=500,detail="Internal server error")
    return{
        "message":"signin completed"

   }

class login(BaseModel):
    username: str
    password_hash: str
@app.post("/login")
def signin(user:login):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM  users WHERE username=?", (user.username,))
    data=cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=404,detail="data not ound")
    print("data found")
    db_password=data[3]
    print("saved")
    if not bcrypt.checkpw( user.password_hash.encode(),db_password.encode()):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"

    )
    print("brcrpty dat saved")
    expire = datetime.now(UTC) + timedelta(hours=1)
    payload={
        "username":data[1],
        "role":data[4],
        "exp":expire
    }

    token=jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHMS
    )
    print("done")
    return {
        "token":token
    }
@app.delete("/delete/{short_code}")
def  delete_url(short_code:str,credentials=Depends(security)):
    token = credentials.credentials
    payload=jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHMS]
    )
    username=payload["username"]
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM url_shortener WHERE short_code=?",(short_code,))
    data =cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=404,detail="url not found")
    owner=data[0]
    if owner !=username:
        raise HTTPException(status_code=403,detail="you are not owner of this url")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM url_shortener WHERE short_code=?",(short_code,))
        conn.commit()
    except Exception:
        raise HTTPException(status_code=500,detail="internal server error")
    return {
        "status": "success",
        "message": "URL deleted"

    }
class updateurl(BaseModel):
    original_url:str
@app.put("/update/{short_code}")
def update_url(short_code:str,new_url:updateurl,credentials=Depends(security)):
    token = credentials.credentials
    payload=jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHMS]
    )
    username=payload["username"]
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM url_shortener WHERE short_code=?",(short_code,))
    data=cursor.fetchone()
    if data is None:
        raise  HTTPException(status_code=404,detail="url not found")
    owner=data[0]
    if owner !=username:
        raise HTTPException(status_code=403,detail= "you are not owner")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE url_shortener SET original_url=? WHERE short_code=?",(new_url.original_url,short_code))
        conn.commit()

    except HTTPException:
        raise HTTPException(status_code=500,detail="internal server error")

    return {
        "original_url":new_url.original_url

    }

@app.delete("/cleanup")
def cleanup():
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM url_shortener WHERE expires_at < ?",(datetime.now().isoformat(),))
        conn.commit()
    except Exception:raise HTTPException(status_code=500, detail="internal server error")
    return {
        "status": "success",
        "message": " Expired URL deleted"

    }
def my_job():
    scheduler=BackgroundScheduler()
    scheduler.add_job(update_top_urls,"interval",minutes=10)
    scheduler.add_job(async_clicks_to_db,"interval",minutes=10)
    scheduler.start()
def update_top_urls():
    cursor = conn.cursor()
    cursor.execute("SELECT short_code,original_url FROM url_shortener ORDER BY clicks DESC LIMIT 100")
    DATA=cursor.fetchall()
    for short_code,url in DATA:
        r.set(short_code,url)
def async_clicks_to_db():
    cursor = conn.cursor()
    cursor.execute("SELECT short_code FROM url_shortener ")
    syn_dta=cursor.fetchall()
    for (short_code,) in syn_dta:
        current_short_code=short_code
        click_data=r.get(f"clicks:{current_short_code}")
        if click_data :
            cursor = conn.cursor()
            cursor.execute("UPDATE url_shortener SET clicks=? WHERE short_code=?",(int(click_data),current_short_code))
            conn.commit()



my_job()