from typing import List, Dict, Optional

current_doc_bytes: Optional[bytes] = None
current_placeholders: List[Dict] = []

def set_document(bytes_data: bytes):
    global current_doc_bytes
    current_doc_bytes = bytes_data

def get_document() -> Optional[bytes]:
    return current_doc_bytes

def set_placeholders(placeholders: List[Dict]):
    global current_placeholders
    current_placeholders = placeholders

def get_placeholders() -> List[Dict]:
    return current_placeholders
