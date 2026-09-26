import pytest

from app.models import Stage


@pytest.mark.asyncio
async def test_replay_failed_document(client):
    payload = {"name": "fail.txt", "content": "chunk me " * 200}
    response = await client.post("/documents/", json=payload)
    document = response.json()

    if document["stage"] == Stage.completed.value:
        pytest.skip("Document happened to succeed; deterministic test requires a failure")

    doc_id = document["id"]
    response = await client.post(f"/replay/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == doc_id
