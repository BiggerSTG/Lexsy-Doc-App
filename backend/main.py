from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import re
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

# In-memory storage for session data
sessions = {}

class ChatMessage(BaseModel):
    role: str
    message: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage]

class GenerateRequest(BaseModel):
    conversation_history: List[ChatMessage]

def extract_placeholders(doc: Document) -> List[Dict[str, str]]:
    """Extract placeholders from document in format [Placeholder Name]"""
    placeholders = []
    seen = set()
    
    # Pattern to match [Text] or \[Text\]
    pattern = r'\[([^\]]+)\]'
    
    # Check paragraphs
    for para in doc.paragraphs:
        matches = re.findall(pattern, para.text)
        for match in matches:
            if match not in seen:
                seen.add(match)
                placeholders.append({
                    'name': match,
                    'value': None,
                    'question': f"What should I fill in for [{match}]?"
                })
    
    # Check tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                matches = re.findall(pattern, cell.text)
                for match in matches:
                    if match not in seen:
                        seen.add(match)
                        placeholders.append({
                            'name': match,
                            'value': None,
                            'question': f"What should I fill in for [{match}]?"
                        })
    
    return placeholders

def extract_values_from_conversation(conversation: List[ChatMessage], placeholders: List[Dict]) -> Dict[str, str]:
    """Use simple pattern matching to extract values from conversation"""
    values = {}
    
    # Create a mapping of lowercase placeholder names for matching
    placeholder_names = {p['name'].lower(): p['name'] for p in placeholders}
    
    for i, msg in enumerate(conversation):
        if msg.role == 'assistant':
            # Check if the assistant asked about a placeholder
            for placeholder_key, placeholder_name in placeholder_names.items():
                if placeholder_key in msg.message.lower() or f"[{placeholder_name}]" in msg.message:
                    # Get the next user message
                    if i + 1 < len(conversation) and conversation[i + 1].role == 'user':
                        values[placeholder_name] = conversation[i + 1].message
                        break
    
    return values

def fill_document(original_doc: Document, values: Dict[str, str]) -> Document:
    """Fill placeholders in the document with provided values"""
    # Create a new document from the original
    new_doc = Document()
    
    # Copy styles
    for style in original_doc.styles:
        try:
            if style.name not in new_doc.styles:
                new_doc.styles.add_style(style.name, style.type)
        except:
            pass
    
    # Process paragraphs
    for para in original_doc.paragraphs:
        text = para.text
        for placeholder, value in values.items():
            text = text.replace(f"[{placeholder}]", value)
        new_para = new_doc.add_paragraph(text)
        new_para.style = para.style
    
    # Process tables
    for table in original_doc.tables:
        new_table = new_doc.add_table(rows=len(table.rows), cols=len(table.columns))
        for i, row in enumerate(table.rows):
            for j, cell in enumerate(row.cells):
                text = cell.text
                for placeholder, value in values.items():
                    text = text.replace(f"[{placeholder}]", value)
                new_table.rows[i].cells[j].text = text
    
    return new_doc

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