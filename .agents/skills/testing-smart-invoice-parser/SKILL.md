---
name: testing-smart-invoice-parser
description: Test the Smart Invoice Parser app end-to-end. Use when verifying UI, API, or parsing changes.
---

# Testing Smart Invoice Parser

## Prerequisites

- Python 3.11+ with virtualenv at `.venv/`
- Tesseract OCR installed (`sudo apt-get install -y tesseract-ocr`)
- No OpenAI API key required (app falls back to regex-based parsing)

## Devin Secrets Needed

- `GITHUB_PAT_PORTFOLIO` — GitHub token for adrianherediaportfolio (for PR operations)
- No other secrets required for local testing

## Starting the Server

```bash
cd /home/ubuntu/smart-invoice-parser
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Verify with: `curl -s http://localhost:8000/health`

Expected: `{"status":"healthy","service":"smart-invoice-parser","version":"X.Y.Z"}`

## Key Test Flows

### 1. UI Load Test
- Navigate to `http://localhost:8000/`
- Verify: heading "Smart Invoice Parser", drag-and-drop upload area, "Parse Invoice" button
- This tests the TemplateResponse fix (Starlette 0.40+ changed the API signature)

### 2. Invoice Upload & Parsing
- Create a test invoice image with Python PIL (or use any invoice PDF/image)
- Click the upload area, select the file
- Click "Parse Invoice"
- Verify: "Success" badge appears, parsed data shows (date, currency, total)
- Without OpenAI key, regex fallback extracts basic fields (totals, dates, currency)

### 3. Swagger Docs
- Navigate to `http://localhost:8000/docs`
- Verify: Swagger UI loads with endpoints: POST /api/v1/parse, GET /api/v1/invoices, GET /api/v1/invoices/{id}
- Check version number in the page title matches expected version

### 4. Version Verification
- Check `/health` endpoint for correct version string
- Check `/docs` page title for matching version

## Creating a Test Invoice Image

```python
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (800, 600), 'white')
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
draw.text((50, 30), 'INVOICE', fill='black', font=font)
draw.text((50, 80), 'Invoice Number: INV-2026-001', fill='black')
draw.text((50, 110), 'Date: 2026-05-13', fill='black')
draw.text((500, 440), 'TOTAL: $8,800.00', fill='black', font=font)
img.save('test-invoice.png')
```

## Known Issues

- Without OpenAI API key, line items might not be extracted (regex fallback limitation)
- The TemplateResponse API changed in Starlette 0.40+; if you see a 500 error on `/`, check that `templates.TemplateResponse(request, "index.html")` is used (not the old signature with context dict)
- Port 8000 may conflict with other services; use `fuser -k 8000/tcp` to free it

## CI

GitHub Actions runs on push/PR with a `test` job. Check CI status before merging.
