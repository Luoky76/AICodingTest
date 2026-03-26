"""AI client for order information extraction.

Calls external AI API to convert raw text into structured order data.
When USE_MOCK_SERVICES is enabled, uses a simple rule-based mock.
"""

from __future__ import annotations

import re

import httpx

from app.config import settings
from app.models.schemas import ExtractedOrderData, OrderItem


async def extract_order_data(raw_text: str) -> ExtractedOrderData:
    """Call AI API to extract structured order data from raw text.

    Args:
        raw_text: The raw text content to analyze.

    Returns:
        ExtractedOrderData with structured order information.
    """
    if settings.USE_MOCK_SERVICES or not settings.AI_API_URL:
        return _mock_extract(raw_text)

    return await _call_ai_api(raw_text)


async def _call_ai_api(raw_text: str) -> ExtractedOrderData:
    """Call the real AI API."""
    async with httpx.AsyncClient(timeout=settings.PROCESSING_TIMEOUT) as client:
        response = await client.post(
            settings.AI_API_URL,
            json={"rawText": raw_text},
        )
        response.raise_for_status()
        data = response.json()

    return ExtractedOrderData(
        customerName=data.get("customerName", ""),
        items=[OrderItem(**item) for item in data.get("items", [])],
        deliveryDate=data.get("deliveryDate", ""),
        confidence=data.get("confidence", 0.0),
    )


def _mock_extract(raw_text: str) -> ExtractedOrderData:
    """Mock AI extraction using simple pattern matching.

    This simulates what an AI API would return by doing basic
    text analysis. In production, this would be replaced by a
    real AI service call.
    """
    text = raw_text.lower()

    # Try to extract customer name
    customer_name = ""
    customer_patterns = [
        r"customer[:\s]+([^\n,]+)",
        r"client[:\s]+([^\n,]+)",
        r"客户[：:\s]+([^\n,]+)",
        r"公司[：:\s]+([^\n,]+)",
    ]
    for pattern in customer_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            customer_name = match.group(1).strip()
            break

    # Try to extract delivery date
    delivery_date = ""
    date_patterns = [
        r"delivery[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        r"交付[日期]*[：:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
    ]
    for pattern in date_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            delivery_date = match.group(1).strip()
            break

    # Try to extract items from table-like patterns
    items: list[OrderItem] = []
    # Match patterns like: PROD-001 | 10 | 99.99  or  PROD-001, 10, 99.99
    item_patterns = [
        r"([A-Z]{2,}[-_]?\d{2,})\s*[|,\t]\s*(\d+(?:\.\d+)?)\s*[|,\t]\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in item_patterns:
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        for m in matches:
            items.append(OrderItem(
                productCode=m[0].upper(),
                quantity=float(m[1]),
                price=float(m[2]),
            ))

    # Calculate confidence based on how much data we extracted
    confidence = 0.0
    if customer_name:
        confidence += 0.3
    if delivery_date:
        confidence += 0.2
    if items:
        confidence += 0.5

    return ExtractedOrderData(
        customerName=customer_name,
        items=items,
        deliveryDate=delivery_date,
        confidence=round(confidence, 2),
    )
