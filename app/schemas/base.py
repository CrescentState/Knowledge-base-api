from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class CoreModel(BaseModel):
    """Base model for all schemas to ensure consistency."""

    model_config = ConfigDict(
        from_attributes=True,  # Allows compatibility with ORMs
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
    )


class DocumentMetadata(CoreModel):
    """Schema for document processing results."""

    filename: str
    content_type: str = Field(..., pattern="application/pdf|text/html")
    file_size_bytes: int = Field(gt=0)
    processed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
