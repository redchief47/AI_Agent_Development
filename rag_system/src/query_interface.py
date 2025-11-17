import logging
from typing import Dict, Any, List
from .document_processor import DocumentProcessor
from .embedding_generator import EmbeddingGenerator
from .vector_store import VectorStore
from .rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)

class QueryInterface:
    def __init__(self, data_dir: str = "data", models_dir: str = "models"):
        
        self.data_dir = data_dir
        self.models_dir = models_dir

        self.doc_processor = DocumentProcessor()
        self.embedding_gen = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.rag_pipeline = RAGPipeline()

        self.vector_store.load_index(models_dir)

    def add_documents(self, directory: str) -> Dict[str, Any]:
        
        try:
            # Load and process documents
            documents = self.doc_processor.load_documents(directory)

            if not documents:
                return {"status": "error", "message": "No valid documents found"}

            embedded_docs = self.embedding_gen.generate_embeddings(documents)

            self.vector_store.build_index(embedded_docs)

            self.vector_store.save_index(self.models_dir)

            return {
                "status": "success",
                "documents_added": len(documents),
                "chunks_created": sum(len(doc['chunks']) for doc in documents)
            }

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return {"status": "error", "message": str(e)}

    def query(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        
        try:
            query_embedding = self.embedding_gen.encode_query(question)

            context_chunks = self.vector_store.search(query_embedding, top_k)

            if not context_chunks:
                return {
                    "status": "no_results",
                    "message": "No relevant information found in the knowledge base.",
                    "query": question
                }

            result = self.rag_pipeline.generate_answer(question, context_chunks)

            return {
                "status": "success",
                "query": question,
                **result
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {"status": "error", "message": str(e), "query": question}

    def get_stats(self) -> Dict[str, Any]:
        
        return {
            "vector_store": self.vector_store.get_stats(),
            "embedding_model": self.embedding_gen.get_model_info(),
            "ollama_status": "available" if self.rag_pipeline.check_ollama_status() else "unavailable"
        }

    def export_knowledge_base(self, output_file: str = "knowledge_base.json") -> Dict[str, Any]:
        
        try:
            stats = self.get_stats()
            with open(output_file, 'w', encoding='utf-8') as f:
                import json
                json.dump({
                    "stats": stats,
                    "export_date": "2024-01-01",  # Would use actual date
                    "note": "Full knowledge base export not implemented in this version"
                }, f, ensure_ascii=False, indent=2)

            return {"status": "success", "file": output_file}

        except Exception as e:
            logger.error(f"Error exporting knowledge base: {e}")
            return {"status": "error", "message": str(e)}

    def summarize_document(self, file_path: str) -> Dict[str, Any]:
        
        try:
            return {
                "status": "not_implemented",
                "message": "Document summarization not yet implemented",
                "file_path": file_path
            }
        except Exception as e:
            logger.error(f"Error summarizing document: {e}")
            return {"status": "error", "message": str(e)}
