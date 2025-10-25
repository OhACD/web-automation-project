import asyncio
import json
import os
import pytest
from fastapi.testclient import TestClient

from app import app, SCRIPT_PATH

client = TestClient(app)

class DummyProcess:
    """
    Dummy asynchronous process used to simulate subprocess execution for testing.
    """
    def __init__(self, stdout_bytes: bytes, stderr_bytes: bytes = b"", returncode: int = 0):
        self._stdout = stdout_bytes
        self._stderr = stderr_bytes
        self.returncode = returncode
        self._killed = False

    async def communicate(self):
        # Simulate async subprocess.communicate
        await asyncio.sleep(0)
        return (self._stdout, self._stderr)

    def kill(self):
        self._killed = True


@pytest.fixture
def env_item(monkeypatch):
    """
    Fixture that reads ITEM_TO_LOOKUP from environment (or default),
    so tests automatically adapt to .env or API configuration.
    """
    item = os.getenv("ITEM_TO_LOOKUP", "Sauce Labs Backpack")
    monkeypatch.setenv("ITEM_TO_LOOKUP", item)
    return item


@pytest.mark.asyncio
async def test_automate_success(monkeypatch, env_item):
    """
    Simulates a successful automation subprocess returning a product lookup.
    """
    mock_output = {
        "status": "success",
        "product": env_item,
        "price": "$29.99"
    }
    dummy = DummyProcess(json.dumps(mock_output).encode(), b"", 0)

    async def fake_create_subprocess_exec(*args, **kwargs):
        return dummy

    monkeypatch.setattr("asyncio.create_subprocess_exec", fake_create_subprocess_exec)

    response = client.post("/automate", json={"run": True})
    assert response.status_code == 200, f"Unexpected response: {response.text}"

    body = response.json()
    assert body["status"] == "success"
    assert "result" in body

    result = body["result"]
    assert result["product"] == env_item
    assert "price" in result and result["price"].startswith("$")

    print(f"Automation success for {result['product']} — price: {result['price']}")


@pytest.mark.asyncio
async def test_automate_script_error(monkeypatch, env_item):
    """
    Simulates a failed automation subprocess returning an error response.
    """
    mock_output = {
        "status": "error",
        "message": f"Product not found: {env_item}"
    }
    dummy = DummyProcess(json.dumps(mock_output).encode(), b"", 1)

    async def fake_create_subprocess_exec(*args, **kwargs):
        return dummy

    monkeypatch.setattr("asyncio.create_subprocess_exec", fake_create_subprocess_exec)

    response = client.post("/automate", json={"run": True})
    assert response.status_code == 500, f"Expected 500, got {response.status_code}: {response.text}"

    body = response.json()
    assert "detail" in body
    assert body["detail"]["status"] == "error"

    detail = body["detail"]
    assert "message" in detail["result"]
    assert env_item in detail["result"]["message"]

    print(f"Automation failed for {env_item}: {detail['result']['message']}")
