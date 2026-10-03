import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

from app.api import chat, health

logging.basicConfig(level=logging.INFO)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def create_app(static_dir: Path = STATIC_DIR) -> FastAPI:
    app = FastAPI(title="Uruguay Guide", docs_url=None, redoc_url=None, openapi_url=None)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse({"detail": "Invalid request."}, status_code=422)

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception) -> JSONResponse:
        logging.getLogger(__name__).exception("unhandled error", exc_info=exc)
        return JSONResponse({"detail": "Something went wrong."}, status_code=500)

    app.include_router(health.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def _api_not_found(path: str) -> None:
        raise HTTPException(404, "Not found.")

    if (static_dir / "index.html").is_file():

        @app.get("/{path:path}", include_in_schema=False)
        async def _spa(path: str) -> FileResponse:
            candidate = (static_dir / path).resolve()
            if path and candidate.is_file() and static_dir.resolve() in candidate.parents:
                return FileResponse(candidate)
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
