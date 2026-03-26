"""Price query client.

Calls external price service API to verify pricing.
When USE_MOCK_SERVICES is enabled, uses mock data.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.models.schemas import PriceInfo

# Mock price data for development/testing
_MOCK_PRICES: dict[str, PriceInfo] = {
    "PROD-001": PriceInfo(productCode="PROD-001", standardPrice=99.99, minPrice=89.99, maxPrice=109.99),
    "PROD-002": PriceInfo(productCode="PROD-002", standardPrice=49.99, minPrice=44.99, maxPrice=54.99),
    "PROD-003": PriceInfo(productCode="PROD-003", standardPrice=199.99, minPrice=179.99, maxPrice=219.99),
    "PROD-004": PriceInfo(productCode="PROD-004", standardPrice=29.99, minPrice=26.99, maxPrice=32.99),
    "SKU-100": PriceInfo(productCode="SKU-100", standardPrice=15.00, minPrice=13.50, maxPrice=16.50),
    "SKU-200": PriceInfo(productCode="SKU-200", standardPrice=75.00, minPrice=67.50, maxPrice=82.50),
}


async def query_price(product_code: str) -> PriceInfo:
    """Query standard price information for a product.

    Args:
        product_code: The product code to look up.

    Returns:
        PriceInfo with standard and allowed price range.
    """
    if settings.USE_MOCK_SERVICES or not settings.PRICE_API_URL:
        return _mock_query(product_code)

    return await _call_price_api(product_code)


async def _call_price_api(product_code: str) -> PriceInfo:
    """Call the real price API."""
    async with httpx.AsyncClient(timeout=settings.PROCESSING_TIMEOUT) as client:
        response = await client.get(
            settings.PRICE_API_URL,
            params={"productCode": product_code},
        )
        response.raise_for_status()
        data = response.json()

    return PriceInfo(
        productCode=product_code,
        standardPrice=data.get("standardPrice", 0.0),
        minPrice=data.get("minPrice", 0.0),
        maxPrice=data.get("maxPrice", 0.0),
    )


def _mock_query(product_code: str) -> PriceInfo:
    """Mock price query using predefined data."""
    code = product_code.strip().upper()
    if code in _MOCK_PRICES:
        return _MOCK_PRICES[code]
    return PriceInfo(
        productCode=code,
        standardPrice=0.0,
        minPrice=0.0,
        maxPrice=0.0,
    )
