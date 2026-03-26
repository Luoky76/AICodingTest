"""Tests for the content parsing service."""

import base64
import io

import pytest

from app.models.schemas import OrderInput
from app.services.parser import parse_content


class TestEmailParsing:
    """Tests for email input parsing."""

    def test_parse_email_with_subject_and_body(self):
        order_input = OrderInput(
            type="email",
            subject="Order from Acme",
            body="Customer: Acme Corp\nPROD-001 | 10 | 99.99",
        )
        result = parse_content(order_input)
        assert "Subject: Order from Acme" in result.rawText
        assert "Customer: Acme Corp" in result.rawText
        assert "PROD-001" in result.rawText

    def test_parse_email_with_empty_body(self):
        order_input = OrderInput(
            type="email",
            subject="Empty Order",
            body="",
        )
        result = parse_content(order_input)
        assert "Subject: Empty Order" in result.rawText

    def test_parse_email_with_text_attachment(self):
        content = base64.b64encode(b"Attached order info").decode("utf-8")
        order_input = OrderInput(
            type="email",
            subject="Order",
            body="See attachment",
            attachments=[{"fileName": "order.txt", "fileContent": content}],
        )
        result = parse_content(order_input)
        assert "Attached order info" in result.rawText


class TestExcelParsing:
    """Tests for Excel input parsing."""

    def _make_excel_content(self) -> str:
        """Create a minimal Excel file and return base64 encoded content."""
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Orders"
        ws.append(["ProductCode", "Quantity", "Price"])
        ws.append(["PROD-001", 10, 99.99])
        ws.append(["PROD-002", 5, 49.99])

        buffer = io.BytesIO()
        wb.save(buffer)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def test_parse_excel(self):
        content = self._make_excel_content()
        order_input = OrderInput(
            type="excel",
            fileName="order.xlsx",
            fileContent=content,
        )
        result = parse_content(order_input)
        assert "ProductCode" in result.rawText
        assert "PROD-001" in result.rawText
        assert "PROD-002" in result.rawText

    def test_parse_excel_empty_content_raises(self):
        order_input = OrderInput(
            type="excel",
            fileName="order.xlsx",
            fileContent="",
        )
        with pytest.raises(ValueError, match="Excel input must have fileContent"):
            parse_content(order_input)


class TestInvalidInput:
    """Tests for invalid input handling."""

    def test_unsupported_type_raises(self):
        with pytest.raises(Exception):
            order_input = OrderInput(type="pdf")
            parse_content(order_input)
