import requests
import json
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        
        self.ollama_url = ollama_url
        self.model = model
        self.generation_url = f"{ollama_url}/api/generate"

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]], max_tokens: int = 500) -> Dict[str, Any]:
        if not self.check_ollama_status():
            return self._generate_extract_answer(query, context_chunks)

        context_text = self._prepare_context(context_chunks)

        prompt = self._create_prompt(query, context_text)

        response = self._call_ollama(prompt, max_tokens)

        sources = self._extract_sources(context_chunks)

        return {
            'answer': response.get('response', ''),
            'sources': sources,
            'confidence': self._calculate_confidence(context_chunks),
            'model': self.model,
            'query': query
        }

    def _generate_extract_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not context_chunks:
            return {
                'answer': "No relevant information found in the documents.",
                'sources': [],
                'confidence': 0.0,
                'model': 'extractive',
                'query': query
            }

        best_chunk = max(context_chunks, key=lambda x: x['score'])
        relevant_text = self._extract_relevant_sentences(query, best_chunk['chunk_text'])

        return {
            'answer': f"Based on the documents: {relevant_text}",
            'sources': self._extract_sources([best_chunk]),
            'confidence': best_chunk['score'],
            'model': 'extractive',
            'query': query
        }

    def _extract_relevant_sentences(self, query: str, text: str) -> str:
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

        if not sentences:
            return text[:500] + "..." if len(text) > 500 else text

        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        query_words = {word for word in query_words if len(word) > 2}  # Filter short words

        sentence_scores = []
        for sentence in sentences:
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            matches = len(query_words.intersection(sentence_words))
            score = matches / len(query_words) if query_words else 0
            sentence_scores.append((sentence, score))

        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [s for s, score in sentence_scores if score > 0][:3]  # Take up to 3 relevant sentences

        if not top_sentences:
            return sentences[0][:500] + "..." if len(sentences[0]) > 500 else sentences[0]

        result = ' '.join(top_sentences)
        return result[:500] + "..." if len(result) > 500 else result

    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = f"Source {i} ({chunk['metadata']['file_name']}):"
            context_parts.append(f"{source}\n{chunk['chunk_text']}\n")

        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        return f

    def _call_ollama(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.1  
            }
        }

        try:
            response = requests.post(self.generation_url, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama: {e}")
            return {"response": "Error: Unable to generate response. Please check if Ollama is running."}

    def _extract_sources(self, context_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = []
        for chunk in context_chunks:
            source = {
                'file_name': chunk['metadata']['file_name'],
                'file_path': chunk['metadata']['file_path'],
                'chunk_index': chunk['metadata']['chunk_index'],
                'score': chunk['score'],
                'text_preview': chunk['chunk_text'][:200] + "..." if len(chunk['chunk_text']) > 200 else chunk['chunk_text']
            }
            sources.append(source)
        return sources

    def _calculate_confidence(self, context_chunks: List[Dict[str, Any]]) -> float:
        if not context_chunks:
            return 0.0

        avg_score = sum(chunk['score'] for chunk in context_chunks) / len(context_chunks)
        return min(max(avg_score, 0.0), 1.0)

    def check_ollama_status(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if self.model in available_models:
                    return True
                else:
                    logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                    return False
            return False
        except requests.exceptions.RequestException:
            logger.error("Ollama is not running or not accessible")
            return False
