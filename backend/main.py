from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from docx import Document
from io import BytesIO

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#To be implemented: Function to extract placeholders from the document
def extract_placeholders(doc):
    return None

# Global storage for uploaded document
current_doc = None
current_placeholders = []

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a legal document"""
    global current_doc, current_placeholders
    
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        doc = Document(BytesIO(contents))
        
        # Store document
        current_doc = doc
        
        # Extract placeholders
        placeholders = extract_placeholders(doc)
        current_placeholders = placeholders
        
        return {
            "filename": file.filename,
            "placeholders": placeholders,
            "count": len(placeholders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Legal Document Assistant API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)