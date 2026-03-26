"""Order Information Auto-Extraction and Verification Assistant.

Entry point for the FastAPI application.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="订单信息自动提取与验证助手",
        description="Order Information Auto-Extraction and Verification Assistant",
        version="0.1.0",
    )

    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Include API routes
    app.include_router(router)

    return app


app = create_app()


def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
