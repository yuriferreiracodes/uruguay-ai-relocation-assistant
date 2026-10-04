from typing import get_args

import httpx

from app.config import get_settings
from app.knowledge.retriever import Retriever, _is_allowed  # pyright: ignore[reportPrivateUsage]
from app.knowledge.sources import OFFICIAL_CATEGORIES
from app.schemas.chat import Category


def make(handler: httpx.MockTransport) -> Retriever:
    return Retriever(get_settings(), httpx.AsyncClient(transport=handler, follow_redirects=True))


async def test_official_category_retrieves_content_and_sources() -> None:
    page = "<html><script>x=1</script><body><h1>Residencia</h1><p>Requisitos</p></body></html>"
    r = make(httpx.MockTransport(lambda req: httpx.Response(200, text=page)))
    ctx = await r.retrieve("residency")
    assert ctx.text and "Residencia Requisitos" in ctx.text and "x=1" not in ctx.text
    assert ctx.sources and all(s.retrieved_at for s in ctx.sources)
    assert all(_is_allowed(s.url) for s in ctx.sources)


async def test_non_official_category_returns_links_without_fetching() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise AssertionError("must not fetch")

    ctx = await make(httpx.MockTransport(boom)).retrieve("culture")
    assert ctx.text is None
    assert ctx.sources and all(s.retrieved_at is None for s in ctx.sources)


async def test_every_in_scope_category_has_sources() -> None:
    def boom(req: httpx.Request) -> httpx.Response:
        raise AssertionError("must not fetch")

    r = make(httpx.MockTransport(boom))
    for category in get_args(Category):
        if category in OFFICIAL_CATEGORIES or category == "out_of_scope":
            continue
        assert (await r.retrieve(category)).sources, category


async def test_retrieval_failure_still_returns_links() -> None:
    ctx = await make(httpx.MockTransport(lambda req: httpx.Response(500))).retrieve("citizenship")
    assert ctx.text is None
    assert ctx.sources and all(s.retrieved_at is None for s in ctx.sources)


async def test_cache_avoids_second_fetch() -> None:
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, text="<p>hello</p>")

    r = make(httpx.MockTransport(handler))
    await r.retrieve("documents")
    first = calls
    await r.retrieve("documents")
    assert calls == first


def test_only_official_domains_allowed() -> None:
    assert _is_allowed("https://www.gub.uy/tramites/x")
    assert _is_allowed("https://www.impo.com.uy")
    assert not _is_allowed("https://evil.com/gub.uy")
    assert not _is_allowed("https://gub.uy.evil.com")
