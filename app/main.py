from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter
from io import BytesIO
import img2pdf

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "PDF API Working!"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/merge")
async def merge(files: list[UploadFile] = File(...)):

    if len(files) < 2:
        raise HTTPException(400, "Need at least 2 PDFs")

    writer = PdfWriter()

    total_pages = 0  # 👈 DEBUG SAFETY

    for file in files:
        content = await file.read()

        if len(content) < 100:
            raise HTTPException(400, f"{file.filename} is empty or invalid")

        reader = PdfReader(BytesIO(content))

        if len(reader.pages) == 0:
            raise HTTPException(400, f"{file.filename} has 0 pages")

        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1

    if total_pages == 0:
        raise HTTPException(400, "No pages found in PDFs")

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    pdf_data = output.read()

    if len(pdf_data) < 1000:
        raise HTTPException(500, "Generated PDF is invalid")

    return Response(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=merged.pdf"
        }
____________________________________________________________________________________________
 
@app.post("/images-to-pdf")
async def images_to_pdf(files: list[UploadFile] = File(...)):

    if len(files) == 0:
        raise HTTPException(400, "No images uploaded")

    images_bytes = []

    for file in files:
        content = await file.read()

        if len(content) < 100:
            raise HTTPException(400, f"{file.filename} is empty")

        images_bytes.append(content)

    # IMPORTANT: img2pdf needs raw bytes list
    pdf_bytes = img2pdf.convert(images_bytes)

    if len(pdf_bytes) < 1000:
        raise HTTPException(500, "PDF generation failed")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=images.pdf"
        }
    )
____________________________________________________________________________________________


    )
