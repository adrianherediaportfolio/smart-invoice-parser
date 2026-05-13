import pytest
from httpx import ASGITransport, AsyncClient

from src.core.database import init_db
from src.main import app


@pytest.fixture(autouse=True)
async def setup_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("src.core.database.DB_PATH", db_path)
    await init_db()


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "smart-invoice-parser"


@pytest.mark.asyncio
async def test_parse_rejects_unsupported_file():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/parse",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_invoices_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/invoices")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_invoice_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/invoices/999")
    assert response.status_code == 404
