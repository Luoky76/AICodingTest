"""Data validation service.

Implements the three required validation checks:
1. Customer validation
2. Inventory validation
3. Price validation
"""

from __future__ import annotations

from app.external.customer_client import query_customer
from app.external.inventory_client import query_inventory
from app.external.price_client import query_price
from app.models.schemas import ExtractedOrderData, ValidationResult


async def validate_order(extracted: ExtractedOrderData) -> ValidationResult:
    """Run all validations on extracted order data.

    Follows the judgment rules from the PRD:
      - confidence < 0.8 → finalStatus = manual
      - any validation fails → finalStatus = fail
      - otherwise → finalStatus = pass

    Args:
        extracted: The extracted order data to validate.

    Returns:
        ValidationResult with status and any issues found.
    """
    issues: list[str] = []

    # Check confidence first
    if extracted.confidence < 0.8:
        return ValidationResult(
            finalStatus="manual",
            confidence=extracted.confidence,
            issues=["AI extraction confidence is below threshold (< 0.8), manual review required"],
        )

    # 5.3.1 Customer validation
    if extracted.customerName:
        customer_issues = await _validate_customer(extracted.customerName)
        issues.extend(customer_issues)
    else:
        issues.append("Customer name is missing")

    # 5.3.2 & 5.3.3 Item validations (inventory + price)
    for item in extracted.items:
        inv_issues = await _validate_inventory(item.productCode, item.quantity)
        issues.extend(inv_issues)

        price_issues = await _validate_price(item.productCode, item.price)
        issues.extend(price_issues)

    # Determine final status
    if issues:
        final_status = "fail"
    else:
        final_status = "pass"

    return ValidationResult(
        finalStatus=final_status,
        confidence=extracted.confidence,
        issues=issues,
    )


async def _validate_customer(customer_name: str) -> list[str]:
    """Validate customer existence and status."""
    issues: list[str] = []

    try:
        info = await query_customer(customer_name)
        if not info.exists:
            issues.append(f"Customer '{customer_name}' does not exist")
        elif not info.active:
            issues.append(f"Customer '{customer_name}' is inactive")
    except Exception as e:
        issues.append(f"Customer validation failed: {e}")

    return issues


async def _validate_inventory(product_code: str, quantity: float) -> list[str]:
    """Validate that inventory is sufficient."""
    issues: list[str] = []

    try:
        info = await query_inventory(product_code)
        if info.availableQuantity < 0:
            issues.append(f"Product '{product_code}' not found in inventory")
        elif info.availableQuantity < quantity:
            issues.append(
                f"Insufficient inventory for '{product_code}': "
                f"available={info.availableQuantity}, required={quantity}"
            )
    except Exception as e:
        issues.append(f"Inventory validation failed for '{product_code}': {e}")

    return issues


async def _validate_price(product_code: str, price: float) -> list[str]:
    """Validate that price is within allowed range."""
    issues: list[str] = []

    try:
        info = await query_price(product_code)
        if info.standardPrice <= 0:
            issues.append(f"No standard price found for '{product_code}'")
        elif price < info.minPrice or price > info.maxPrice:
            issues.append(
                f"Price for '{product_code}' is out of range: "
                f"price={price}, allowed=[{info.minPrice}, {info.maxPrice}]"
            )
    except Exception as e:
        issues.append(f"Price validation failed for '{product_code}': {e}")

    return issues
