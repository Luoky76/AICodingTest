"""Main processing pipeline.

Orchestrates: Input → Content Parsing → AI Extraction → Data Validation → Result Output
"""

from __future__ import annotations

from app.models.schemas import (
    FinalOutput,
    OrderInput,
    ValidationResult,
)
from app.services.extractor import extract_order
from app.services.parser import parse_content
from app.services.validator import validate_order

# Suggestion text for each status
_SUGGESTIONS: dict[str, str] = {
    "pass": "建议创建订单",
    "fail": "存在异常，需人工处理",
    "manual": "信息不完整，需人工确认",
}


async def process_order(order_input: OrderInput) -> FinalOutput:
    """Execute the full order processing pipeline.

    Pipeline: Input → Content Parsing → AI Extraction → Data Validation → Result Output

    Args:
        order_input: The raw order input (email or excel).

    Returns:
        FinalOutput with extracted data, validation result, and suggestion.

    Raises:
        ValueError: If input is invalid.
        RuntimeError: If processing fails.
    """
    # Step 1: Content Parsing
    parsed = parse_content(order_input)

    # Step 2: AI Extraction
    extracted = await extract_order(parsed)

    # Step 3: Data Validation
    validation = await validate_order(extracted)

    # Step 4: Generate suggestion
    suggestion = _SUGGESTIONS.get(validation.finalStatus, "未知状态")

    # Step 5: Assemble final output
    # Strip confidence from validation result for final output (per PRD 5.5)
    validation_output = ValidationResult(
        finalStatus=validation.finalStatus,
        confidence=validation.confidence,
        issues=validation.issues,
    )

    return FinalOutput(
        extractedData=extracted,
        validationResult=validation_output,
        suggestion=suggestion,
    )
