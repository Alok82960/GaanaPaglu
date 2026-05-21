"""Lightweight TF-IDF based song search - works within 512MB RAM."""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger


class EmbeddingEngine:
    """Lightweight recommendation engine using TF-IDF similarity."""

    def __init__(self):
        self.songs: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load songs and build TF-IDF index."""
        if self._initialized:
            return

        # Load songs
        songs_path = Path("data/songs.json")
        if songs_path.exists():
            with open(songs_path, "r", encoding="utf-8") as f:
                self.songs = json.load(f)
            logger.info(f"Loaded {len(self.songs)} songs")

            # Build TF-IDF index
            texts = [self._song_to_text(song) for song in self.songs]
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            logger.info("TF-IDF index built successfully")
        else:
            logger.warning("Songs dataset not found!")

        self._initialized = True

    def _song_to_text(self, song: Dict[str, Any]) -> str:
        """Convert song metadata to searchable text."""
        parts = [
            song.get("title", ""),
            song.get("artist", ""),
            song.get("album", ""),
            song.get("genre", ""),
            song.get("sub_genre", ""),
            song.get("mood", ""),
            song.get("language", ""),
            str(song.get("year", "")),
            song.get("description", ""),
            song.get("mood", ""),
            song.get("genre", ""),
        ]
        return " ".join(parts).lower()

    def search(self, query: str, top_k: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search songs by query."""
        if not self._initialized or self.tfidf_matrix is None:
            return []

        # Transform query
        query_vec = self.vectorizer.transform([query.lower()])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Apply filters
        if filters:
            for key, value in filters.items():
                if value:
                    if isinstance(value, list):
                        mask = np.array([
                            song.get(key, "").lower() in [v.lower() for v in value]
                            for song in self.songs
                        ])
                    else:
                        mask = np.array([
                            value.lower() in song.get(key, "").lower()
                            for song in self.songs
                        ])
                    similarities = similarities * mask

        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                song = self.songs[idx].copy()
                song["match_score"] = round(float(similarities[idx]) * 100, 2)
                results.append(song)

        return results

    def find_similar(self, song_title: str, artist: Optional[str] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Find similar songs."""
        if not self._initialized or self.tfidf_matrix is None:
            return []

        # Find reference song
        ref_idx = None
        for i, song in enumerate(self.songs):
            if song_title.lower() in song.get("title", "").lower():
                if not artist or artist.lower() in song.get("artist", "").lower():
                    ref_idx = i
                    break

        if ref_idx is not None:
            similarities = cosine_similarity(
                self.tfidf_matrix[ref_idx:ref_idx+1], self.tfidf_matrix
            ).flatten()
            similarities[ref_idx] = -1  # Exclude self
        else:
            query = f"{song_title} {artist or ''}"
            query_vec = self.vectorizer.transform([query.lower()])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                song = self.songs[idx].copy()
                song["match_score"] = round(float(similarities[idx]) * 100, 2)
                results.append(song)

        return results


# Singleton
embedding_engine = EmbeddingEngine()
