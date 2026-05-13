from src.services.parser import parse_with_regex


def test_regex_parser_extracts_invoice_number():
    text = "Invoice #INV-2024-001\nDate: 2024-03-15\nTotal: $1,250.00"
    result = parse_with_regex(text)
    assert result.invoice_number == "INV-2024-001"


def test_regex_parser_extracts_date():
    text = "Invoice #001\nDate: 2024-03-15\nDue Date: 2024-04-15"
    result = parse_with_regex(text)
    assert result.invoice_date == "2024-03-15"
    assert result.due_date == "2024-04-15"


def test_regex_parser_extracts_total():
    text = "Subtotal: $1,000.00\nTax: $210.00\nTotal: $1,210.00"
    result = parse_with_regex(text)
    assert result.total_amount == 1210.00


def test_regex_parser_detects_eur_currency():
    text = "Total: €500.00"
    result = parse_with_regex(text)
    assert result.currency == "EUR"


def test_regex_parser_detects_usd_currency():
    text = "Total: $500.00"
    result = parse_with_regex(text)
    assert result.currency == "USD"


def test_regex_parser_detects_gbp_currency():
    text = "Total: £500.00"
    result = parse_with_regex(text)
    assert result.currency == "GBP"


def test_regex_parser_extracts_tax():
    text = "Tax: $105.00\nTotal: $1,105.00"
    result = parse_with_regex(text)
    assert result.tax_amount == 105.00


def test_regex_parser_handles_empty_text():
    result = parse_with_regex("")
    assert result.invoice_number == ""
    assert result.total_amount is None


def test_regex_parser_handles_spanish_invoice():
    text = "Factura N° FA-2024-100\nFecha: 2024-06-01\nImporte Total: €3,500.00\nIVA: €735.00"
    result = parse_with_regex(text)
    assert result.invoice_number == "FA-2024-100"
    assert result.total_amount == 3500.00
    assert result.currency == "EUR"
