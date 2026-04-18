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
    def compress_pdf(self, input_path: str, output_path: str, quality: int = 50) -> str:
    try:
        settings = {30: '/screen', 50: '/ebook', 80: '/printer', 100: '/prepress'}
        gs_setting = settings.get(quality, '/ebook')

        print(f"🔄 Ghostscript {gs_setting} ({quality}%)...")

        cmd = [
            "gs",   # ✅ Render/Linux
            "-sDEVICE=pdfwrite",
            f"-dPDFSETTINGS={gs_setting}",
            "-dCompatibilityLevel=1.4",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode != 0:
            print("❌ GS ERROR:", result.stderr)

        if os.path.exists(output_path):
            print(f"✅ SUCCESS {gs_setting}!")
            return output_path
        else:
            raise Exception("Output not created")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return input_path
