import token

from fastapi import responses
from fastapi.testclient import TestClient
from main import  app
login_client=TestClient(app)
response=login_client.post("/login",json={"username":"amandeep","password_hash":"aman@123"})
assert response.status_code==200