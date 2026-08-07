from fastapi.testclient import TestClient
from  main import app
import uuid
client=TestClient(app)

response=client.post(
    "/signup",
    json={
            "username":f"text_{uuid.uuid4().hex}",
            "email":f"text_{uuid.uuid4().hex}@example.com",
            "password_hash":"aman@123"
    }
)
assert response.status_code == 200
