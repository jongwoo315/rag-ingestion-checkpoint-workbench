import pytest


@pytest.mark.asyncio
async def test_create_and_list_document(client):
    payload = {"name": "sample.txt", "content": "hello world " * 50}
    response = await client.post("/documents/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "sample.txt"
    assert data["chunks_count"] > 0

    response = await client.get("/documents/")
    assert response.status_code == 200
    assert len(response.json()) == 1
