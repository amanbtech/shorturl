
import uuid

from fastapi.testclient import TestClient
from main import  app


login_client=TestClient(app)
name=f"text_{uuid.uuid4().hex}"
gmail=f"text_{uuid.uuid4().hex}"
def login():
    login_client.post("/signup",json={
        "username":name,
        "email":gmail,
        "password_hash":"aman@123"

    })
    response=login_client.post("/login", json={"username":name, "password_hash": "aman@123"})
    print(response.status_code)
    print(response.text)
    print(response.json())
    assert response.status_code==200