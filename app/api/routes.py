"""API routes for the order extraction and verification system."""

from __future__ import annotations

import base64
import traceback

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.models.schemas import ErrorResponse, FinalOutput, OrderInput
from app.services.processor import process_order

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the main page."""
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/api/process", response_model=FinalOutput)
async def process_order_api(order_input: OrderInput) -> FinalOutput | JSONResponse:
    """Process an order from JSON input.

    Accepts email or excel type input and returns the full processing result.
    """
    try:
        result = await process_order(order_input)
        return result
    except (ValueError, RuntimeError) as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message=str(e)).model_dump(),
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message=f"Internal error: {str(e)}").model_dump(),
        )


@router.post("/api/upload-excel", response_model=FinalOutput)
async def upload_excel(file: UploadFile = File(...)) -> FinalOutput | JSONResponse:
    """Process an uploaded Excel file.

    Accepts an Excel file upload and processes it through the pipeline.
    """
    try:
        if not file.filename:
            raise ValueError("No file provided")

        if not file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("Only .xlsx and .xls files are supported")

        content = await file.read()
        encoded = base64.b64encode(content).decode("utf-8")

        order_input = OrderInput(
            type="excel",
            fileName=file.filename,
            fileContent=encoded,
        )

        result = await process_order(order_input)
        return result
    except (ValueError, RuntimeError) as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message=str(e)).model_dump(),
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message=f"Internal error: {str(e)}").model_dump(),
        )


@router.post("/api/process-email", response_model=FinalOutput)
async def process_email_form(
    subject: str = Form(""),
    body: str = Form(""),
    attachment: UploadFile | None = File(None),
) -> FinalOutput | JSONResponse:
    """Process an email-format order from form data.

    Accepts email subject, body, and optional attachment.
    """
    try:
        attachments = []
        if attachment and attachment.filename:
            content = await attachment.read()
            encoded = base64.b64encode(content).decode("utf-8")
            attachments.append({
                "fileName": attachment.filename,
                "fileContent": encoded,
            })

        order_input = OrderInput(
            type="email",
            subject=subject,
            body=body,
            attachments=attachments if attachments else None,
        )

        result = await process_order(order_input)
        return result
    except (ValueError, RuntimeError) as e:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(message=str(e)).model_dump(),
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message=f"Internal error: {str(e)}").model_dump(),
        )
