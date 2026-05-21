"""Lightweight response generator - template-based (no PyTorch/transformers needed)."""

from typing import List, Dict, Any
from loguru import logger


class ResponseGenerator:
    """Generates explanations using templates (no heavy ML models)."""

    def __init__(self):
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("Response generator ready (template mode)")

    def generate_explanation(self, song: Dict[str, Any], query: str, query_type: str) -> str:
        """Generate explanation for why a song was recommended."""
        mood = song.get("mood", "great")
        genre = song.get("genre", "music")
        artist = song.get("artist", "this artist")
        year = song.get("year", "")
        language = song.get("language", "")

        explanations = {
            "natural": f"This {mood.lower()} {genre.lower()} track by {artist} matches your vibe. A {language} gem from {year}.",
            "similar": f"Shares similar {genre.lower()} elements and {mood.lower()} energy with your pick.",
            "mood": f"With its {mood.lower()} atmosphere, this {genre.lower()} track from {year} sets the perfect tone.",
            "preference": f"Based on your love for {genre.lower()} and {mood.lower()} music, {artist} is a natural fit.",
            "personalized": f"Your taste shows you enjoy {mood.lower()} {genre.lower()} — {artist} delivers exactly that.",
        }

        return explanations.get(query_type, explanations["natural"])

    def generate_summary(self, songs: List[Dict[str, Any]], query: str, query_type: str) -> str:
        """Generate summary for recommendation set."""
        if not songs:
            return "No recommendations found."

        genres = list(set(s.get("genre", "") for s in songs[:5]))
        moods = list(set(s.get("mood", "") for s in songs[:5]))
        artists = list(set(s.get("artist", "") for s in songs[:3]))

        genre_text = ", ".join(genres[:3]) if genres else "various genres"
        mood_text = ", ".join(moods[:2]) if moods else "various moods"
        artist_text = ", ".join(artists[:2]) if artists else "various artists"

        return (
            f"Found {len(songs)} tracks spanning {genre_text} with {mood_text} vibes. "
            f"Featuring {artist_text} and more."
        )


# Singleton
response_generator = ResponseGenerator()
