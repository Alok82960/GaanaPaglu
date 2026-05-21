"""Recommendation API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database.connection import get_db
from app.database.models import User, QueryHistory
from app.auth.utils import get_current_user
from app.recommendations.engine import recommendation_engine
from app.recommendations.schemas import (
    NaturalQueryRequest,
    SimilarSongRequest,
    MoodRequest,
    PreferenceBasedRequest,
    RecommendationResponse,
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.post("/query", response_model=RecommendationResponse)
async def recommend_by_query(
    request: NaturalQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Get recommendations based on natural language query."""
    logger.info(f"User {current_user.username} query: {request.query}")

    recommendations, summary = await recommendation_engine.recommend_by_query(
        query=request.query,
        num_results=request.num_results,
        user=current_user,
        db=db,
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for your query. Try a different search.",
        )

    # Log query history
    history = QueryHistory(
        user_id=current_user.id,
        query_text=request.query,
        query_type="natural",
        results_count=len(recommendations),
    )
    db.add(history)

    return RecommendationResponse(
        query=request.query,
        query_type="natural",
        total_results=len(recommendations),
        recommendations=recommendations,
        ai_summary=summary,
    )


@router.post("/similar", response_model=RecommendationResponse)
async def recommend_similar(
    request: SimilarSongRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Find songs similar to a given song."""
    logger.info(f"User {current_user.username} finding similar to: {request.song_title}")

    recommendations, summary = await recommendation_engine.recommend_similar(
        song_title=request.song_title,
        artist=request.artist,
        num_results=request.num_results,
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No similar songs found for '{request.song_title}'. Try another song.",
        )

    # Log query history
    query_text = f"Similar to: {request.song_title}" + (f" by {request.artist}" if request.artist else "")
    history = QueryHistory(
        user_id=current_user.id,
        query_text=query_text,
        query_type="similar",
        results_count=len(recommendations),
    )
    db.add(history)

    return RecommendationResponse(
        query=query_text,
        query_type="similar",
        total_results=len(recommendations),
        recommendations=recommendations,
        ai_summary=summary,
    )


@router.post("/mood", response_model=RecommendationResponse)
async def recommend_by_mood(
    request: MoodRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Get mood-based playlist recommendations."""
    logger.info(f"User {current_user.username} mood request: {request.mood}")

    recommendations, summary = await recommendation_engine.recommend_by_mood(
        mood=request.mood,
        num_results=request.num_results,
        language=request.language,
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No songs found for mood '{request.mood}'. Try a different mood.",
        )

    # Log query history
    history = QueryHistory(
        user_id=current_user.id,
        query_text=f"Mood: {request.mood}",
        query_type="mood",
        results_count=len(recommendations),
    )
    db.add(history)

    return RecommendationResponse(
        query=f"Mood: {request.mood}",
        query_type="mood",
        total_results=len(recommendations),
        recommendations=recommendations,
        ai_summary=summary,
    )


@router.post("/preferences", response_model=RecommendationResponse)
async def recommend_by_preferences(
    request: PreferenceBasedRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Get recommendations based on explicit preferences."""
    logger.info(f"User {current_user.username} preference-based request")

    recommendations, summary = await recommendation_engine.recommend_by_preferences(
        genres=request.genres,
        artists=request.artists,
        moods=request.moods,
        languages=request.languages,
        decade=request.decade,
        num_results=request.num_results,
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found for your preferences. Try broadening your criteria.",
        )

    # Log query history
    query_text = f"Preferences: genres={request.genres}, moods={request.moods}"
    history = QueryHistory(
        user_id=current_user.id,
        query_text=query_text,
        query_type="preference",
        results_count=len(recommendations),
    )
    db.add(history)

    return RecommendationResponse(
        query=query_text,
        query_type="preference",
        total_results=len(recommendations),
        recommendations=recommendations,
        ai_summary=summary,
    )


@router.get("/personalized", response_model=RecommendationResponse)
async def recommend_personalized(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RecommendationResponse:
    """Get personalized recommendations based on user history."""
    logger.info(f"User {current_user.username} personalized request")

    recommendations, summary = await recommendation_engine.recommend_personalized(
        user=current_user,
        db=db,
        num_results=10,
    )

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough data for personalized recommendations. Like some songs first!",
        )

    # Log query history
    history = QueryHistory(
        user_id=current_user.id,
        query_text="Personalized recommendations",
        query_type="personalized",
        results_count=len(recommendations),
    )
    db.add(history)

    return RecommendationResponse(
        query="Personalized recommendations",
        query_type="personalized",
        total_results=len(recommendations),
        recommendations=recommendations,
        ai_summary=summary,
    )
