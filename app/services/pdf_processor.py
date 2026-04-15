import fitz  # PyMuPDF
from PIL import Image
import img2pdf
from PyPDF2 import PdfMerger
from io import BytesIO
import tempfile

class PDFProcessor:
    
    @staticmethod
    def images_to_pdf(image_bytes_list: list[bytes]) -> bytes:
        """Convert list of image bytes to PDF"""
        images = [Image.open(BytesIO(img)) for img in image_bytes_list]
        pdf_bytes = img2pdf.convert(images)
        return pdf_bytes
    
    @staticmethod
    def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
        """Merge multiple PDFs"""
        merger = PdfMerger()
        for pdf_bytes in pdf_bytes_list:
            merger.append(BytesIO(pdf_bytes))
        output = BytesIO()
        merger.write(output)
        merger.close()
        return output.getvalue()
    
    @staticmethod
    def compress_pdf(pdf_bytes: bytes, level: int = 4) -> bytes:
        """Compress PDF (1-9, higher = more compression)"""
        doc = fitz.open("pdf", pdf_bytes)
        doc.saveIncr(garbage=level, deflate=True, clean=True)
        compressed_bytes = doc.tobytes("pdf")
        doc.close()
        return compressed_bytes
