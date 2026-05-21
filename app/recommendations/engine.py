"""Core recommendation engine combining embeddings and LLM generation."""

import json
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from app.database.models import User, UserPreference, UserInteraction
from app.recommendations.embeddings import embedding_engine
from app.recommendations.generator import response_generator
from app.recommendations.schemas import SongRecommendation


class RecommendationEngine:
    """Hybrid recommendation engine using semantic search + LLM explanations."""

    def __init__(self):
        """Initialize the recommendation engine."""
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize both the embedding engine and response generator."""
        if self._initialized:
            return

        await embedding_engine.initialize()
        # Skip GPT-Neo loading for faster startup - use template explanations
        # await response_generator.initialize()
        self._initialized = True
        logger.info("Recommendation engine fully initialized (using fast mode)")

    async def recommend_by_query(
        self, query: str, num_results: int = 10, user: Optional[User] = None, db: Optional[AsyncSession] = None
    ) -> tuple[List[SongRecommendation], str]:
        """Generate recommendations from a natural language query.

        Args:
            query: Natural language query from user.
            num_results: Number of recommendations to return.
            user: Optional user for personalization.
            db: Optional database session for user data.

        Returns:
            Tuple of (list of recommendations, AI summary).
        """
        # Get user preferences for boosting
        filters = await self._get_user_filters(user, db) if user and db else None

        # Semantic search
        results = embedding_engine.search(query, top_k=num_results * 2, filters=filters)

        # Apply personalization boost
        if user and db:
            results = await self._apply_personalization(results, user, db)

        # Trim to requested count
        results = results[:num_results]

        # Generate explanations
        recommendations = []
        for song in results:
            explanation = response_generator.generate_explanation(song, query, "natural")
            recommendations.append(self._to_recommendation(song, explanation))

        # Generate summary
        summary = response_generator.generate_summary(results, query, "natural")

        return recommendations, summary

    async def recommend_similar(
        self, song_title: str, artist: Optional[str] = None, num_results: int = 10
    ) -> tuple[List[SongRecommendation], str]:
        """Find songs similar to a given song.

        Args:
            song_title: Reference song title.
            artist: Optional artist name.
            num_results: Number of results.

        Returns:
            Tuple of (list of recommendations, AI summary).
        """
        results = embedding_engine.find_similar(song_title, artist, top_k=num_results)

        query = f"songs similar to {song_title}" + (f" by {artist}" if artist else "")

        recommendations = []
        for song in results:
            explanation = response_generator.generate_explanation(song, query, "similar")
            recommendations.append(self._to_recommendation(song, explanation))

        summary = response_generator.generate_summary(results, query, "similar")

        return recommendations, summary

    async def recommend_by_mood(
        self, mood: str, num_results: int = 10, language: Optional[str] = None
    ) -> tuple[List[SongRecommendation], str]:
        """Generate mood-based playlist.

        Args:
            mood: Desired mood/vibe.
            num_results: Number of songs.
            language: Optional language filter.

        Returns:
            Tuple of (list of recommendations, AI summary).
        """
        query = f"{mood} mood music"
        filters = {"mood": mood}
        if language:
            filters["language"] = language

        results = embedding_engine.search(query, top_k=num_results, filters=filters)

        # If not enough results with strict filter, relax it
        if len(results) < num_results:
            results = embedding_engine.search(query, top_k=num_results)

        recommendations = []
        for song in results:
            explanation = response_generator.generate_explanation(song, mood, "mood")
            recommendations.append(self._to_recommendation(song, explanation))

        summary = response_generator.generate_summary(results, mood, "mood")

        return recommendations, summary

    async def recommend_by_preferences(
        self,
        genres: Optional[List[str]] = None,
        artists: Optional[List[str]] = None,
        moods: Optional[List[str]] = None,
        languages: Optional[List[str]] = None,
        decade: Optional[str] = None,
        num_results: int = 10,
    ) -> tuple[List[SongRecommendation], str]:
        """Generate recommendations based on explicit preferences.

        Args:
            genres: Preferred genres.
            artists: Preferred artists.
            moods: Preferred moods.
            languages: Preferred languages.
            decade: Preferred decade.
            num_results: Number of results.

        Returns:
            Tuple of (list of recommendations, AI summary).
        """
        # Build query from preferences
        query_parts = []
        if genres:
            query_parts.append(f"genres: {', '.join(genres)}")
        if artists:
            query_parts.append(f"artists like: {', '.join(artists)}")
        if moods:
            query_parts.append(f"mood: {', '.join(moods)}")
        if languages:
            query_parts.append(f"language: {', '.join(languages)}")
        if decade:
            query_parts.append(f"from the {decade}")

        query = "Music with " + ", ".join(query_parts) if query_parts else "popular music"

        # Build filters
        filters = {}
        if languages:
            filters["language"] = languages
        if genres:
            filters["genre"] = genres

        results = embedding_engine.search(query, top_k=num_results * 2, filters=filters)

        # If filters are too restrictive, relax
        if len(results) < num_results:
            results = embedding_engine.search(query, top_k=num_results)

        results = results[:num_results]

        recommendations = []
        for song in results:
            explanation = response_generator.generate_explanation(song, query, "preference")
            recommendations.append(self._to_recommendation(song, explanation))

        summary = response_generator.generate_summary(results, query, "preference")

        return recommendations, summary

    async def recommend_personalized(
        self, user: User, db: AsyncSession, num_results: int = 10
    ) -> tuple[List[SongRecommendation], str]:
        """Generate personalized recommendations based on user history.

        Args:
            user: Current user.
            db: Database session.
            num_results: Number of results.

        Returns:
            Tuple of (list of recommendations, AI summary).
        """
        # Get user preferences
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
        prefs = prefs_result.scalar_one_or_none()

        # Get liked songs
        likes_result = await db.execute(
            select(UserInteraction)
            .where(
                UserInteraction.user_id == user.id,
                UserInteraction.interaction_type == "like",
            )
            .order_by(UserInteraction.created_at.desc())
            .limit(20)
        )
        liked_songs = likes_result.scalars().all()

        # Get disliked song IDs to exclude
        dislikes_result = await db.execute(
            select(UserInteraction.song_id)
            .where(
                UserInteraction.user_id == user.id,
                UserInteraction.interaction_type == "dislike",
            )
        )
        disliked_ids = set(row[0] for row in dislikes_result.all())

        # Build personalized query
        query_parts = []
        if prefs:
            genres = json.loads(prefs.favorite_genres) if prefs.favorite_genres else []
            moods = json.loads(prefs.favorite_moods) if prefs.favorite_moods else []
            artists = json.loads(prefs.favorite_artists) if prefs.favorite_artists else []

            if genres:
                query_parts.append(f"genres: {', '.join(genres[:3])}")
            if moods:
                query_parts.append(f"mood: {', '.join(moods[:3])}")
            if artists:
                query_parts.append(f"artists like: {', '.join(artists[:3])}")

        # Add context from liked songs
        if liked_songs:
            liked_titles = [f"{s.song_title} by {s.song_artist}" for s in liked_songs[:5]]
            query_parts.append(f"similar to: {', '.join(liked_titles)}")

        query = "Music recommendations: " + "; ".join(query_parts) if query_parts else "popular trending music"

        # Search
        results = embedding_engine.search(query, top_k=num_results * 3)

        # Filter out disliked songs
        results = [r for r in results if r.get("song_id", "") not in disliked_ids]
        results = results[:num_results]

        recommendations = []
        for song in results:
            explanation = response_generator.generate_explanation(song, query, "personalized")
            recommendations.append(self._to_recommendation(song, explanation))

        summary = response_generator.generate_summary(results, query, "personalized")

        return recommendations, summary

    async def _get_user_filters(self, user: User, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Get filters based on user preferences."""
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
        prefs = prefs_result.scalar_one_or_none()

        if not prefs:
            return None

        filters = {}
        languages = json.loads(prefs.preferred_languages) if prefs.preferred_languages else []
        if languages:
            filters["language"] = languages

        return filters if filters else None

    async def _apply_personalization(
        self, results: List[Dict[str, Any]], user: User, db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Boost scores based on user history."""
        # Get liked genres/moods
        likes_result = await db.execute(
            select(UserInteraction)
            .where(
                UserInteraction.user_id == user.id,
                UserInteraction.interaction_type == "like",
            )
            .limit(50)
        )
        liked_songs = likes_result.scalars().all()
        liked_ids = set(s.song_id for s in liked_songs)

        # Get disliked IDs
        dislikes_result = await db.execute(
            select(UserInteraction.song_id)
            .where(
                UserInteraction.user_id == user.id,
                UserInteraction.interaction_type == "dislike",
            )
        )
        disliked_ids = set(row[0] for row in dislikes_result.all())

        # Filter and boost
        personalized = []
        for song in results:
            song_id = song.get("song_id", "")
            if song_id in disliked_ids:
                continue  # Skip disliked
            if song_id in liked_ids:
                continue  # Skip already liked (they know it)
            personalized.append(song)

        return personalized

    def _to_recommendation(self, song: Dict[str, Any], explanation: str) -> SongRecommendation:
        """Convert a song dict to a SongRecommendation schema."""
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


# Singleton instance
recommendation_engine = RecommendationEngine()
