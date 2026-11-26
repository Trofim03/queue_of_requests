import pytest

@pytest.mark.asyncio
async def test_create_and_list_tickets(client):
    # Создание
    response = await client.post("/api/tickets", json={"title": "Test", "description": "Test desc"})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "queued"
    
    # Список с фильтром
    response = await client.get("/api/tickets?status=queued")
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["title"] == "Test"
    
    # Карточка
    ticket_id = data["id"]
    response = await client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200