"""Sentence Transformer embeddings for semantic song search."""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

from sentence_transformers import SentenceTransformer
from loguru import logger

from app.config import get_settings

settings = get_settings()


class EmbeddingEngine:
    """Manages song embeddings for semantic similarity search."""

    def __init__(self):
        """Initialize the embedding engine."""
        self.model: Optional[SentenceTransformer] = None
        self.songs: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load the embedding model and song data."""
        if self._initialized:
            return

        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)

        # Load songs dataset
        songs_path = Path("data/songs.json")
        if songs_path.exists():
            with open(songs_path, "r", encoding="utf-8") as f:
                self.songs = json.load(f)
            logger.info(f"Loaded {len(self.songs)} songs from dataset")

            # Generate or load embeddings
            embeddings_path = Path("data/embeddings.npy")
            if embeddings_path.exists():
                self.embeddings = np.load(embeddings_path)
                logger.info("Loaded pre-computed embeddings")
            else:
                await self._generate_embeddings()
        else:
            logger.warning("Songs dataset not found. Run data/generate_dataset.py first.")

        self._initialized = True

    async def _generate_embeddings(self) -> None:
        """Generate embeddings for all songs."""
        logger.info("Generating embeddings for all songs...")
        texts = [self._song_to_text(song) for song in self.songs]
        self.embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=64)

        # Save embeddings
        embeddings_path = Path("data/embeddings.npy")
        embeddings_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(embeddings_path, self.embeddings)
        logger.info(f"Saved embeddings to {embeddings_path}")

    def _song_to_text(self, song: Dict[str, Any]) -> str:
        """Convert a song's metadata to a searchable text representation."""
        parts = [
            f"Title: {song.get('title', '')}",
            f"Artist: {song.get('artist', '')}",
            f"Album: {song.get('album', '')}",
            f"Genre: {song.get('genre', '')}",
            f"Sub-genre: {song.get('sub_genre', '')}",
            f"Mood: {song.get('mood', '')}",
            f"Language: {song.get('language', '')}",
            f"Year: {song.get('year', '')}",
            f"Description: {song.get('description', '')}",
        ]
        return " | ".join(parts)

    def search(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for songs similar to the query.

        Args:
            query: Natural language search query.
            top_k: Number of results to return.
            filters: Optional filters (genre, language, mood, etc.).

        Returns:
            List of songs with similarity scores.
        """
        if not self._initialized or self.embeddings is None:
            return []

        # Encode query
        query_embedding = self.model.encode([query])

        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()

        # Apply filters
        if filters:
            mask = np.ones(len(self.songs), dtype=bool)
            for key, value in filters.items():
                if value:
                    if isinstance(value, list):
                        mask &= np.array([
                            song.get(key, "").lower() in [v.lower() for v in value]
                            for song in self.songs
                        ])
                    else:
                        mask &= np.array([
                            value.lower() in song.get(key, "").lower()
                            for song in self.songs
                        ])
            similarities = similarities * mask

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                song = self.songs[idx].copy()
                song["match_score"] = round(float(similarities[idx]) * 100, 2)
                results.append(song)

        return results

    def find_similar(self, song_title: str, artist: Optional[str] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find songs similar to a given song.

        Args:
            song_title: Title of the reference song.
            artist: Optional artist name for better matching.
            top_k: Number of results to return.

        Returns:
            List of similar songs with scores.
        """
        if not self._initialized or self.embeddings is None:
            return []

        # Find the reference song
        ref_idx = None
        for i, song in enumerate(self.songs):
            title_match = song_title.lower() in song.get("title", "").lower()
            artist_match = True if not artist else artist.lower() in song.get("artist", "").lower()
            if title_match and artist_match:
                ref_idx = i
                break

        if ref_idx is not None:
            # Use the song's embedding directly
            ref_embedding = self.embeddings[ref_idx:ref_idx + 1]
        else:
            # Song not in dataset, encode the query
            query = f"Title: {song_title}"
            if artist:
                query += f" | Artist: {artist}"
            ref_embedding = self.model.encode([query])

        # Compute similarities
        similarities = np.dot(self.embeddings, ref_embedding.T).flatten()

        # Exclude the reference song itself
        if ref_idx is not None:
            similarities[ref_idx] = -1

        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                song = self.songs[idx].copy()
                song["match_score"] = round(float(similarities[idx]) * 100, 2)
                results.append(song)

        return results


# Singleton instance
embedding_engine = EmbeddingEngine()
