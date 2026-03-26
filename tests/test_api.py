"""Tests for the API endpoints."""

import json

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestProcessEndpoint:
    """Tests for the /api/process endpoint."""

    def test_process_email_json(self, client):
        payload = {
            "type": "email",
            "subject": "Order - Acme Corp",
            "body": (
                "Customer: Acme Corp\n"
                "Delivery: 2024-06-15\n\n"
                "PROD-001 | 10 | 99.99\n"
                "PROD-002 | 5 | 49.99"
            ),
            "attachments": [],
        }
        response = client.post("/api/process", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Check structure matches PRD 5.5
        assert "extractedData" in data
        assert "validationResult" in data
        assert "suggestion" in data

        # Check extracted data structure
        extracted = data["extractedData"]
        assert "customerName" in extracted
        assert "items" in extracted
        assert "deliveryDate" in extracted
        assert "confidence" in extracted

        # Check validation result structure
        validation = data["validationResult"]
        assert validation["finalStatus"] in ("pass", "fail", "manual")
        assert "issues" in validation

    def test_process_invalid_type(self, client):
        payload = {"type": "pdf"}
        response = client.post("/api/process", json=payload)
        assert response.status_code == 422  # Pydantic validation error

    def test_process_email_missing_body(self, client):
        payload = {
            "type": "email",
            "subject": "",
            "body": "",
        }
        response = client.post("/api/process", json=payload)
        data = response.json()
        # Should still return a result (with low confidence)
        assert response.status_code == 200 or data.get("error")


class TestEmailFormEndpoint:
    """Tests for the /api/process-email endpoint."""

    def test_process_email_form(self, client):
        response = client.post(
            "/api/process-email",
            data={
                "subject": "Test Order",
                "body": "Customer: Acme Corp\nPROD-001 | 10 | 99.99",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "extractedData" in data
        assert "validationResult" in data


class TestIndexPage:
    """Tests for the frontend page."""

    def test_index_page_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "订单信息自动提取与验证助手" in response.text


class TestErrorFormat:
    """Tests to ensure error responses follow the unified format."""

    def test_error_response_format(self, client):
        payload = {"type": "excel", "fileName": "", "fileContent": ""}
        response = client.post("/api/process", json=payload)
        if response.status_code >= 400:
            data = response.json()
            assert "error" in data
            assert "message" in data


class TestSuggestionMapping:
    """Tests for suggestion text generation."""

    def test_pass_suggestion(self, client):
        payload = {
            "type": "email",
            "subject": "Order",
            "body": "Customer: Acme Corp\nDelivery: 2024-06-15\nPROD-001 | 10 | 99.99\nPROD-002 | 5 | 49.99",
        }
        response = client.post("/api/process", json=payload)
        data = response.json()
        status = data["validationResult"]["finalStatus"]
        if status == "pass":
            assert data["suggestion"] == "建议创建订单"
        elif status == "fail":
            assert data["suggestion"] == "存在异常，需人工处理"
        elif status == "manual":
            assert data["suggestion"] == "信息不完整，需人工确认"
