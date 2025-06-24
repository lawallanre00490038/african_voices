from src.routes import github_router
from fastapi import FastAPI
import uvicorn,os
from contextlib import asynccontextmanager
from fastapi.requests import Request
from typing import cast
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.middleware import register_middleware
from src.errors import register_all_errors
from src.utils.audio_data_summary_folder.audio_summary import audio_data
from src.db import create_tables

load_dotenv()


version = "v1"

description = """
A REST API on the African Voices project.
"""

version_prefix = f"/api/{version}"



@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_tables() # This will bypass alembic migrations

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


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "Welcome to African Voices API"}


@app.get(f"{version_prefix}/health", tags=["Health"])
async def ping():
    return JSONResponse(content={"status": "pong"})



app.include_router(
    github_router
)
app.include_router(
    audio_data,
    tags=["Audio Data Summary in JSON"],
)



# if __name__ == "__main__":
#     uvicorn.run(
#         app="main:app",
#         host="localhost",
#         port=8000,
#         proxy_headers=True
#     )



if __name__ == "__main__":
    ENV = os.getenv("ENV", "development")
    PORT = int(os.getenv("PORT", 10000))
    HOST = "0.0.0.0" if ENV == "production" else "localhost"

    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=10000,
        reload=True if ENV == "development" else False,
        proxy_headers=True
    )