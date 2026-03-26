"""Pydantic data models for the order extraction and verification system."""

from __future__ import annotations

from pydantic import BaseModel, Field


# --- Input Models ---

class AttachmentInput(BaseModel):
    """Email attachment."""
    fileName: str
    fileContent: str  # base64 encoded or text


class EmailInput(BaseModel):
    """Email input format."""
    type: str = Field("email", pattern="^email$")
    subject: str = ""
    body: str = ""
    attachments: list[AttachmentInput] = []


class ExcelInput(BaseModel):
    """Excel input format."""
    type: str = Field("excel", pattern="^excel$")
    fileName: str = ""
    fileContent: str = ""  # base64 encoded


class OrderInput(BaseModel):
    """Unified order input that can be email or excel."""
    type: str = Field(..., pattern="^(email|excel)$")
    subject: str | None = None
    body: str | None = None
    attachments: list[AttachmentInput] | None = None
    fileName: str | None = None
    fileContent: str | None = None


# --- Parsed Content ---

class ParsedContent(BaseModel):
    """Output of the content parser."""
    rawText: str


# --- Extracted Order Data ---

class OrderItem(BaseModel):
    """Single item in an order."""
    productCode: str
    quantity: float
    price: float


class ExtractedOrderData(BaseModel):
    """Structured order data extracted by AI."""
    customerName: str = ""
    items: list[OrderItem] = []
    deliveryDate: str = ""
    confidence: float = 0.0


# --- Validation Results ---

class ValidationResult(BaseModel):
    """Result of all validation checks."""
    finalStatus: str = Field(..., pattern="^(pass|fail|manual)$")
    confidence: float = 0.0
    issues: list[str] = []


# --- Final Output ---

class FinalOutput(BaseModel):
    """Complete processing result."""
    extractedData: ExtractedOrderData
    validationResult: ValidationResult
    suggestion: str


# --- Error Response ---

class ErrorResponse(BaseModel):
    """Unified error response format."""
    error: bool = True
    message: str


# --- External Service Models ---

class CustomerInfo(BaseModel):
    """Customer query result."""
    exists: bool
    active: bool


class InventoryInfo(BaseModel):
    """Inventory query result."""
    productCode: str
    availableQuantity: float


class PriceInfo(BaseModel):
    """Price query result."""
    productCode: str
    standardPrice: float
    minPrice: float
    maxPrice: float
