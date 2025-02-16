"""API models for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List


class ScriptSearchResult(BaseModel):
    """Movie script search result."""

    title: str = Field(..., description="Movie title")
    url: str = Field(..., description="Script URL")
    source: str = Field(..., description="Source website (IMSDB/Cinematheque)")


class ScriptResponse(BaseModel):
    """Movie script response."""

    title: str = Field(..., description="Movie title")
    script: str = Field(..., description="Script content")
    source: str = Field(..., description="Source website")
    url: str = Field(..., description="Source URL")


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")

class BechdelScoreResponse(BaseModel):
    """Bechdel test analysis response."""

    passes_test: bool = Field(..., description="Whether the movie passes the Bechdel test")
    female_characters: List[str] = Field(..., description="List of identified female character names")
    failure_reasons: Optional[List[str]] = Field(None, description="Reasons for failing the test, if applicable")
    num_female_conversations: int = Field(
        ..., description="Number of conversations between female characters"
    )
