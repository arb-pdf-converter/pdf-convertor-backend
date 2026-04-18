from pypdf import PdfReader, PdfWriter
from pikepdf import Pdf, ObjectStreamMode  # 👈 ADD PIKEPDF
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
        """Real PDF compression using pikepdf"""
        try:
            compression_map = {
                "30": {"image_quality": 85, "downsample": False},
                "50": {"image_quality": 75, "downsample": True},
                "80": {"image_quality": 60, "downsample": True}
            }
            settings = compression_map.get(level, {"image_quality": 75, "downsample": True})
            
            pdf = Pdf.open(BytesIO(pdf_bytes))
            
            # Save with compression
            output = BytesIO()
            pdf.save(
                output,
                object_stream_mode=ObjectStreamMode.generate,
                normalize_content=True,
                remove_duplicate_objects=True,
                image_quality=settings["image_quality"],
                downsample_images=settings["downsample"],
                jpeg_filter=True
            )
            output.seek(0)
            
            result = output.read()
            print(f"Compression {level}: {len(pdf_bytes)/1024:.1f}KB → {len(result)/1024:.1f}KB")
            return result
            
        except Exception as e:
            print(f"Compression failed: {e}")
            return pdf_bytes  # Return original if compression fails
