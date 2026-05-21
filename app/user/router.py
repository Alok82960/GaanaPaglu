"""User preference and history API routes."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger

from app.database.connection import get_db
from app.database.models import User, UserPreference, UserInteraction, QueryHistory
from app.auth.utils import get_current_user
from app.user.schemas import (
    PreferenceUpdate,
    PreferenceResponse,
    SongInteraction,
    InteractionResponse,
    UserHistoryResponse,
    QueryHistoryResponse,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.put("/preferences", response_model=PreferenceResponse)
async def update_preferences(
    prefs: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PreferenceResponse:
    """Update user music preferences."""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    user_prefs = result.scalar_one_or_none()

    if not user_prefs:
        user_prefs = UserPreference(user_id=current_user.id)
        db.add(user_prefs)

    # Update only provided fields
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

    await db.flush()
    logger.info(f"Preferences updated for user: {current_user.username}")

    return PreferenceResponse(
        favorite_genres=json.loads(user_prefs.favorite_genres),
        favorite_artists=json.loads(user_prefs.favorite_artists),
        favorite_moods=json.loads(user_prefs.favorite_moods),
        preferred_languages=json.loads(user_prefs.preferred_languages),
        preferred_decades=json.loads(user_prefs.preferred_decades),
        min_tempo=user_prefs.min_tempo,
        max_tempo=user_prefs.max_tempo,
        updated_at=user_prefs.updated_at,
    )


@router.get("/preferences", response_model=PreferenceResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PreferenceResponse:
    """Get current user preferences."""
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    user_prefs = result.scalar_one_or_none()

    if not user_prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found. Update preferences first.",
        )

    return PreferenceResponse(
        favorite_genres=json.loads(user_prefs.favorite_genres),
        favorite_artists=json.loads(user_prefs.favorite_artists),
        favorite_moods=json.loads(user_prefs.favorite_moods),
        preferred_languages=json.loads(user_prefs.preferred_languages),
        preferred_decades=json.loads(user_prefs.preferred_decades),
        min_tempo=user_prefs.min_tempo,
        max_tempo=user_prefs.max_tempo,
        updated_at=user_prefs.updated_at,
    )


@router.post("/like", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def like_song(
    song: SongInteraction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InteractionResponse:
    """Like a song."""
    # Remove existing dislike if any
    result = await db.execute(
        select(UserInteraction).where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.song_id == song.song_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.interaction_type = "like"
        await db.flush()
        return existing

    interaction = UserInteraction(
        user_id=current_user.id,
        song_id=song.song_id,
        song_title=song.song_title,
        song_artist=song.song_artist,
        interaction_type="like",
    )
    db.add(interaction)
    await db.flush()

    logger.info(f"User {current_user.username} liked: {song.song_title}")
    return interaction


@router.post("/dislike", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def dislike_song(
    song: SongInteraction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InteractionResponse:
    """Dislike a song."""
    result = await db.execute(
        select(UserInteraction).where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.song_id == song.song_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.interaction_type = "dislike"
        await db.flush()
        return existing

    interaction = UserInteraction(
        user_id=current_user.id,
        song_id=song.song_id,
        song_title=song.song_title,
        song_artist=song.song_artist,
        interaction_type="dislike",
    )
    db.add(interaction)
    await db.flush()

    logger.info(f"User {current_user.username} disliked: {song.song_title}")
    return interaction


@router.get("/history", response_model=UserHistoryResponse)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserHistoryResponse:
    """Get user interaction history."""
    # Get likes
    likes_result = await db.execute(
        select(UserInteraction)
        .where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.interaction_type == "like",
        )
        .order_by(UserInteraction.created_at.desc())
        .limit(50)
    )
    likes = likes_result.scalars().all()

    # Get dislikes
    dislikes_result = await db.execute(
        select(UserInteraction)
        .where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.interaction_type == "dislike",
        )
        .order_by(UserInteraction.created_at.desc())
        .limit(50)
    )
    dislikes = dislikes_result.scalars().all()

    # Get recent queries
    queries_result = await db.execute(
        select(QueryHistory)
        .where(QueryHistory.user_id == current_user.id)
        .order_by(QueryHistory.created_at.desc())
        .limit(20)
    )
    queries = queries_result.scalars().all()

    # Get totals
    total_likes = await db.execute(
        select(func.count(UserInteraction.id)).where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.interaction_type == "like",
        )
    )
    total_dislikes = await db.execute(
        select(func.count(UserInteraction.id)).where(
            UserInteraction.user_id == current_user.id,
            UserInteraction.interaction_type == "dislike",
        )
    )
    total_queries = await db.execute(
        select(func.count(QueryHistory.id)).where(
            QueryHistory.user_id == current_user.id
        )
    )

    return UserHistoryResponse(
        likes=likes,
        dislikes=dislikes,
        recent_queries=queries,
        total_likes=total_likes.scalar() or 0,
        total_dislikes=total_dislikes.scalar() or 0,
        total_queries=total_queries.scalar() or 0,
    )
