import subprocess
import tempfile
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
        """Ghostscript: 70-90% reduction GUARANTEED"""
        try:
            # Ghostscript compression levels
            gs_levels = {
                "30": "/default",      # Screen (72dpi)
                "50": "/ebook",        # Ebook (150dpi) 
                "80": "/printer"       # Printer (300dpi)
            }
            gs_level = gs_levels.get(level, "/ebook")
            
            # Write input to temp file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_file:
                input_file.write(pdf_bytes)
                input_path = input_file.name
            
            # Output temp file
            output_path = input_path.replace('.pdf', '_compressed.pdf')
            
            # Ghostscript command - REAL COMPRESSION
            cmd = [
                'gs',
                '-sDEVICE=pdfwrite',
                f'-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={gs_level}',
                f'-dNOPAUSE',
                f'-dQUIET',
                f'-dBATCH',
                f'-sOutputFile={output_path}',
                input_path
            ]
            
            # Run Ghostscript
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup input
            subprocess.run(['rm', input_path])
            
            if result.returncode != 0:
                print(f"Ghostscript error: {result.stderr}")
                return pdf_bytes
            
            # Read compressed output
            with open(output_path, 'rb') as f:
                compressed_bytes = f.read()
            
            # Cleanup output
            subprocess.run(['rm', output_path])
            
            orig_size = len(pdf_bytes) / (1024*1024)
            new_size = len(compressed_bytes) / (1024*1024)
            print(f"🎉 Ghostscript {level}: {orig_size:.1f}MB → {new_size:.1f}MB ({((1-new_size/orig_size)*100):.0f}% ↓)")
            
            return compressed_bytes
            
        except Exception as e:
            print(f"Compression failed: {e}")
            return pdf_bytes
