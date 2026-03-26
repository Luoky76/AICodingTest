"""Customer query client.

Calls external customer service API to verify customer information.
When USE_MOCK_SERVICES is enabled, uses mock data.
"""

from __future__ import annotations

import httpx

from app.config import settings
from app.models.schemas import CustomerInfo

# Mock customer database for development/testing
_MOCK_CUSTOMERS: dict[str, CustomerInfo] = {
    "acme corp": CustomerInfo(exists=True, active=True),
    "acme corporation": CustomerInfo(exists=True, active=True),
    "globex": CustomerInfo(exists=True, active=True),
    "initech": CustomerInfo(exists=True, active=False),
    "测试公司": CustomerInfo(exists=True, active=True),
    "示例企业": CustomerInfo(exists=True, active=True),
    "无效客户": CustomerInfo(exists=True, active=False),
}


async def query_customer(customer_name: str) -> CustomerInfo:
    """Query customer existence and status.

    Args:
        customer_name: The customer name to look up.

    Returns:
        CustomerInfo with existence and active status.
    """
    if settings.USE_MOCK_SERVICES or not settings.CUSTOMER_API_URL:
        return _mock_query(customer_name)

    return await _call_customer_api(customer_name)


async def _call_customer_api(customer_name: str) -> CustomerInfo:
    """Call the real customer API."""
    async with httpx.AsyncClient(timeout=settings.PROCESSING_TIMEOUT) as client:
        response = await client.get(
            settings.CUSTOMER_API_URL,
            params={"customerName": customer_name},
        )
        response.raise_for_status()
        data = response.json()

    return CustomerInfo(
        exists=data.get("exists", False),
        active=data.get("active", False),
    )


def _mock_query(customer_name: str) -> CustomerInfo:
    """Mock customer query using predefined data."""
    key = customer_name.strip().lower()
    if key in _MOCK_CUSTOMERS:
        return _MOCK_CUSTOMERS[key]
    return CustomerInfo(exists=False, active=False)
