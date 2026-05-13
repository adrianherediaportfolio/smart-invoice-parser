# Smart Invoice Parser API

[![CI](https://github.com/adrianherediaportfolio/smart-invoice-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianherediaportfolio/smart-invoice-parser/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A REST API that extracts structured data from invoice PDFs and images using **OCR (Tesseract)** + **AI (OpenAI)**. Upload any invoice and get back clean, structured JSON with vendor info, line items, totals, and more.

## Features

- **PDF & Image Support** — Upload PDF, PNG, JPEG, TIFF, or BMP invoices
- **Dual Extraction Engine** — OCR via Tesseract + intelligent AI parsing via OpenAI
- **Regex Fallback** — Works without an OpenAI key using pattern-based extraction
- **Web UI** — Built-in drag-and-drop upload interface for quick testing
- **REST API** — Full CRUD API with Swagger documentation
- **Persistent Storage** — SQLite database stores all parsed invoices
- **Docker Ready** — One-command deployment with Docker Compose
- **Multi-language OCR** — Supports English and Spanish invoices

## Quick Start

### Prerequisites

- Python 3.11+
- Tesseract OCR (`sudo apt install tesseract-ocr` on Ubuntu)

### Installation

```bash
git clone https://github.com/adrianherediaportfolio/smart-invoice-parser.git
cd smart-invoice-parser

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional — regex fallback works without it)

# Run the server
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

### Docker

```bash
cp .env.example .env
# Edit .env with your settings
docker compose up -d
```

## API Documentation

Interactive docs available at `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc`.

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/parse` | Upload and parse an invoice |
| `GET` | `/api/v1/invoices` | List all parsed invoices |
| `GET` | `/api/v1/invoices/{id}` | Get a specific invoice |
| `GET` | `/health` | Health check |

### Parse an Invoice

```bash
curl -X POST http://localhost:8000/api/v1/parse \
  -F "file=@invoice.pdf"
```

**Response:**

```json
{
  "success": true,
  "message": "Invoice parsed successfully",
  "invoice": {
    "id": 1,
    "filename": "invoice.pdf",
    "data": {
      "vendor_name": "Acme Corp",
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-03-15",
      "due_date": "2024-04-15",
      "line_items": [
        {
          "description": "Web Development Services",
          "quantity": 40,
          "unit_price": 75.00,
          "total": 3000.00
        }
      ],
      "subtotal": 3000.00,
      "tax_rate": 0.21,
      "tax_amount": 630.00,
      "total_amount": 3630.00,
      "currency": "EUR"
    }
  }
}
```

## Project Structure

```
smart-invoice-parser/
├── src/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── config.py          # Settings management
│   │   └── database.py        # SQLite operations
│   ├── models/
│   │   └── invoice.py         # Pydantic models
│   ├── services/
│   │   ├── ocr.py             # Text extraction (Tesseract + pdfplumber)
│   │   └── parser.py          # AI + regex parsing
│   └── main.py                # FastAPI app entry point
├── templates/
│   └── index.html             # Web UI
├── tests/
│   ├── test_api.py            # API integration tests
│   └── test_parser.py         # Parser unit tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Running Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com)** — Modern async Python web framework
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** — Open-source OCR engine
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — PDF text extraction
- **[OpenAI API](https://openai.com)** — Intelligent field extraction
- **[SQLite](https://sqlite.org)** — Lightweight embedded database
- **[Pydantic](https://pydantic.dev)** — Data validation and serialization

## License

MIT — see [LICENSE](LICENSE).
