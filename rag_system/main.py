#!/usr/bin/env python3


import argparse
import sys
import logging
from pathlib import Path
from src.query_interface import QueryInterface

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="RAG System - Query your personal documents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add documents command
    add_parser = subparsers.add_parser('add-documents', help='Add documents to knowledge base')
    add_parser.add_argument('directory', help='Directory containing documents')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query the knowledge base')
    query_parser.add_argument('question', help='Question to ask')
    query_parser.add_argument('--top-k', type=int, default=5, help='Number of top results to retrieve')

    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive query mode')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show knowledge base statistics')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export knowledge base')
    export_parser.add_argument('output_file', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize query interface
    try:
        interface = QueryInterface()
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        sys.exit(1)

    # Handle commands
    if args.command == 'add-documents':
        result = interface.add_documents(args.directory)
        if result['status'] == 'success':
            print(f"✅ Successfully added {result['documents_added']} documents with {result['chunks_created']} chunks")
        else:
            print(f"❌ Error: {result['message']}")
            sys.exit(1)

    elif args.command == 'query':
        result = interface.query(args.question, args.top_k)
        display_query_result(result)

    elif args.command == 'interactive':
        run_interactive_mode(interface)

    elif args.command == 'stats':
        stats = interface.get_stats()
        display_stats(stats)

    elif args.command == 'export':
        result = interface.export_knowledge_base(args.output_file)
        if result['status'] == 'success':
            print(f"✅ Knowledge base exported to {result['file']}")
        else:
            print(f"❌ Error: {result['message']}")
            sys.exit(1)

def display_query_result(result: dict):

    if result['status'] == 'error':
        print(f"❌ Error: {result['message']}")
        return

    if result['status'] == 'no_results':
        print(f"🤔 No relevant information found for: {result['query']}")
        return

    print(f"🤖 Answer: {result['answer']}")
    print(f"📊 Confidence: {result['confidence']:.2f}")
    print(f"📚 Sources ({len(result['sources'])}):")

    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['file_name']} (score: {source['score']:.3f})")
        print(f"     {source['text_preview']}")
        print()

def run_interactive_mode(interface: QueryInterface):

    print("🤖 RAG System Interactive Mode")
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'stats' to show knowledge base statistics")
    print("-" * 50)

    while True:
        try:
            question = input("❓ Ask a question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            if question.lower() == 'stats':
                stats = interface.get_stats()
                display_stats(stats)
                continue

            if not question:
                continue

            result = interface.query(question)
            display_query_result(result)
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def display_stats(stats: dict):

    print("📊 Knowledge Base Statistics")
    print("-" * 30)

    vs = stats.get('vector_store', {})
    if vs.get('status') == 'not_initialized':
        print("❌ Vector store not initialized")
    else:
        print(f"📄 Total documents: {vs.get('total_documents', 0)}")
        print(f"📝 Total chunks: {vs.get('total_chunks', 0)}")
        print(f"🔍 Vector dimension: {vs.get('dimension', 0)}")

    em = stats.get('embedding_model', {})
    print(f"🧠 Embedding model: {em.get('model_name', 'Unknown')}")

    ollama = stats.get('ollama_status', 'unknown')
    status_icon = "✅" if ollama == "available" else "❌"
    print(f"{status_icon} Ollama status: {ollama}")

if __name__ == "__main__":
    main()
