"""Order Information Auto-Extraction and Verification Assistant.

Entry point for the FastAPI application.
"""

import threading
import webbrowser

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.config import settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="订单信息自动提取与验证助手",
        description="Order Information Auto-Extraction and Verification Assistant",
        version="0.1.0",
    )

    # Mount static files
    application.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Include API routes
    application.include_router(router)

    return application


app = create_app()


def _open_browser() -> None:
    """Open the default browser to the application URL after a short delay."""
    url = f"http://127.0.0.1:{settings.PORT}"
    webbrowser.open(url)


def main() -> None:
    """Run the application server."""
    # Open browser in a background thread so it doesn't block server startup
    timer = threading.Timer(1.5, _open_browser)
    timer.daemon = True
    timer.start()

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
