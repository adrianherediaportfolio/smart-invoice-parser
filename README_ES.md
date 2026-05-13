# Smart Invoice Parser API

[![CI](https://github.com/adrianherediaportfolio/smart-invoice-parser/actions/workflows/ci.yml/badge.svg)](https://github.com/adrianherediaportfolio/smart-invoice-parser/actions)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Una API REST que extrae datos estructurados de facturas en PDF e imagenes usando **OCR (Tesseract)** + **IA (OpenAI)**. Sube cualquier factura y obtendras JSON estructurado con datos del proveedor, lineas de detalle, totales y mas.

## Caracteristicas

- **Soporte PDF e Imagenes** — Sube facturas en PDF, PNG, JPEG, TIFF o BMP
- **Motor de Extraccion Dual** — OCR via Tesseract + parseo inteligente con IA de OpenAI
- **Fallback con Regex** — Funciona sin clave de OpenAI usando extraccion por patrones
- **Interfaz Web** — Interfaz de arrastrar y soltar integrada para pruebas rapidas
- **API REST** — API CRUD completa con documentacion Swagger
- **Almacenamiento Persistente** — Base de datos SQLite guarda todas las facturas parseadas
- **Docker Ready** — Despliegue con un solo comando usando Docker Compose
- **OCR Multi-idioma** — Soporta facturas en ingles y espanol

## Inicio Rapido

### Requisitos

- Python 3.11+
- Tesseract OCR (`sudo apt install tesseract-ocr` en Ubuntu)

### Instalacion

```bash
git clone https://github.com/adrianherediaportfolio/smart-invoice-parser.git
cd smart-invoice-parser

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install ".[dev]"

# Configurar entorno
cp .env.example .env
# Edita .env y anade tu OPENAI_API_KEY (opcional — el fallback con regex funciona sin ella)

# Ejecutar el servidor
uvicorn src.main:app --reload
```

La API estara disponible en `http://localhost:8000`.

### Docker

```bash
cp .env.example .env
# Edita .env con tu configuracion
docker compose up -d
```

## Documentacion de la API

Documentacion interactiva disponible en `http://localhost:8000/docs` (Swagger UI) o `http://localhost:8000/redoc`.

### Endpoints

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| `POST` | `/api/v1/parse` | Sube y parsea una factura |
| `GET` | `/api/v1/invoices` | Lista todas las facturas parseadas |
| `GET` | `/api/v1/invoices/{id}` | Obtiene una factura especifica |
| `GET` | `/health` | Verificacion de salud |

### Parsear una Factura

```bash
curl -X POST http://localhost:8000/api/v1/parse \
  -F "file=@factura.pdf"
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Invoice parsed successfully",
  "invoice": {
    "id": 1,
    "filename": "factura.pdf",
    "data": {
      "vendor_name": "Acme Corp",
      "invoice_number": "INV-2024-001",
      "invoice_date": "2024-03-15",
      "due_date": "2024-04-15",
      "line_items": [
        {
          "description": "Servicios de Desarrollo Web",
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

## Estructura del Proyecto

```
smart-invoice-parser/
├── src/
│   ├── api/
│   │   └── routes.py          # Endpoints de la API
│   ├── core/
│   │   ├── config.py          # Gestion de configuracion
│   │   └── database.py        # Operaciones SQLite
│   ├── models/
│   │   └── invoice.py         # Modelos Pydantic
│   ├── services/
│   │   ├── ocr.py             # Extraccion de texto (Tesseract + pdfplumber)
│   │   └── parser.py          # Parseo con IA + regex
│   └── main.py                # Punto de entrada FastAPI
├── templates/
│   └── index.html             # Interfaz web
├── tests/
│   ├── test_api.py            # Tests de integracion de la API
│   └── test_parser.py         # Tests unitarios del parser
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```

## Ejecutar Tests

```bash
pytest tests/ -v
```

## Stack Tecnologico

- **[FastAPI](https://fastapi.tiangolo.com)** — Framework web asincrono moderno para Python
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** — Motor OCR open-source
- **[pdfplumber](https://github.com/jsvine/pdfplumber)** — Extraccion de texto de PDFs
- **[OpenAI API](https://openai.com)** — Extraccion inteligente de campos
- **[SQLite](https://sqlite.org)** — Base de datos embebida ligera
- **[Pydantic](https://pydantic.dev)** — Validacion y serializacion de datos

## Licencia

MIT — ver [LICENSE](LICENSE).
