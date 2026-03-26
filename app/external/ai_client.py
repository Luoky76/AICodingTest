"""AI client for order information extraction.

Calls the Deepseek AI API to convert raw text into structured order data.
When USE_MOCK_SERVICES is enabled, uses a simple rule-based mock.
"""

from __future__ import annotations

import json
import re

import httpx

from app.config import settings
from app.models.schemas import ExtractedOrderData, OrderItem

# System prompt instructing the AI to extract order information
_SYSTEM_PROMPT = """你是一个专业的订单信息提取助手。你的任务是从用户提供的非结构化文本中提取订单信息。

请严格按照以下JSON格式返回结果，不要包含任何其他文字、解释或markdown标记：
{
  "customerName": "客户名称（字符串）",
  "items": [
    {
      "productCode": "产品编码（字符串）",
      "quantity": 数量（数字）,
      "price": 单价（数字）
    }
  ],
  "deliveryDate": "交付日期（字符串，格式YYYY-MM-DD）",
  "confidence": 置信度（0到1之间的数字，表示你对提取结果的信心程度）
}

提取规则：
1. customerName: 提取客户/公司名称，如果找不到则返回空字符串
2. items: 提取所有产品项目，包括产品编码、数量和单价
3. deliveryDate: 提取交付日期，统一转为YYYY-MM-DD格式，如果找不到则返回空字符串
4. confidence: 根据信息完整度给出0-1的置信度评分：
   - 1.0: 所有字段都能明确提取
   - 0.8-0.99: 大部分字段可以提取，少量信息需要推断
   - 0.5-0.79: 部分字段缺失或不确定
   - 0.0-0.49: 大量信息缺失，提取结果不可靠

只返回JSON，不要返回任何其他内容。"""


async def extract_order_data(raw_text: str) -> ExtractedOrderData:
    """Call AI API to extract structured order data from raw text.

    Args:
        raw_text: The raw text content to analyze.

    Returns:
        ExtractedOrderData with structured order information.
    """
    if settings.USE_MOCK_SERVICES or not settings.AI_API_KEY:
        return _mock_extract(raw_text)

    return await _call_ai_api(raw_text)


async def _call_ai_api(raw_text: str) -> ExtractedOrderData:
    """Call the Deepseek AI API for order extraction."""
    async with httpx.AsyncClient(timeout=settings.PROCESSING_TIMEOUT) as client:
        response = await client.post(
            settings.AI_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.AI_API_KEY}",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": raw_text},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            },
        )
        response.raise_for_status()
        result = response.json()

    # Extract the AI response content
    content = result["choices"][0]["message"]["content"]
    data = json.loads(content)

    return ExtractedOrderData(
        customerName=data.get("customerName", ""),
        items=[OrderItem(**item) for item in data.get("items", [])],
        deliveryDate=data.get("deliveryDate", ""),
        confidence=float(data.get("confidence", 0.0)),
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
