from fastapi.testclient import TestClient
from main import  app
client=TestClient(app)
def test_redirect():
    client.post(
        "/signup",
        json={
            "username": "aman",
            "email": "aman@gmail.com",
            "password_hash": "123456"
        }
    )
    login_response = client.post(
        "/login",
        json={
            "username": "aman",
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
    short_code=data_response.json()["short_code"]
    delete_response=client.delete(f"/delete/{short_code}",headers={"Authorization":f"Bearer{token}"})
    assert delete_response.status_code == 200