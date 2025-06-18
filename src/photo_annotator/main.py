from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from photo_annotator.api.routes import router
from photo_annotator.services.csv_service import CSVService
from photo_annotator.services.file_handler import FileHandler
from photo_annotator.services.image_service import ImageService

app = FastAPI(
    title="Photo Annotation Tool",
    description="A web application for manual photo annotation with CSV export",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize services
csv_service = CSVService("annotations.csv")
csv_service.initialize()

file_handler = FileHandler(str(UPLOAD_DIR))
image_service = ImageService(str(UPLOAD_DIR))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/")
async def read_root():
    """Serve the main page"""
    from fastapi.responses import FileResponse
    return FileResponse("templates/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "photo-annotation-tool"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)