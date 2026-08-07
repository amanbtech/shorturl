
import uuid

from fastapi.testclient import TestClient
from main import  app
login_client=TestClient(app)
response=login_client.post("/login", json={"username":f"text_{uuid.uuid4().hex}", "password_hash": "aman@123"})
assert response.status_code==200