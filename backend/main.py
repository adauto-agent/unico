from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid
from extractor import UnicoExtractor

app = FastAPI(title="UNICO Order Extractor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
FRONTEND_DIR = "../frontend"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

extractor = UnicoExtractor()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "unico-backend"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
    
    file_id = str(uuid.uuid4())
    temp_pdf = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    output_xlsx = os.path.join(OUTPUT_DIR, f"{file_id}.xlsx")
    
    try:
        with open(temp_pdf, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process PDF
        items_count = extractor.extract(temp_pdf, output_xlsx)
        
        return {
            "filename": f"{file_id}.xlsx",
            "items_count": items_count,
            "message": "Trích xuất thành công!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý: {str(e)}")

@app.get("/download/{filename}")
async def download_excel(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File không tồn tại")
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"unico_extract_{filename}"
    )

# Serve frontend
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

# Mount static files for frontend assets
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9981)
