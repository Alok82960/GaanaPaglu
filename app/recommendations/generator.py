"""GPT-Neo based natural language response generator."""

from typing import List, Dict, Any, Optional

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from loguru import logger

from app.config import get_settings

settings = get_settings()


class ResponseGenerator:
    """Generates natural language explanations for recommendations using GPT-Neo."""

    def __init__(self):
        """Initialize the response generator."""
        self.model = None
        self.tokenizer = None
        self.device = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load the GPT-Neo model and tokenizer."""
        if self._initialized:
            return

        logger.info(f"Loading language model: {settings.model_name}")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(settings.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )
        self.model.to(self.device)
        self.model.eval()

        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self._initialized = True
        logger.info("Language model loaded successfully")

    def generate_explanation(self, song: Dict[str, Any], query: str, query_type: str) -> str:
        """Generate a natural language explanation for why a song was recommended.

        Args:
            song: Song metadata dictionary.
            query: The user's original query.
            query_type: Type of recommendation (natural, similar, mood, etc.).

        Returns:
            Natural language explanation string.
        """
        if not self._initialized:
            return self._fallback_explanation(song, query, query_type)

        prompt = self._build_explanation_prompt(song, query, query_type)

        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2,
                )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated part
            explanation = generated[len(prompt):].strip()

            # Clean up - take first complete sentence(s)
            if "." in explanation:
                sentences = explanation.split(".")
                explanation = ". ".join(sentences[:2]).strip() + "."

            return explanation if explanation else self._fallback_explanation(song, query, query_type)

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._fallback_explanation(song, query, query_type)

    def generate_summary(self, songs: List[Dict[str, Any]], query: str, query_type: str) -> str:
        """Generate a summary for the entire recommendation set.

        Args:
            songs: List of recommended songs.
            query: The user's original query.
            query_type: Type of recommendation.

        Returns:
            Natural language summary string.
        """
        if not self._initialized:
            return self._fallback_summary(songs, query, query_type)

        # Build a concise prompt
        song_list = ", ".join([f"{s.get('title', '')} by {s.get('artist', '')}" for s in songs[:5]])
        prompt = (
            f"A music recommendation system found these songs for the query '{query}': {song_list}. "
            f"Summary of why these songs match:"
        )

        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2,
                )

            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            summary = generated[len(prompt):].strip()

            if "." in summary:
                sentences = summary.split(".")
                summary = ". ".join(sentences[:3]).strip() + "."

            return summary if summary else self._fallback_summary(songs, query, query_type)

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return self._fallback_summary(songs, query, query_type)

    def _build_explanation_prompt(self, song: Dict[str, Any], query: str, query_type: str) -> str:
        """Build a prompt for generating song explanations."""
        return (
            f"Explain why '{song.get('title', '')}' by {song.get('artist', '')} "
            f"({song.get('genre', '')}, {song.get('mood', '')} mood, {song.get('year', '')}) "
            f"is a good recommendation for someone who asked: '{query}'. "
            f"Reason:"
        )

    def _fallback_explanation(self, song: Dict[str, Any], query: str, query_type: str) -> str:
        """Generate a template-based explanation when the model is unavailable."""
        mood = song.get("mood", "great")
        genre = song.get("genre", "music")
        artist = song.get("artist", "this artist")
        year = song.get("year", "")

        explanations = {
            "natural": f"This {mood.lower()} {genre.lower()} track matches your vibe perfectly. {artist}'s style aligns with what you're looking for.",
            "similar": f"This song shares similar {genre.lower()} elements and {mood.lower()} energy that you enjoy.",
            "mood": f"With its {mood.lower()} atmosphere, this {genre.lower()} track from {year} sets exactly the right tone.",
            "preference": f"Based on your love for {genre.lower()} and {mood.lower()} music, this {artist} track is a natural fit.",
            "personalized": f"Your listening history shows you enjoy {mood.lower()} {genre.lower()} — this track delivers exactly that.",
        }

        return explanations.get(query_type, explanations["natural"])

    def _fallback_summary(self, songs: List[Dict[str, Any]], query: str, query_type: str) -> str:
        """Generate a template-based summary when the model is unavailable."""
        genres = list(set(s.get("genre", "") for s in songs[:5]))
        moods = list(set(s.get("mood", "") for s in songs[:5]))

        genre_text = ", ".join(genres[:3]) if genres else "various genres"
        mood_text = ", ".join(moods[:3]) if moods else "various moods"

        return (
            f"Here are {len(songs)} recommendations spanning {genre_text} with "
            f"{mood_text} vibes. These tracks were selected based on your query "
            f"and should match what you're looking for."
        )


# Singleton instance
response_generator = ResponseGenerator()
