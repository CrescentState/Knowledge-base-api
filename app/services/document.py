import asyncio
import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from loguru import logger

from app.schemas.document import ExtractionResult


class DocumentProcessor:
    def __init__(self) -> None:
        logger.info("Initializing DocumentProcessor with Docling models...")

        # Configure OCR pipeline to fix RapidOCR empty result warnings.
        # The default scale is too low for many scanned PDFs; raising it to 3.0
        # gives RapidOCR larger images to detect text regions reliably.
        # force_full_page_ocr ensures every page is OCR'd even if Docling
        # thinks it already contains a text layer (common with hybrid PDFs).
        ocr_options = RapidOcrOptions(
            force_full_page_ocr=True,
        )
        pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            ocr_options=ocr_options,
        )
        pipeline_options.images_scale = 3.0  # Increase render resolution for OCR

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    async def process_pdf(self, file_path: Path) -> ExtractionResult:
        # "Bind" the filename to all logs in this scope
        log = logger.bind(filename=file_path.name)

        log.info(f"Starting extraction for: {file_path.name}")
        start_time = time.perf_counter()

        try:
            # Run the blocking Docling conversion in a thread pool so it does
            # not freeze the FastAPI event loop during processing.
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, self.converter.convert, file_path
            )

            end_time = time.perf_counter()
            total_duration = end_time - start_time

            # Metadata extraction
            page_count = (
                len(result.document.pages) if hasattr(result.document, "pages") else 1
            )
            avg_time_per_page = total_duration / page_count if page_count > 0 else 0

            # Professional Granular Logging
            log.success(f"Extraction complete for {file_path.name}")
            log.info(f"Total Pages: {page_count}")
            log.info(f"Total Time: {total_duration:.2f}s")
            log.info(f"Avg Time Per Page: {avg_time_per_page:.2f}s")

            metadata_dict: dict = {}
            if hasattr(result.document, "metadata"):
                meta = result.document.metadata
                metadata_dict = meta.model_dump() if hasattr(meta, "model_dump") else meta.dict()

            return ExtractionResult(
                content=result.document.export_to_markdown(),
                page_count=page_count,
                metadata=metadata_dict,
                processing_time_seconds=round(total_duration, 2),
            )

        except Exception as e:
            log.error(f"Failed to process document: {str(e)}")
            raise e