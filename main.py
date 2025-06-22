from src.routes import github_router
from fastapi import FastAPI
import uvicorn,os
from contextlib import asynccontextmanager
from fastapi.requests import Request
from typing import cast
from fastapi.responses import JSONResponse

from src.middleware import register_middleware
from src.errors import register_all_errors

# from auth_service.db import create_tables


version = "v1"

description = """
A REST API on the Auth Services for the AI Governance Readiness Assessment Platform.

This API enables:
- AI governance readiness assessments based on the STANDARD framework.
- Dynamic scoring and generation of readiness reports.
- User management, including assessment tracking and analytics.
- Secure storage and retrieval of assessment data.
- PDF generation for assessment reports.
- Compliance with GDPR/NDPR regulations.
"""

version_prefix = f"/api/{version}"



@asynccontextmanager
async def lifespan(app: FastAPI):

    # await create_tables() # This will bypass alembic migrations

    yield


app = FastAPI(
    lifespan=lifespan,
    title="African Voices",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "EqualyzAI",
        "url": "https://equalyz.ai/",
        "email": "uche@equalyz.ai",
    },
    terms_of_service="https://equalyz.ai/about-us/",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)


# Register error handlers and middleware
register_all_errors(app)
register_middleware(app)


@app.get(f"/")
async def ping():
    return JSONResponse(content={"status": "Welcome to African Voices API"})


@app.get(f"{version_prefix}/health", tags=["Health"])
async def ping():
    return JSONResponse(content={"status": "pong"})



app.include_router(
    github_router,
    prefix=f"{version_prefix}/data",
    tags=["Data"],
)




if __name__ == "__main__":
    ENV = os.getenv("ENV", "development")
    PORT = int(os.getenv("PORT", 10000))
    HOST = "0.0.0.0" if ENV == "production" else "localhost"

    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True if ENV == "development" else False,
        proxy_headers=True
    )
