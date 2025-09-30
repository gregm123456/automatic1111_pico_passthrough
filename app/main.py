from fastapi import FastAPI
from app.routers import txt2img
from app.config import Settings

settings = Settings()

def create_app() -> FastAPI:
    app = FastAPI(title="Pico A1111 Proxy")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        import time
        from starlette.requests import Request

        start = time.time()
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        print(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed:.1f}ms)")
        return response

    app.include_router(txt2img.router)
    return app

app = create_app()
