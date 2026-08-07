from urllib import response
import uuid
from fastapi.testclient import TestClient
from main import  app
client=TestClient(app)
def test_redirect():
    name=f"text_{uuid.uuid4().hex}"
    gmail=f"text_{uuid.uuid4().hex}@gmail.com"
    client.post(
        "/signup",
        json={
            "username": name,
            "email": gmail,
            "password_hash": "123456"
        }
    )
    login_response = client.post(
        "/login",
        json={
            "username": name,
            "password_hash": "123456"
        }
    )
    token = login_response.json()["token"]
    data_response = client.post(
        "/data_save",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "original_url": "https://google.com/",
            "expiry_days": 8
        }
    )
    short_code=data_response.json()["short_code"]
    redirect_response=client.get(f"/{short_code}",follow_redirects=False)
    assert redirect_response.status_code==307
    assert redirect_response.headers["location"]=="https://google.com/"