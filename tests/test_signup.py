from fastapi.testclient import TestClient
from  main import app
client=TestClient(app)

response=client.post(
    "/signup",
    json={
            "username":"amdeep",
            "email":"amanech@gmail.com",
            "password_hash":"aman@123"
    }
)
assert response.status_code == 200
