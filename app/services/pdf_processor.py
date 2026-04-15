from pypdf import PdfReader, PdfWriter
from PIL import Image
import img2pdf
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import io

class PDFProcessor:

    
# ---------------- IMAGES TO PDF ----------------
    
    @staticmethod
    def images_to_pdf(image_bytes_list: list[bytes]) -> bytes:
        """Image → PDF using img2pdf (pure Python)"""
        images = [Image.open(BytesIO(img)) for img in image_bytes_list]
        pdf_bytes = img2pdf.convert(images)
        return pdf_bytes
    

# ---------------- MERGE ----------------

    @staticmethod
    def merge_pdfs(pdf_bytes_list: list[bytes]) -> bytes:
        writer = PdfWriter()

        for pdf_bytes in pdf_bytes_list:
            reader = PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return output.read()

    
# ---------------- COMPRESS ----------------
    @staticmethod
    def compress_pdf(pdf_bytes: bytes, level: str) -> bytes:
        reader = PdfReader(BytesIO(pdf_bytes))
        writer = PdfWriter()

        # Map levels to optimization strength
        compression_map = {
            "30": {"optimize": False},
            "50": {"optimize": True},
            "80": {"optimize": True}
        }

        settings = compression_map.get(level, {"optimize": True})

        for page in reader.pages:
            writer.add_page(page)

        output = BytesIO()
        writer.write(output, **settings)
        output.seek(0)

        return output.read()

