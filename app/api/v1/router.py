import re
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile
from loguru import logger

from app.services.chunks import ChunkingService
from app.services.vector import VectorService

router = APIRouter(prefix="/documents", tags=["documents"])
chunker = ChunkingService()
vector_db = VectorService()

# Directory for upload temp files (unique per upload so both 10-K and manual work)
UPLOAD_TEMP_DIR = Path("temp_uploads")
# Safe name for Chroma (no path separators, reasonable length)
SAFE_NAME_MAX_LEN = 200


def _safe_document_name(filename: str) -> str:
    """Base filename safe for storage and Chroma ids (e.g. 10-K-Q4-2023-As-Filed.pdf)."""
    base = Path(filename).name if filename else "document.pdf"
    safe = re.sub(r"[^\w\s\-\.]", "_", base)
    return safe[:SAFE_NAME_MAX_LEN] if len(safe) > SAFE_NAME_MAX_LEN else safe or "document.pdf"


def _temp_path_for_upload(filename: str) -> Path:
    """Unique temp path per upload so concurrent or same-name uploads don't clash."""
    UPLOAD_TEMP_DIR.mkdir(exist_ok=True)
    base = Path(filename).name if filename else "document.pdf"
    safe_base = re.sub(r"[^\w\s\-\.]", "_", base)[:SAFE_NAME_MAX_LEN] or "document.pdf"
    return UPLOAD_TEMP_DIR / f"{uuid.uuid4().hex}_{safe_base}"


# This is the "Worker" function that runs after the response is sent
async def process_document_task(
    processor: object, file_path: Path, original_name: str
) -> None:
    doc_name = _safe_document_name(original_name)
    try:
        logger.info(f"Background processing started for {original_name}")
        result = await processor.process_pdf(file_path)

        content = (result.content or "").strip()
        if not content:
            logger.warning(
                f"No text extracted from {original_name}; skipping chunking and vector store."
            )
            return

        chunks = chunker.create_chunks(content)
        if not chunks:
            logger.warning(f"No chunks produced for {original_name}; skipping vector store.")
            return

        await vector_db.upsert_chunks(chunks, doc_name)
        logger.success(
            f"Background processing complete: {len(content)} characters, {len(chunks)} chunks."
        )

    except Exception as e:
        logger.error(f"Background processing failed for {original_name}: {e}")
    finally:
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as e:
                logger.debug(f"Could not remove temp file {file_path}: {e}")
            else:
                logger.debug(f"Temporary file {file_path} removed.")


@router.post("/upload", status_code=202)  # 202 = Accepted
async def upload_document(
    request: Request, background_tasks: BackgroundTasks, file: UploadFile = None
) -> dict:
    if file is None:
        file = File(...)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # Unique temp path so either 10-K or Owners_Manual (or both) work without overwriting
    temp_path = _temp_path_for_upload(file.filename)

    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(
        process_document_task, request.app.state.processor, temp_path, file.filename
    )

    return {
        "message": "File uploaded successfully. Processing has started in the background.",
        "filename": file.filename,
    }
