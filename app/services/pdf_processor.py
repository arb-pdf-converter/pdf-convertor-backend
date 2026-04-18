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
        """Ghostscript with proper error handling"""
        import os
        import tempfile
        import subprocess
    
        try:
            # Ghostscript settings
            gs_settings = {
                "30": "/screen",     # 72 DPI
                "50": "/ebook",      # 150 DPI  
                "80": "/printer"     # 300 DPI
            }
            if level == "30":
                resolution = "72"
            elif level == "50":
                resolution = "150"
            else:
                resolution = "300"
        
            # Create secure temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = os.path.join(temp_dir, "input.pdf")
                output_path = os.path.join(temp_dir, "output.pdf")
            
                # Write input
                with open(input_path, "wb") as f:
                    f.write(pdf_bytes)
            
                # Ghostscript command
                cmd = [
                    "gs",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    "-dNOPAUSE",
                    "-dBATCH",
                    "-dSAFER",

                # 🔥 FORCE real compression
                    "-dDetectDuplicateImages=true",
                    "-dCompressFonts=true",
                    "-dSubsetFonts=true",

                # 🔥 Image compression
                    "-dDownsampleColorImages=true",
                    "-dDownsampleGrayImages=true",
                    "-dDownsampleMonoImages=true",

                    "-dColorImageDownsampleType=/Bicubic",
                    "-dGrayImageDownsampleType=/Bicubic",
                    "-dMonoImageDownsampleType=/Bicubic",

                    f"-dColorImageResolution={resolution}",
                    f"-dGrayImageResolution={resolution}",
                    f"-dMonoImageResolution={resolution}",

                    f"-sOutputFile={output_path}",
                    input_path
                ]
                # Execute
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True,
                    timeout=60
                )
            
                # Check output file exists and has size
                if not os.path.exists(output_path):
                    print("❌ Ghostscript: No output file")
                    return pdf_bytes
            
                output_size = os.path.getsize(output_path)
                if output_size < 1024:  # Less than 1KB = failed
                    print("❌ Ghostscript: Output too small")
                    return pdf_bytes
            
                # Read result
                with open(output_path, "rb") as f:
                    compressed_bytes = f.read()
            
                orig_size = len(pdf_bytes) / (1024*1024)
                new_size = len(compressed_bytes) / (1024*1024)
            
                print(f"🎉 SUCCESS {level}: {orig_size:.1f}MB → {new_size:.1f}MB")
                return compressed_bytes
            
        except subprocess.TimeoutExpired:
            print("⏰ Ghostscript timeout")
            return pdf_bytes
        except Exception as e:
            print(f"❌ Error: {e}")
            return pdf_bytes
