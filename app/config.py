"""Application configuration."""

import os


class Settings:
    """Application settings loaded from environment variables."""

    # Server settings
    HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

    # External service URLs
    AI_API_URL: str = os.getenv(
        "AI_API_URL", "https://api.deepseek.com/chat/completions"
    )
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek-chat")
    CUSTOMER_API_URL: str = os.getenv("CUSTOMER_API_URL", "")
    INVENTORY_API_URL: str = os.getenv("INVENTORY_API_URL", "")
    PRICE_API_URL: str = os.getenv("PRICE_API_URL", "")

    # Use mock external services when real APIs are not configured
    USE_MOCK_SERVICES: bool = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

    # Processing timeout in seconds (AI API calls may need more time)
    PROCESSING_TIMEOUT: float = float(os.getenv("PROCESSING_TIMEOUT", "30.0"))


settings = Settings()
