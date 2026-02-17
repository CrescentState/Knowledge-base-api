import os
from collections.abc import Sequence
from typing import Any

import chromadb
from chromadb.utils import embedding_functions
from loguru import logger


class VectorService:
    def __init__(self) -> None:
        # Ensure the data directory exists
        self.persist_path = "./data/chroma"
        os.makedirs(self.persist_path, exist_ok=True)

        # Initialize the persistent client (saves to disk)
        self.client = chromadb.PersistentClient(path=self.persist_path)

        # Use the lightweight, local-running embedding model
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        self.collection = self.client.get_or_create_collection(
            name="knowledge_base", embedding_function=self.embedding_fn
        )

    async def upsert_chunks(self, chunks: Sequence[Any], document_name: str) -> None:
        """Saves chunks into the vector database."""
        ids = [f"{document_name}_{i}" for i in range(len(chunks))]
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [{"source": document_name, **chunk.metadata} for chunk in chunks]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        logger.success(f"Successfully stored {len(chunks)} chunks in ChromaDB.")
