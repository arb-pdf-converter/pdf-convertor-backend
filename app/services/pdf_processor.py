import subprocess
import tempfile
import uuid
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
    def compress_pdf(input_path: str, quality: str = "ebook"):
    output_path = f"/tmp/compressed_{uuid.uuid4().hex}.pdf"

    quality_map = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress"
    }

    cmd = [
    "gs",
    "-sDEVICE=pdfwrite",
    "-dCompatibilityLevel=1.4",

    # 🔥 MAX compression
    "-dPDFSETTINGS=/screen",

    "-dDownsampleColorImages=true",
    "-dColorImageResolution=72",

    "-dDownsampleGrayImages=true",
    "-dGrayImageResolution=72",

    "-dDownsampleMonoImages=true",
    "-dMonoImageResolution=72",

    "-dColorImageFilter=/DCTEncode",
    "-dGrayImageFilter=/DCTEncode",
    "-dDetectDuplicateImages=true",
    "-dCompressFonts=true",
    "-dSubsetFonts=true",
    "-dNOPAUSE",
    "-dBATCH",
    "-dQUIET",

    f"-sOutputFile={output_path}",
    input_path
]
    subprocess.run(cmd, check=True)

    return output_path
