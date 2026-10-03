import httpx


async def test_health(client: httpx.AsyncClient) -> None:
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_unknown_api_route_is_404(client: httpx.AsyncClient) -> None:
    assert (await client.get("/api/nope")).status_code == 404
