"""Order information extraction service.

Coordinates calling the AI API to extract structured order data.
"""

from __future__ import annotations

from app.external.ai_client import extract_order_data
from app.models.schemas import ExtractedOrderData, ParsedContent


async def extract_order(parsed: ParsedContent) -> ExtractedOrderData:
    """Extract structured order data from parsed content.

    Args:
        parsed: The parsed content containing raw text.

    Returns:
        ExtractedOrderData with structured order information.

    Raises:
        RuntimeError: If extraction fails.
    """
    if not parsed.rawText.strip():
        raise ValueError("Cannot extract order data from empty content")

    try:
        result = await extract_order_data(parsed.rawText)
    except Exception as e:
        raise RuntimeError(f"Order extraction failed: {e}")

    return result
