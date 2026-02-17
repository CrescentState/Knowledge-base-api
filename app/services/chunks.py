from collections.abc import Sequence
from typing import Any

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from loguru import logger


class ChunkingService:
    def __init__(self) -> None:
        # We split based on headers to keep "Context" together
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

    def create_chunks(self, markdown_text: str) -> Sequence[Any]:
        """Breaks markdown into semantic pieces."""
        try:
            # First split by header
            header_splits = self.header_splitter.split_text(markdown_text)
            # Then split by character limit if sections are still too big
            final_chunks = self.text_splitter.split_documents(header_splits)
            logger.info(f"Generated {len(final_chunks)} chunks.")
            return final_chunks
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            raise e
