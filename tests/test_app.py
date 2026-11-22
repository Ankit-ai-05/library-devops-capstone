import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
from app import app

def test_health():
    client = app.test_client()
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "UP"

def test_api_add_and_get_books():
    client = app.test_client()
    res = client.post("/api/books", json={"title": "DevOps Handbook", "author": "Gene Kim"})
    assert res.status_code == 201
    res_list = client.get("/api/books")
    assert res_list.status_code == 200
    assert len(res_list.get_json()) >= 1
