from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def generate_embeddings(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        
        embedded_docs = []

        for doc in documents:
            try:
                chunk_embeddings = self.model.encode(doc['chunks'], show_progress_bar=False)

                if isinstance(chunk_embeddings, list):
                    chunk_embeddings = np.array(chunk_embeddings, dtype=np.float32)
                elif not isinstance(chunk_embeddings, np.ndarray):
                    chunk_embeddings = np.array(chunk_embeddings, dtype=np.float32)
                else:
                    chunk_embeddings = chunk_embeddings.astype(np.float32)

                embedded_doc = {
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'chunks': doc['chunks'],
                    'embeddings': chunk_embeddings, 
                    'chunk_count': len(doc['chunks'])
                }

                embedded_docs.append(embedded_doc)
                logger.info(f"Generated embeddings for {doc['metadata']['file_name']}: {len(doc['chunks'])} chunks")

            except Exception as e:
                logger.error(f"Error generating embeddings for {doc['metadata']['file_name']}: {e}")
                continue

        return embedded_docs

    def encode_query(self, query: str) -> np.ndarray:
        
        embedding = self.model.encode([query], show_progress_bar=False)[0]
        # Ensure consistent dtype
        if isinstance(embedding, list):
            embedding = np.array(embedding, dtype=np.float32)
        elif isinstance(embedding, np.ndarray):
            embedding = embedding.astype(np.float32)
        return embedding

    def get_model_info(self) -> Dict[str, Any]:
        
        return {
            'model_name': self.model_name,
            'max_seq_length': self.model.max_seq_length,
            'embedding_dimension': self.model.get_sentence_embedding_dimension()
        }
