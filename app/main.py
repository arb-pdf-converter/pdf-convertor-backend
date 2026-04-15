from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import endpoints
from app.utils.cors import add_cors_middleware

app = FastAPI(
    title="PDF Converter API",
    description="Merge, compress, convert images to PDF",
    version="1.0.0"
)

# CORS for frontend
app = add_cors_middleware(app)

# Include API routes
app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "PDF Converter API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
