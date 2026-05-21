"""Core recommendation engine."""

from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from app.recommendations.embeddings import embedding_engine
from app.recommendations.generator import response_generator
from app.recommendations.schemas import SongRecommendation


class RecommendationEngine:
    """Recommendation engine combining TF-IDF search + template explanations."""

    def __init__(self):
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await embedding_engine.initialize()
        await response_generator.initialize()
        self._initialized = True

    def recommend_by_query(self, query: str, num_results: int = 10) -> Tuple[List[SongRecommendation], str]:
        results = embedding_engine.search(query, top_k=num_results)
        recommendations = [self._to_rec(s, query, "natural") for s in results]
        summary = response_generator.generate_summary(results, query, "natural")
        return recommendations, summary

    def recommend_similar(self, song_title: str, artist: Optional[str] = None, num_results: int = 10) -> Tuple[List[SongRecommendation], str]:
        results = embedding_engine.find_similar(song_title, artist, top_k=num_results)
        query = f"similar to {song_title}"
        recommendations = [self._to_rec(s, query, "similar") for s in results]
        summary = response_generator.generate_summary(results, query, "similar")
        return recommendations, summary

    def recommend_by_mood(self, mood: str, num_results: int = 10, language: Optional[str] = None) -> Tuple[List[SongRecommendation], str]:
        query = f"{mood} mood music"
        filters = {"mood": mood}
        if language:
            filters["language"] = language
        results = embedding_engine.search(query, top_k=num_results, filters=filters)
        if len(results) < num_results:
            results = embedding_engine.search(query, top_k=num_results)
        recommendations = [self._to_rec(s, mood, "mood") for s in results]
        summary = response_generator.generate_summary(results, mood, "mood")
        return recommendations, summary

    def _to_rec(self, song: Dict[str, Any], query: str, qtype: str) -> SongRecommendation:
        explanation = response_generator.generate_explanation(song, query, qtype)
        return SongRecommendation(
            song_id=song.get("song_id", "unknown"),
            title=song.get("title", "Unknown"),
            artist=song.get("artist", "Unknown"),
            album=song.get("album", "Unknown"),
            genre=song.get("genre", "Unknown"),
            sub_genre=song.get("sub_genre"),
            year=song.get("year", 2000),
            duration_ms=song.get("duration_ms", 200000),
            mood=song.get("mood", "Unknown"),
            tempo=song.get("tempo"),
            language=song.get("language", "Unknown"),
            popularity=song.get("popularity", 50),
            description=song.get("description"),
            match_score=song.get("match_score", 0.0),
            explanation=explanation,
        )


# Singleton
recommendation_engine = RecommendationEngine()
