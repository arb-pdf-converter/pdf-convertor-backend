from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter
from typing import Literal
from PIL import Image
from io import BytesIO

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://pdf-convertor-backend-i30o.onrender.com",
        "https://arb-service.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "PDF API Working"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------- MERGE PDFs ----------------
@app.post("/merge")
async def merge(files: list[UploadFile] = File(...)):

    if len(files) < 2:
        raise HTTPException(400, "Need at least 2 PDFs")

    writer = PdfWriter()

    for file in files:
        content = await file.read()
        reader = PdfReader(BytesIO(content))

        for page in reader.pages:
            writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)

    return Response(
        content=output.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=merged.pdf"}
    )


# ---------------- IMAGES TO PDF ----------------
@app.post("/images-to-pdf")
async def images_to_pdf(files: list[UploadFile] = File(...)):

    if len(files) == 0:
        raise HTTPException(400, "No images uploaded")

    images = []

    for file in files:
        content = await file.read()
        img = Image.open(BytesIO(content)).convert("RGB")
        images.append(img)

    output = BytesIO()
    images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
    output.seek(0)

    return Response(
        content=output.read(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=images.pdf"}
    )

# ---------------- COMPRESS PDF ----------------
@app.post("/compress-pdf")
async def compress_pdf(
    file: UploadFile = File(...),
    level: Literal["30", "50", "80"] = "50"
):
    print("🔥 COMPRESS HIT")
    content = await file.read()

    if len(content) < 1000:
        raise HTTPException(400, "Invalid PDF file")

    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)

    output.seek(0)
    pdf_bytes = output.getvalue()

    if len(pdf_bytes) < 1000:
        raise HTTPException(500, "Compression failed (empty output)")
    
    print(len(content))
    print(len(pdf_bytes))
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=compressed.pdf"
        }
    )
