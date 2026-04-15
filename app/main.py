from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO

app = FastAPI()

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
