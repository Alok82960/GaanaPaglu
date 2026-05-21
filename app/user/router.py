"""User preference and history routes."""

import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from app.database.connection import get_db
from app.database.models import User, UserPreference, UserInteraction, QueryHistory
from app.auth.utils import get_current_user
from app.user.schemas import PreferenceUpdate, PreferenceResponse, SongInteraction, InteractionResponse, UserHistoryResponse

router = APIRouter(prefix="/user", tags=["User"])


@router.put("/preferences", response_model=PreferenceResponse)
def update_preferences(prefs: PreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not user_prefs:
        user_prefs = UserPreference(user_id=current_user.id)
        db.add(user_prefs)

    if prefs.favorite_genres is not None:
        user_prefs.favorite_genres = json.dumps(prefs.favorite_genres)
    if prefs.favorite_artists is not None:
        user_prefs.favorite_artists = json.dumps(prefs.favorite_artists)
    if prefs.favorite_moods is not None:
        user_prefs.favorite_moods = json.dumps(prefs.favorite_moods)
    if prefs.preferred_languages is not None:
        user_prefs.preferred_languages = json.dumps(prefs.preferred_languages)
    if prefs.preferred_decades is not None:
        user_prefs.preferred_decades = json.dumps(prefs.preferred_decades)
    if prefs.min_tempo is not None:
        user_prefs.min_tempo = prefs.min_tempo
    if prefs.max_tempo is not None:
        user_prefs.max_tempo = prefs.max_tempo

    db.flush()
    return PreferenceResponse(
        favorite_genres=json.loads(user_prefs.favorite_genres),
        favorite_artists=json.loads(user_prefs.favorite_artists),
        favorite_moods=json.loads(user_prefs.favorite_moods),
        preferred_languages=json.loads(user_prefs.preferred_languages),
        preferred_decades=json.loads(user_prefs.preferred_decades),
        min_tempo=user_prefs.min_tempo, max_tempo=user_prefs.max_tempo,
        updated_at=user_prefs.updated_at,
    )


@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not user_prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return PreferenceResponse(
        favorite_genres=json.loads(user_prefs.favorite_genres),
        favorite_artists=json.loads(user_prefs.favorite_artists),
        favorite_moods=json.loads(user_prefs.favorite_moods),
        preferred_languages=json.loads(user_prefs.preferred_languages),
        preferred_decades=json.loads(user_prefs.preferred_decades),
        min_tempo=user_prefs.min_tempo, max_tempo=user_prefs.max_tempo,
        updated_at=user_prefs.updated_at,
    )


@router.post("/like", response_model=InteractionResponse, status_code=201)
def like_song(song: SongInteraction, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserInteraction).filter(UserInteraction.user_id == current_user.id, UserInteraction.song_id == song.song_id).first()
    if existing:
        existing.interaction_type = "like"
        db.flush()
        return existing
    interaction = UserInteraction(user_id=current_user.id, song_id=song.song_id, song_title=song.song_title, song_artist=song.song_artist, interaction_type="like")
    db.add(interaction)
    db.flush()
    return interaction


@router.post("/dislike", response_model=InteractionResponse, status_code=201)
def dislike_song(song: SongInteraction, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserInteraction).filter(UserInteraction.user_id == current_user.id, UserInteraction.song_id == song.song_id).first()
    if existing:
        existing.interaction_type = "dislike"
        db.flush()
        return existing
    interaction = UserInteraction(user_id=current_user.id, song_id=song.song_id, song_title=song.song_title, song_artist=song.song_artist, interaction_type="dislike")
    db.add(interaction)
    db.flush()
    return interaction


@router.get("/history", response_model=UserHistoryResponse)
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    likes = db.query(UserInteraction).filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == "like").order_by(UserInteraction.created_at.desc()).limit(50).all()
    dislikes = db.query(UserInteraction).filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == "dislike").order_by(UserInteraction.created_at.desc()).limit(50).all()
    queries = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id).order_by(QueryHistory.created_at.desc()).limit(20).all()
    total_likes = db.query(func.count(UserInteraction.id)).filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == "like").scalar() or 0
    total_dislikes = db.query(func.count(UserInteraction.id)).filter(UserInteraction.user_id == current_user.id, UserInteraction.interaction_type == "dislike").scalar() or 0
    total_queries = db.query(func.count(QueryHistory.id)).filter(QueryHistory.user_id == current_user.id).scalar() or 0

    return UserHistoryResponse(likes=likes, dislikes=dislikes, recent_queries=queries, total_likes=total_likes, total_dislikes=total_dislikes, total_queries=total_queries)
