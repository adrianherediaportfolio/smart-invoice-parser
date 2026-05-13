import io
import logging

import pdfplumber
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/tiff", "image/bmp"}
SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_TYPES = SUPPORTED_IMAGE_TYPES | SUPPORTED_PDF_TYPES


def extract_text_from_image(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    texts = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texts.append(page_text)
            else:
                # Fallback to OCR if no text layer
                img = page.to_image(resolution=300)
                pil_image = img.original
                ocr_text = pytesseract.image_to_string(pil_image, lang="eng")
                if ocr_text.strip():
                    texts.append(ocr_text.strip())
    return "\n\n".join(texts)


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type in SUPPORTED_PDF_TYPES:
        logger.info("Extracting text from PDF")
        return extract_text_from_pdf(file_bytes)
    elif content_type in SUPPORTED_IMAGE_TYPES:
        logger.info("Extracting text from image")
        return extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {content_type}")
