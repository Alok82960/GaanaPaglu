"""Pydantic schemas for user preferences and interactions."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences."""

    favorite_genres: Optional[List[str]] = Field(None, description="List of favorite genres")
    favorite_artists: Optional[List[str]] = Field(None, description="List of favorite artists")
    favorite_moods: Optional[List[str]] = Field(None, description="List of favorite moods")
    preferred_languages: Optional[List[str]] = Field(None, description="Preferred song languages")
    preferred_decades: Optional[List[str]] = Field(None, description="Preferred decades (e.g., '2000s', '2010s')")
    min_tempo: Optional[int] = Field(None, ge=40, le=220, description="Minimum BPM preference")
    max_tempo: Optional[int] = Field(None, ge=40, le=220, description="Maximum BPM preference")


class PreferenceResponse(BaseModel):
    """Schema for user preference response."""

    favorite_genres: List[str]
    favorite_artists: List[str]
    favorite_moods: List[str]
    preferred_languages: List[str]
    preferred_decades: List[str]
    min_tempo: Optional[int]
    max_tempo: Optional[int]
    updated_at: datetime

    class Config:
        from_attributes = True


class SongInteraction(BaseModel):
    """Schema for liking/disliking a song."""

    song_id: str = Field(..., description="Spotify track ID")
    song_title: str = Field(..., description="Song title")
    song_artist: str = Field(..., description="Song artist")


class InteractionResponse(BaseModel):
    """Schema for interaction response."""

    id: int
    song_id: str
    song_title: str
    song_artist: str
    interaction_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class QueryHistoryResponse(BaseModel):
    """Schema for query history response."""

    id: int
    query_text: str
    query_type: str
    results_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserHistoryResponse(BaseModel):
    """Combined user history response."""

    likes: List[InteractionResponse]
    dislikes: List[InteractionResponse]
    recent_queries: List[QueryHistoryResponse]
    total_likes: int
    total_dislikes: int
    total_queries: int
