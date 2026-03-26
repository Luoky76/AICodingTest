"""Tests for the data validation service."""

import pytest

from app.models.schemas import ExtractedOrderData, OrderItem
from app.services.validator import validate_order


@pytest.fixture
def valid_order():
    """A valid order that should pass all checks."""
    return ExtractedOrderData(
        customerName="Acme Corp",
        items=[
            OrderItem(productCode="PROD-001", quantity=10, price=99.99),
            OrderItem(productCode="PROD-002", quantity=5, price=49.99),
        ],
        deliveryDate="2024-06-15",
        confidence=0.9,
    )


@pytest.fixture
def low_confidence_order():
    """An order with low confidence score."""
    return ExtractedOrderData(
        customerName="Acme Corp",
        items=[
            OrderItem(productCode="PROD-001", quantity=10, price=99.99),
        ],
        deliveryDate="2024-06-15",
        confidence=0.5,
    )


class TestValidation:
    """Tests for order validation."""

    @pytest.mark.asyncio
    async def test_valid_order_passes(self, valid_order):
        result = await validate_order(valid_order)
        assert result.finalStatus == "pass"
        assert len(result.issues) == 0

    @pytest.mark.asyncio
    async def test_low_confidence_returns_manual(self, low_confidence_order):
        result = await validate_order(low_confidence_order)
        assert result.finalStatus == "manual"
        assert any("confidence" in issue.lower() for issue in result.issues)

    @pytest.mark.asyncio
    async def test_unknown_customer_fails(self):
        order = ExtractedOrderData(
            customerName="Unknown Company",
            items=[OrderItem(productCode="PROD-001", quantity=10, price=99.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("does not exist" in issue for issue in result.issues)

    @pytest.mark.asyncio
    async def test_inactive_customer_fails(self):
        order = ExtractedOrderData(
            customerName="Initech",
            items=[OrderItem(productCode="PROD-001", quantity=10, price=99.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("inactive" in issue.lower() for issue in result.issues)

    @pytest.mark.asyncio
    async def test_insufficient_inventory_fails(self):
        order = ExtractedOrderData(
            customerName="Acme Corp",
            items=[OrderItem(productCode="PROD-001", quantity=999, price=99.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("insufficient" in issue.lower() for issue in result.issues)

    @pytest.mark.asyncio
    async def test_price_out_of_range_fails(self):
        order = ExtractedOrderData(
            customerName="Acme Corp",
            items=[OrderItem(productCode="PROD-001", quantity=10, price=999.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("out of range" in issue.lower() for issue in result.issues)

    @pytest.mark.asyncio
    async def test_zero_stock_product_fails(self):
        order = ExtractedOrderData(
            customerName="Acme Corp",
            items=[OrderItem(productCode="PROD-003", quantity=1, price=199.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("insufficient" in issue.lower() for issue in result.issues)

    @pytest.mark.asyncio
    async def test_missing_customer_name_fails(self):
        order = ExtractedOrderData(
            customerName="",
            items=[OrderItem(productCode="PROD-001", quantity=10, price=99.99)],
            deliveryDate="2024-06-15",
            confidence=0.9,
        )
        result = await validate_order(order)
        assert result.finalStatus == "fail"
        assert any("missing" in issue.lower() for issue in result.issues)
