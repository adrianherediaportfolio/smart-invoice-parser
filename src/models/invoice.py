from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = ""
    quantity: float | None = None
    unit_price: float | None = None
    total: float | None = None


class InvoiceData(BaseModel):
    vendor_name: str = ""
    vendor_address: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    due_date: str = ""
    customer_name: str = ""
    customer_address: str = ""
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: float | None = None
    tax_rate: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    currency: str = ""
    payment_terms: str = ""
    notes: str = ""


class InvoiceResponse(BaseModel):
    id: int
    filename: str
    data: InvoiceData
    raw_text: str
    created_at: str


class InvoiceListItem(BaseModel):
    id: int
    filename: str
    created_at: str


class ParseResponse(BaseModel):
    success: bool
    message: str
    invoice: InvoiceResponse | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: str = ""
