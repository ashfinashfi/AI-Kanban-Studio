import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app, VALID_TOKEN
from backend.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_auth_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/auth/login", json={"username": "user", "password": "wrongpassword"})
        assert res.status_code == 401

        res = await ac.post("/api/auth/login", json={"username": "user", "password": "password"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["token"] == VALID_TOKEN

@pytest.mark.asyncio
async def test_board_crud():
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/board", headers=headers)
        assert res.status_code == 200
        board = res.json()
        assert len(board["columns"]) == 5

        res = await ac.post("/api/cards", json={"column_id": "col-backlog", "title": "Pytest Task", "details": "Testing FastAPI"}, headers=headers)
        assert res.status_code == 200
        board = res.json()
        new_cards = [c for c in board["cards"].values() if c["title"] == "Pytest Task"]
        assert len(new_cards) == 1
        card_id = new_cards[0]["id"]

        res = await ac.put(f"/api/cards/{card_id}", json={"title": "Updated Pytest Task"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["cards"][card_id]["title"] == "Updated Pytest Task"

        res = await ac.post("/api/columns/col-backlog/rename", json={"title": "New Backlog"}, headers=headers)
        assert res.status_code == 200
        col = next(c for c in res.json()["columns"] if c["id"] == "col-backlog")
        assert col["title"] == "New Backlog"

        res = await ac.post("/api/cards/move", json={"active_id": card_id, "over_id": "col-done"}, headers=headers)
        assert res.status_code == 200
        done_col = next(c for c in res.json()["columns"] if c["id"] == "col-done")
        assert card_id in done_col["cardIds"]

        res = await ac.delete(f"/api/cards/{card_id}", headers=headers)
        assert res.status_code == 200
        assert card_id not in res.json()["cards"]

@pytest.mark.asyncio
async def test_ai_endpoints():
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/ai/test")
        assert res.status_code == 200
        assert "result" in res.json()

        res = await ac.post("/api/ai/chat", json={"message": "Add a task called AI Card to Backlog"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "reply" in data
        assert "board" in data
