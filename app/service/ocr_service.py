# app/services/ocr.py
import io
import logging
from typing import List
from fastapi import UploadFile, Request
from fastapi.responses import JSONResponse
import pdfplumber
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

async def extract_text_from_image(
    request: Request,
    files: List[UploadFile],
    api_key: str
) -> JSONResponse:
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    results = []
    for file in files:
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            results.append({"filename": file.filename, "error": "File must be an image"})
            continue
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))
            text = pytesseract.image_to_string(image)
            results.append({"filename": file.filename, "text": text})
            logger.info(f"Processed image: {file.filename}")
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
            logger.error(f"Error processing {file.filename}: {e}")
    return JSONResponse(content={"results": results})

async def extract_text_from_pdf(
    request: Request,
    files: List[UploadFile],
    api_key: str
) -> JSONResponse:
    results = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            results.append({"filename": file.filename, "error": "File must be a PDF"})
            continue
        try:
            contents = await file.read()
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages])
            results.append({"filename": file.filename, "text": text})
            logger.info(f"Processed PDF: {file.filename}")
        except Exception as e:
            results.append({"filename": file.filename, "error": str(e)})
            logger.error(f"Error processing {file.filename}: {e}")
    return JSONResponse(content={"results": results})
