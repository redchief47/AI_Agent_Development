import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
import json
import os
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, dimension: int = 384, index_file: str = None):
        
        self.dimension = dimension
        self.index_file = index_file or "vector_index.faiss"
        self.index = None
        self.documents = []
        self.metadata = []

    def build_index(self, embedded_documents: List[Dict[str, Any]]):
        
        all_embeddings = []
        all_metadata = []

        for doc in embedded_documents:
            embeddings = np.array(doc['embeddings'])
            all_embeddings.append(embeddings)

            # Store metadata for each chunk
            for i, chunk in enumerate(doc['chunks']):
                chunk_metadata = {
                    'file_name': doc['metadata']['file_name'],
                    'file_path': doc['metadata']['file_path'],
                    'chunk_index': i,
                    'chunk_text': chunk,
                    'total_chunks': len(doc['chunks'])
                }
                all_metadata.append(chunk_metadata)

        # Concatenate all embeddings
        if all_embeddings:
            embeddings_array = np.vstack(all_embeddings)
            self.dimension = embeddings_array.shape[1]

            # Create FAISS index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
            faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
            self.index.add(embeddings_array)

            self.documents = embedded_documents
            self.metadata = all_metadata

            logger.info(f"Built FAISS index with {len(all_metadata)} chunks from {len(embedded_documents)} documents")
        else:
            logger.warning("No embeddings provided to build index")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")

        # Normalize query embedding
        faiss.normalize_L2(query_embedding.reshape(1, -1))

        # Search
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                result = {
                    'score': float(score),
                    'metadata': self.metadata[idx],
                    'chunk_text': self.metadata[idx]['chunk_text']
                }
                results.append(result)

        return results

    def save_index(self, directory: str = "models"):
        
        os.makedirs(directory, exist_ok=True)

        if self.index is not None:
            index_path = os.path.join(directory, self.index_file)
            faiss.write_index(self.index, index_path)

            metadata_path = os.path.join(directory, "metadata.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': self.metadata,
                    'documents': [{'metadata': doc['metadata'], 'chunk_count': doc['chunk_count']} for doc in self.documents]
                }, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved index to {index_path} and metadata to {metadata_path}")
        else:
            logger.warning("No index to save")

    def load_index(self, directory: str = "models"):
        
        index_path = os.path.join(directory, self.index_file)
        metadata_path = os.path.join(directory, "metadata.json")

        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)

            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.metadata = data['metadata']
                self.documents = data['documents']

            logger.info(f"Loaded index from {index_path} with {len(self.metadata)} chunks")
        else:
            logger.warning(f"Index files not found in {directory}")

    def get_stats(self) -> Dict[str, Any]:
        
        if self.index is None:
            return {"status": "not_initialized"}

        return {
            "total_chunks": len(self.metadata),
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "index_size": self.index.ntotal if self.index else 0
        }
