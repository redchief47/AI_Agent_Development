import os
import hashlib
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.processed_docs = {}

    def load_documents(self, directory: str) -> List[Dict[str, Any]]:
        
        documents = []
        dir_path = Path(directory)

        if not dir_path.exists():
            raise ValueError(f"Directory {directory} does not exist")

        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx', '.txt']:
                try:
                    doc_data = self._load_single_document(file_path)
                    if doc_data:
                        documents.append(doc_data)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")

        return documents

    def _load_single_document(self, file_path: Path) -> Dict[str, Any]:
        
        content = self._extract_text(file_path)
        if not content.strip():
            return None

        # Generate unique ID based on content hash
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # Check for duplicates
        if content_hash in self.processed_docs:
            logger.info(f"Duplicate document detected: {file_path}")
            return None

        self.processed_docs[content_hash] = True

        # Extract metadata
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_type': file_path.suffix.lower(),
            'file_size': file_path.stat().st_size,
            'content_hash': content_hash,
            'last_modified': file_path.stat().st_mtime
        }

        return {
            'content': content,
            'metadata': metadata,
            'chunks': self._chunk_text(content)
        }

    def _extract_text(self, file_path: Path) -> str:
        
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            return self._extract_pdf_text(file_path)
        elif suffix == '.docx':
            return self._extract_docx_text(file_path)
        elif suffix == '.txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _extract_pdf_text(self, file_path: Path) -> str:
        
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_docx_text(self, file_path: Path) -> str:
        
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_txt_text(self, file_path: Path) -> str:
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    def _chunk_text(self, text: str) -> List[str]:
        
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks
