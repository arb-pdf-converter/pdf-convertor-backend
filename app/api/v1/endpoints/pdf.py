from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
from app.services.pdf_processor import PDFProcessor

router = APIRouter()

@router.post("/images-to-pdf")
async def images_to_pdf(files: list[UploadFile] = File(...)):
    """Convert multiple images to single PDF"""
    try:
        image_bytes_list = []
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(400, "Only image files allowed")
            content = await file.read()
            image_bytes_list.append(content)
        
        pdf_bytes = PDFProcessor.images_to_pdf(image_bytes_list)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=converted.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, f"Conversion failed: {str(e)}")

@router.post("/merge-pdf")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    """Merge multiple PDFs into one"""
    try:
        if len(files) < 2:
            raise HTTPException(400, "Need at least 2 PDFs to merge")
        
        pdf_bytes_list = []
        for file in files:
            if not file.content_type == "application/pdf":
                raise HTTPException(400, "Only PDF files allowed")
            content = await file.read()
            pdf_bytes_list.append(content)
        
        merged_bytes = PDFProcessor.merge_pdfs(pdf_bytes_list)
        
        return StreamingResponse(
            io.BytesIO(merged_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=merged.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, f"Merge failed: {str(e)}")

@router.post("/compress-pdf")
async def compress_pdf(file: UploadFile = File(...), level: int = 4):
    """Compress single PDF"""
    try:
        if not file.content_type == "application/pdf":
            raise HTTPException(400, "Only PDF files allowed")
        
        content = await file.read()
        compressed_bytes = PDFProcessor.compress_pdf(content, level)
        
        return StreamingResponse(
            io.BytesIO(compressed_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=compressed.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, f"Compression failed: {str(e)}")
