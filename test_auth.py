import os
from fastapi.testclient import TestClient
import pytest

from app import app

client = TestClient(app)

def test_no_api_key_env_allows_requests(monkeypatch):
    # Ensure AUTOMATION_API_KEY is not set
    monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)
    resp = client.post("/automate", json={"run": False})
    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"

def test_api_key_required_and_rejected(monkeypatch):
    # Set the env var to require a key
    monkeypatch.setenv("AUTOMATION_API_KEY", "test-key")
    # Without header -> 401
    resp = client.post("/automate", json={"run": False})
    assert resp.status_code == 401

def test_api_key_required_and_accepted(monkeypatch):
    monkeypatch.setenv("AUTOMATION_API_KEY", "test-key")
    headers = {"X-API-Key": "test-key"}
    resp = client.post("/automate", json={"run": False}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "skipped"