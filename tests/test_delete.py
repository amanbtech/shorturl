from fastapi.testclient import TestClient
from main import  app
client=TestClient(app)
import uuid
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
            "original_url": "https://google.com",
            "expiry_days": 8
        }
    )
    print(login_response.status_code)
    print(login_response.json())

    print(data_response.status_code)
    print(data_response.text)
    print(data_response.json())
    short_code=data_response.json()["short_code"]
    delete_response=client.delete(f"/delete/{short_code}",headers={"Authorization":f"Bearer{token}"})
    assert delete_response.status_code == 200