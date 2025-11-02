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

#To be implemented: Function to extract values from conversation history
def extract_values_from_conversation(conversation_history, placeholders):
    return None

def fill_document(doc, values):
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
    
@app.post("/chat")
async def chat(request): #Type annotation needs to be added-missing key logic
    """Handle conversation to fill placeholders"""
    global current_placeholders
    
    try:
        # Extract values from conversation so far
        values = extract_values_from_conversation(request.conversation_history, current_placeholders)
        
        # Find next unfilled placeholder
        next_placeholder = None
        for p in current_placeholders:
            if p['name'] not in values:
                next_placeholder = p
                break
        
        # Generate response
        if next_placeholder:
            response = f"Thank you! Now, {next_placeholder['question']}"
            all_filled = False
        else:
            response = "Great! I have all the information I need. Your document is ready to download."
            all_filled = True
        
        return {
            "response": response,
            "all_filled": all_filled,
            "filled_count": len(values),
            "total_count": len(current_placeholders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")
    
@app.post("/generate")
async def generate_document(request): #Type annotation needs to be added-missing key logic
    """Generate the completed document"""
    global current_doc, current_placeholders
    
    if current_doc is None:
        raise HTTPException(status_code=400, detail="No document uploaded")
    
    try:
        # Extract all values from conversation
        values = extract_values_from_conversation(request.conversation_history, current_placeholders)
        
        # Fill the document
        filled_doc = fill_document(current_doc, values)
        
        # Save to BytesIO
        doc_io = BytesIO()
        filled_doc.save(doc_io)
        doc_io.seek(0)
        
        return StreamingResponse(
            doc_io,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=completed_document.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Legal Document Assistant API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)