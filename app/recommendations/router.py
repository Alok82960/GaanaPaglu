"""Recommendation API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from app.database.connection import get_db
from app.database.models import User, QueryHistory
from app.auth.utils import get_current_user
from app.recommendations.engine import recommendation_engine
from app.recommendations.schemas import (
    NaturalQueryRequest, SimilarSongRequest, MoodRequest,
    PreferenceBasedRequest, RecommendationResponse,
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.post("/query", response_model=RecommendationResponse)
def recommend_by_query(request: NaturalQueryRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"User {current_user.username} query: {request.query}")
    recommendations, summary = recommendation_engine.recommend_by_query(request.query, request.num_results)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")
    db.add(QueryHistory(user_id=current_user.id, query_text=request.query, query_type="natural", results_count=len(recommendations)))
    return RecommendationResponse(query=request.query, query_type="natural", total_results=len(recommendations), recommendations=recommendations, ai_summary=summary)


@router.post("/similar", response_model=RecommendationResponse)
def recommend_similar(request: SimilarSongRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recommendations, summary = recommendation_engine.recommend_similar(request.song_title, request.artist, request.num_results)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No similar songs found")
    query_text = f"Similar to: {request.song_title}"
    db.add(QueryHistory(user_id=current_user.id, query_text=query_text, query_type="similar", results_count=len(recommendations)))
    return RecommendationResponse(query=query_text, query_type="similar", total_results=len(recommendations), recommendations=recommendations, ai_summary=summary)


@router.post("/mood", response_model=RecommendationResponse)
def recommend_by_mood(request: MoodRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recommendations, summary = recommendation_engine.recommend_by_mood(request.mood, request.num_results, request.language)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No songs found for this mood")
    db.add(QueryHistory(user_id=current_user.id, query_text=f"Mood: {request.mood}", query_type="mood", results_count=len(recommendations)))
    return RecommendationResponse(query=f"Mood: {request.mood}", query_type="mood", total_results=len(recommendations), recommendations=recommendations, ai_summary=summary)


@router.post("/preferences", response_model=RecommendationResponse)
def recommend_by_preferences(request: PreferenceBasedRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query_parts = []
    if request.genres: query_parts.append(" ".join(request.genres))
    if request.moods: query_parts.append(" ".join(request.moods))
    if request.languages: query_parts.append(" ".join(request.languages))
    query = " ".join(query_parts) or "popular music"
    recommendations, summary = recommendation_engine.recommend_by_query(query, request.num_results)
    if not recommendations:
        raise HTTPException(status_code=404, detail="No recommendations found")
    db.add(QueryHistory(user_id=current_user.id, query_text=query, query_type="preference", results_count=len(recommendations)))
    return RecommendationResponse(query=query, query_type="preference", total_results=len(recommendations), recommendations=recommendations, ai_summary=summary)


@router.get("/personalized", response_model=RecommendationResponse)
def recommend_personalized(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Build query from user's liked songs
    from app.database.models import UserInteraction, UserPreference
    import json

    query_parts = []
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if prefs:
        genres = json.loads(prefs.favorite_genres) if prefs.favorite_genres else []
        moods = json.loads(prefs.favorite_moods) if prefs.favorite_moods else []
        if genres: query_parts.extend(genres[:3])
        if moods: query_parts.extend(moods[:2])

    likes = db.query(UserInteraction).filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == "like").limit(5).all()
    for like in likes:
        query_parts.append(like.song_artist)

    query = " ".join(query_parts) if query_parts else "bollywood romantic popular hits"
    recommendations, summary = recommendation_engine.recommend_by_query(query, 10)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Not enough data for personalized recommendations")
    return RecommendationResponse(query="Personalized", query_type="personalized", total_results=len(recommendations), recommendations=recommendations, ai_summary=summary)
