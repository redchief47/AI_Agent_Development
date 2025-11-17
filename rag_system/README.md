# RAG System - Retrieval-Augmented Generation for Personal Documents

A local, privacy-focused system that allows you to query your personal documents using natural language, powered by embeddings and large language models.

## Features

- **Document Support**: PDF, DOCX, and TXT files
- **Local Processing**: All embeddings and processing happen locally
- **Intelligent Chunking**: Smart text splitting for better retrieval
- **Duplicate Detection**: Automatic removal of duplicate content
- **Source Attribution**: Always know which document provided the information
- **Confidence Scoring**: Understand how reliable the answer is
- **Follow-up Questions**: Ask clarifying questions for better results

## Prerequisites

- Python 3.8+
- Ollama (for local LLM inference)
- Required Python packages (see requirements.txt)

## Installation

1. **Install Ollama**:
   ```bash
   # Download from https://ollama.ai/
   # Pull a model (e.g., Llama 2)
   ollama pull llama2
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd rag-system
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Usage

### Command Line Interface

```bash
# Add documents to your knowledge base
python main.py add-documents /path/to/your/documents

# Query your documents
python main.py query "What is the capital of France?"

# Interactive mode
python main.py interactive

# View statistics
python main.py stats

# Export knowledge base
python main.py export knowledge_base.json
```

### Python API

```python
from src.query_interface import QueryInterface

# Initialize
interface = QueryInterface()

# Add documents
result = interface.add_documents("/path/to/documents")
print(f"Added {result['documents_added']} documents")

# Query
result = interface.query("Your question here")
print(result['answer'])
print(f"Sources: {len(result['sources'])}")
```

## Architecture

```
Documents (PDF/DOCX/TXT)
    ↓
Document Processor
    ↓
Text Chunks + Metadata
    ↓
Embedding Generator (Sentence Transformers)
    ↓
Vector Embeddings
    ↓
FAISS Vector Store
    ↓
Query → Retrieval → Context
    ↓
RAG Pipeline (Ollama LLM)
    ↓
Answer + Sources + Confidence
```

## Configuration

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Vector Store**: FAISS with cosine similarity
- **LLM**: Ollama with configurable models
- **Chunk Size**: 1000 characters with 200 character overlap

## File Structure

```
rag_system/
├── src/
│   ├── document_processor.py    # Document loading and chunking
│   ├── embedding_generator.py   # Generate embeddings
│   ├── vector_store.py         # FAISS vector operations
│   ├── rag_pipeline.py         # LLM integration
│   └── query_interface.py      # Main API
├── data/                       # Your documents
├── models/                     # Saved models and indices
├── docs/                       # Documentation
├── main.py                     # CLI entry point
├── requirements.txt
└── README.md
```

## Example Queries

```bash
# Add some test documents
python main.py add-documents ./data

# Ask questions
python main.py query "What are the main benefits of renewable energy?"
python main.py query "How does machine learning work?"
python main.py query "What is the history of artificial intelligence?"
```

## Troubleshooting

**Ollama not found**: Make sure Ollama is running and the model is pulled
**No documents found**: Check file paths and supported formats (PDF, DOCX, TXT)
**Low quality answers**: Try rephrasing questions or adding more relevant documents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Made By Shreyash Vinchurkar
