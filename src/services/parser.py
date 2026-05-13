import json
import logging
import re

from openai import AsyncOpenAI

from src.core.config import settings
from src.models.invoice import InvoiceData

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are an invoice data extraction expert. \
Given the raw text from an invoice, extract all structured data as JSON.

Extract the following fields:
- vendor_name: Company/person who issued the invoice
- vendor_address: Full address of the vendor
- invoice_number: Invoice/receipt number
- invoice_date: Date the invoice was issued (YYYY-MM-DD format)
- due_date: Payment due date (YYYY-MM-DD format)
- customer_name: Name of the customer/buyer
- customer_address: Full address of the customer
- line_items: Array of items, each with: description, quantity, unit_price, total
- subtotal: Subtotal before tax
- tax_rate: Tax percentage (as decimal, e.g. 0.21 for 21%)
- tax_amount: Total tax amount
- total_amount: Final total amount
- currency: Currency code (EUR, USD, GBP, etc.)
- payment_terms: Payment terms if mentioned
- notes: Any additional notes

If a field cannot be determined, use an empty string for text fields, \
null for numeric fields, and an empty array for line_items.

Return ONLY valid JSON, no markdown formatting or explanation.

Raw invoice text:
{text}"""


async def parse_with_ai(raw_text: str) -> InvoiceData:
    if not settings.openai_api_key:
        logger.warning("No OpenAI API key configured, using regex fallback")
        return parse_with_regex(raw_text)

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You extract structured data from invoices. Return only valid JSON.",
                },
                {"role": "user", "content": EXTRACTION_PROMPT.format(text=raw_text)},
            ],
            temperature=0.1,
            max_tokens=2000,
        )

        content = response.choices[0].message.content.strip()
        # Remove markdown code block if present
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n?", "", content)
            content = re.sub(r"\n?```$", "", content)

        data = json.loads(content)
        return InvoiceData(**data)

    except Exception as e:
        logger.error(f"AI parsing failed: {e}, falling back to regex")
        return parse_with_regex(raw_text)


def parse_with_regex(raw_text: str) -> InvoiceData:
    """Fallback parser using regex patterns when OpenAI is not available."""
    data = InvoiceData()

    # Invoice number patterns
    inv_match = re.search(
        r"(?:invoice|factura|receipt|recibo)\s*[#:nN°ºo.]*\s*([A-Z0-9\-/]+)",
        raw_text,
        re.IGNORECASE,
    )
    if inv_match:
        data.invoice_number = inv_match.group(1).strip()

    # Date patterns (various formats)
    date_match = re.search(
        r"(?:date|fecha|issued)[\s:]*(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})", raw_text, re.IGNORECASE
    )
    if date_match:
        data.invoice_date = date_match.group(1).strip()

    # Due date
    due_match = re.search(
        r"(?:due|vencimiento|payment)[\s:]*(?:date)?[\s:]*(\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4})",
        raw_text,
        re.IGNORECASE,
    )
    if due_match:
        data.due_date = due_match.group(1).strip()

    # Total amount (use negative lookbehind to avoid matching "Subtotal")
    total_match = re.search(
        r"(?<!sub)(?:total|importe total|grand total)[\s:]*[$€£]?\s*([\d,.]+)",
        raw_text,
        re.IGNORECASE,
    )
    if total_match:
        amount_str = total_match.group(1).replace(",", "")
        try:
            data.total_amount = float(amount_str)
        except ValueError:
            pass

    # Currency detection
    if "€" in raw_text or "EUR" in raw_text:
        data.currency = "EUR"
    elif "$" in raw_text or "USD" in raw_text:
        data.currency = "USD"
    elif "£" in raw_text or "GBP" in raw_text:
        data.currency = "GBP"

    # Tax
    tax_match = re.search(
        r"(?:tax|iva|vat|impuesto)[\s:]*[$€£]?\s*([\d,.]+)", raw_text, re.IGNORECASE
    )
    if tax_match:
        amount_str = tax_match.group(1).replace(",", "")
        try:
            data.tax_amount = float(amount_str)
        except ValueError:
            pass

    return data
