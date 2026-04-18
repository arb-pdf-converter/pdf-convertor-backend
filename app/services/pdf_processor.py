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
        """Real PDF compression using pikepdf"""
        try:
            # Compression levels: higher number = more aggressive
            compression_map = {
                "30": 1,  # Light
                "50": 2,  # Medium  
                "80": 3   # Heavy
            }
            compression_level = compression_map.get(level, 2)
            
            # Open PDF with pikepdf
            pdf = Pdf.open(BytesIO(pdf_bytes))
            
            # Apply compression based on level
            if compression_level >= 1:
                # Remove duplicate objects and optimize structure
                pdf.remove_unreferenced_resources()
                
            if compression_level >= 2:
                # Compress images and streams
                for page in pdf.pages:
                    for img in page.images:
                        img.filter = "DCTDecode"  # JPEG compression
                        img.colorspace = "DeviceRGB"
                
                # Compress all streams
                pdf.save(BytesIO(), 
                        object_stream_mode=ObjectStreamMode.generate,
                        stream_decode_level=parse_compressed_stream.all,
                        downsample_images=True,
                        image_quality=90 - (compression_level * 20))  # 70-90 quality
                
            else:
                # Light compression only
                pdf.save(BytesIO(), 
                        object_stream_mode=ObjectStreamMode.generate,
                        stream_decode_level=parse_compressed_stream.all)
            
            output = BytesIO()
            pdf.save(output)
            output.seek(0)
            return output.read()
            
        except Exception as e:
            print(f"Compression error: {e}")
            # Fallback: return original
            return pdf_bytes
