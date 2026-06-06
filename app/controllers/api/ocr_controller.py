from app.service import ocr_service
from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import JSONResponse
from app.dependencies.auth import get_api_key
from typing import List

router = APIRouter(prefix="/extract", tags=["OCR"])


@router.post("/image")
async def ocr_image(
    request: Request,
    files: List[UploadFile] = File(...),
    api_key: str = Depends(get_api_key)
):
    return await ocr_service.extract_text_from_image(request, files, api_key)

@router.post("/pdf")
async def ocr_pdf(
    request: Request,
    files: List[UploadFile] = File(...),
    api_key: str = Depends(get_api_key)
):
    return await ocr_service.extract_text_from_pdf(request, files, api_key)
