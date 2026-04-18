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

    def final_optimize(input_path):
        output_path = f"/tmp/final_{uuid.uuid4().hex}.pdf"

        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",

            # 🔥 final compression pass
            "-dPDFSETTINGS=/screen",

            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",

            f"-sOutputFile={output_path}",
            input_path
        ]

        subprocess.run(cmd, check=True)
        return output_path

    def compress_pdf(input_path):
        step1 = compress_pdf_ilovepdf(input_path, "/tmp/step1.pdf")
        step2 = final_optimize(step1)
        return step2
    
