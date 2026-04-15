from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter
from io import BytesIO

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

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(400, "Only PDF files allowed")

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
        headers={
            "Content-Disposition": "attachment; filename=merged.pdf"
        }
    )
