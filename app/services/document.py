import time
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from loguru import logger

from app.core.config import settings
from app.schemas.document import ExtractionResult


class DocumentProcessor:
    def __init__(self) -> None:
        logger.info("Initializing DocumentProcessor with Docling models...")
        pipeline_options = PdfPipelineOptions()
        # Use PDF text layer only; no OCR. Avoids RapidOCR "empty result" warnings for text-based PDFs.
        # Set do_ocr=True only if you need to process scanned/image-only PDFs.
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        self.converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
        )

    async def process_pdf(self, file_path: Path) -> ExtractionResult:
        # "Bind" the filename to all logs in this scope
        log = logger.bind(filename=file_path.name)

        log.info(f"Starting extraction for: {file_path.name}")
        start_time = time.perf_counter()

        try:
            # Optional limits for very large PDFs (0 = no limit)
            kwargs: dict = {}
            if settings.PDF_MAX_PAGES > 0:
                kwargs["max_num_pages"] = settings.PDF_MAX_PAGES
            if settings.PDF_MAX_FILE_SIZE_MB > 0:
                kwargs["max_file_size"] = settings.PDF_MAX_FILE_SIZE_MB * 1024 * 1024

            # The conversion process
            result = self.converter.convert(file_path, **kwargs)

            end_time = time.perf_counter()
            total_duration = end_time - start_time

            # Metadata extraction
            page_count = len(result.document.pages) if hasattr(result.document, "pages") else 1
            avg_time_per_page = total_duration / page_count if page_count > 0 else 0

            # Professional Granular Logging
            log.success(f"Extraction complete for {file_path.name}")
            log.info(f"Total Pages: {page_count}")
            log.info(f"Total Time: {total_duration:.2f}s")
            log.info(f"Avg Time Per Page: {avg_time_per_page:.2f}s")

            return ExtractionResult(
                content=result.document.export_to_markdown(),
                page_count=page_count,
                metadata=result.document.metadata.dict()
                if hasattr(result.document, "metadata")
                else {},
                processing_time_seconds=round(total_duration, 2),
            )

        except Exception as e:
            log.error(f"Failed to process document: {str(e)}")
            raise e
