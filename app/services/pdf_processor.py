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
    def recompress_image(data):
        img = Image.open(BytesIO(data))

        if img.mode != "RGB":
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=30, optimize=True)
        return buffer.getvalue()

    def compress_pdfs(input_path: str, output_path: str):
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            # This keeps structure but does NOT fully extract images yet
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        return output_path

    def compress_pdf(input_path: str):
    output_path = f"/tmp/compressed_{uuid.uuid4().hex}.pdf"

    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",

        # 🔥 real aggressive compression
        "-dPDFSETTINGS=/screen",

        "-dDownsampleColorImages=true",
        "-dColorImageResolution=72",

        "-dDownsampleGrayImages=true",
        "-dGrayImageResolution=72",

        "-dDownsampleMonoImages=true",
        "-dMonoImageResolution=72",

        "-dDetectDuplicateImages=true",
        "-dCompressFonts=true",
        "-dSubsetFonts=true",

        "-dNOPAUSE",
        "-dBATCH",
        "-dQUIET",

        f"-sOutputFile={output_path}",
        input_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("ERROR:", result.stderr)
        raise Exception("Ghostscript failed")

    return output_path
    
