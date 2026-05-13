import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.core.config import settings
from src.core.database import get_invoice, list_invoices, save_invoice
from src.models.invoice import (
    ErrorResponse,
    InvoiceData,
    InvoiceListItem,
    InvoiceResponse,
    ParseResponse,
)
from src.services.ocr import SUPPORTED_TYPES, extract_text
from src.services.parser import parse_with_ai

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["invoices"])


@router.post(
    "/parse",
    response_model=ParseResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def parse_invoice(file: UploadFile = File(...)) -> ParseResponse:
    """Upload and parse an invoice PDF or image.

    Supported formats: PDF, PNG, JPEG, TIFF, BMP.
    Returns structured invoice data extracted via OCR + AI.
    """
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. "
            f"Supported: {', '.join(sorted(SUPPORTED_TYPES))}",
        )

    file_bytes = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb} MB",
        )

    try:
        raw_text = extract_text(file_bytes, file.content_type)
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the document. "
            "Ensure the file contains readable text or a clear image.",
        )

    try:
        parsed_data: InvoiceData = await parse_with_ai(raw_text)
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice parsing failed: {str(e)}")

    invoice_id = await save_invoice(
        filename=file.filename or "unknown",
        parsed_data=parsed_data.model_dump(),
        raw_text=raw_text,
    )

    return ParseResponse(
        success=True,
        message="Invoice parsed successfully",
        invoice=InvoiceResponse(
            id=invoice_id,
            filename=file.filename or "unknown",
            data=parsed_data,
            raw_text=raw_text,
            created_at="",
        ),
    )


@router.get("/invoices", response_model=list[InvoiceListItem])
async def get_invoices(limit: int = 50, offset: int = 0) -> list[InvoiceListItem]:
    """List all parsed invoices."""
    rows = await list_invoices(limit=limit, offset=offset)
    return [InvoiceListItem(**row) for row in rows]


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_invoice_by_id(invoice_id: int) -> InvoiceResponse:
    """Get a specific parsed invoice by ID."""
    invoice = await get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return InvoiceResponse(
        id=invoice["id"],
        filename=invoice["filename"],
        data=InvoiceData(**invoice["parsed_data"]),
        raw_text=invoice["raw_text"],
        created_at=invoice["created_at"],
    )
