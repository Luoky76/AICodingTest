"""Inventory query client.

Calls external inventory service API to check stock levels.
When USE_MOCK_SERVICES is enabled, uses mock data.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.models.schemas import InventoryInfo

# Mock inventory data for development/testing
_MOCK_INVENTORY: dict[str, float] = {
    "PROD-001": 100.0,
    "PROD-002": 50.0,
    "PROD-003": 0.0,
    "PROD-004": 200.0,
    "SKU-100": 500.0,
    "SKU-200": 10.0,
}


async def query_inventory(product_code: str) -> InventoryInfo:
    """Query available inventory for a product.

    Args:
        product_code: The product code to look up.

    Returns:
        InventoryInfo with available quantity.
    """
    if settings.USE_MOCK_SERVICES or not settings.INVENTORY_API_URL:
        return _mock_query(product_code)

    return await _call_inventory_api(product_code)


async def _call_inventory_api(product_code: str) -> InventoryInfo:
    """Call the real inventory API."""
    async with httpx.AsyncClient(timeout=settings.PROCESSING_TIMEOUT) as client:
        response = await client.get(
            settings.INVENTORY_API_URL,
            params={"productCode": product_code},
        )
        response.raise_for_status()
        data = response.json()

    return InventoryInfo(
        productCode=product_code,
        availableQuantity=data.get("availableQuantity", 0.0),
    )


def _mock_query(product_code: str) -> InventoryInfo:
    """Mock inventory query using predefined data."""
    code = product_code.strip().upper()
    quantity = _MOCK_INVENTORY.get(code, -1.0)
    return InventoryInfo(
        productCode=code,
        availableQuantity=quantity,
    )
