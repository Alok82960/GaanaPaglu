"""Pydantic schemas for recommendations."""

from pydantic import BaseModel, Field
from typing import Optional, List


class NaturalQueryRequest(BaseModel):
    """Schema for natural language recommendation query."""

    query: str = Field(..., min_length=3, max_length=500, description="Natural language query")
    num_results: int = Field(10, ge=1, le=50, description="Number of recommendations")


class SimilarSongRequest(BaseModel):
    """Schema for finding similar songs."""

    song_title: str = Field(..., description="Song title to find similar songs for")
    artist: Optional[str] = Field(None, description="Artist name for better matching")
    num_results: int = Field(10, ge=1, le=50, description="Number of recommendations")


class MoodRequest(BaseModel):
    """Schema for mood-based playlist generation."""

    mood: str = Field(..., description="Mood/vibe (e.g., 'energetic', 'chill', 'melancholic')")
    num_results: int = Field(10, ge=1, le=50, description="Number of songs in playlist")
    language: Optional[str] = Field(None, description="Preferred language filter")


class PreferenceBasedRequest(BaseModel):
    """Schema for preference-based recommendations."""

    genres: Optional[List[str]] = Field(None, description="Preferred genres")
    artists: Optional[List[str]] = Field(None, description="Preferred artists")
    moods: Optional[List[str]] = Field(None, description="Preferred moods")
    languages: Optional[List[str]] = Field(None, description="Preferred languages")
    decade: Optional[str] = Field(None, description="Preferred decade (e.g., '2010s')")
    num_results: int = Field(10, ge=1, le=50, description="Number of recommendations")


class SongRecommendation(BaseModel):
    """Schema for a single song recommendation."""

    song_id: str = Field(..., description="Spotify track ID")
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Artist name")
    album: str = Field(..., description="Album name")
    genre: str = Field(..., description="Genre")
    sub_genre: Optional[str] = Field(None, description="Sub-genre")
    year: int = Field(..., description="Release year")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    mood: str = Field(..., description="Song mood/vibe")
    tempo: Optional[float] = Field(None, description="BPM")
    language: str = Field(..., description="Song language")
    popularity: int = Field(..., description="Popularity score 0-100")
    description: Optional[str] = Field(None, description="Song description")
    match_score: float = Field(..., ge=0, le=100, description="Match percentage")
    explanation: str = Field(..., description="Why this song was recommended")


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""

    query: str = Field(..., description="Original query")
    query_type: str = Field(..., description="Type of recommendation")
    total_results: int = Field(..., description="Number of results returned")
    recommendations: List[SongRecommendation] = Field(..., description="List of recommended songs")
    ai_summary: str = Field(..., description="AI-generated summary of recommendations")
