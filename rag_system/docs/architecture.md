# RAG System Architecture

## Overview

The RAG (Retrieval-Augmented Generation) system is designed to provide accurate, source-attributed answers to questions about personal documents using local processing for privacy and control.

## Core Components

### 1. Document Processor (`document_processor.py`)

**Purpose**: Load and preprocess documents from various formats.

**Features**:
- Multi-format support (PDF, DOCX, TXT)
- Intelligent text chunking with overlap
- Metadata extraction (file info, size, modification time)
- Duplicate detection using content hashing

**Process Flow**:
```
File → Text Extraction → Chunking → Metadata → Document Object
```

### 2. Embedding Generator (`embedding_generator.py`)

**Purpose**: Convert text chunks into vector embeddings.

**Features**:
- Local sentence transformer models
- Configurable model selection
- Batch processing for efficiency
- Model information and statistics

**Technical Details**:
- Default model: `all-MiniLM-L6-v2` (384 dimensions)
- Cosine similarity for semantic matching
- Optimized for sentence-level embeddings

### 3. Vector Store (`vector_store.py`)

**Purpose**: Efficient storage and retrieval of vector embeddings.

**Features**:
- FAISS-based vector indexing
- Cosine similarity search
- Persistent storage (save/load indices)
- Metadata association with vectors

**Technical Details**:
- IndexFlatIP for inner product (cosine similarity)
- L2 normalization of vectors
- JSON metadata storage

### 4. RAG Pipeline (`rag_pipeline.py`)

**Purpose**: Generate answers using retrieved context and LLM.

**Features**:
- Ollama integration for local LLM inference
- Context preparation from retrieved chunks
- Prompt engineering for factual answers
- Source attribution and confidence scoring

**Process Flow**:
```
Query → Context Retrieval → Prompt Creation → LLM Generation → Answer + Sources
```

### 5. Query Interface (`query_interface.py`)

**Purpose**: High-level API for system interaction.

**Features**:
- Document ingestion
- Query processing
- Statistics and monitoring
- Knowledge base export
- Error handling and logging

## Data Flow

```
1. Document Ingestion:
   Documents → Document Processor → Chunks + Metadata

2. Index Building:
   Chunks → Embedding Generator → Vectors → Vector Store

3. Query Processing:
   Question → Embedding → Retrieval → Context → LLM → Answer
```

## File Formats Supported

- **PDF**: Text extraction using PyPDF2
- **DOCX**: Text extraction using python-docx
- **TXT**: Direct text reading with encoding detection

## Chunking Strategy

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Strategy**: Word-based splitting to preserve context

## Embedding Configuration

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Similarity**: Cosine similarity
- **Normalization**: L2 normalization

## Vector Search

- **Library**: FAISS
- **Index Type**: IndexFlatIP (exact search)
- **Similarity**: Cosine similarity
- **Top-K**: Configurable (default: 5)

## LLM Integration

- **Provider**: Ollama
- **Default Model**: llama2
- **Temperature**: 0.1 (factual responses)
- **Max Tokens**: 500
- **Streaming**: Disabled for CLI

## Storage Structure

```
models/
├── vector_index.faiss    # FAISS index file
└── metadata.json         # Chunk metadata and document info

data/
└── [user documents]      # PDF, DOCX, TXT files
```

## Error Handling

- **Document Loading**: Skip corrupted files, log errors
- **Embedding Generation**: Continue with other documents on failure
- **Vector Search**: Return empty results if index unavailable
- **LLM Generation**: Fallback responses for API failures

## Performance Considerations

- **Memory Usage**: Embeddings stored in memory during search
- **Index Size**: Scales with number of chunks
- **Query Speed**: Sub-second for typical document collections
- **Batch Processing**: Efficient for multiple documents

## Extensibility

- **New Document Formats**: Add extractors to DocumentProcessor
- **Different Embeddings**: Modify EmbeddingGenerator
- **Alternative Vector Stores**: Replace VectorStore implementation
- **Other LLMs**: Update RAGPipeline for different providers

## Security & Privacy

- **Local Processing**: All data stays on user's machine
- **No External APIs**: Except Ollama (local)
- **No Data Transmission**: Embeddings and documents never leave device
- **File Access**: Only reads specified directories
