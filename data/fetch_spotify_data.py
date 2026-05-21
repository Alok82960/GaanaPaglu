"""Fetch 5000 songs from Spotify API across multiple genres and languages.

Usage:
    python data/fetch_spotify_data.py

Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file.
"""

import json
import os
import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Any

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
    sys.exit(1)

# Initialize Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ),
    requests_timeout=30,
    retries=3,
)

# --- Configuration ---

# Playlists to fetch from (curated for Hindi, English, Punjabi, Haryanvi)
PLAYLISTS = {
    # Hindi / Bollywood
    "37i9dQZF1DX0XUfTFmNBRM": "Bollywood Butter",
    "37i9dQZF1DX4WlGnBiHnHi": "Bollywood 90s",
    "37i9dQZF1DX7cLxqtNO3zl": "Bollywood 2000s",
    "37i9dQZF1DWVlYsZJXqdym": "Hindi Hits",
    "37i9dQZF1DX0PmMzHBfvE9": "Bollywood Romantic",
    "37i9dQZF1DX5q67ZpWyRrZ": "Bollywood Party",
    "37i9dQZF1DX18jTM2l2fJY": "Hindi Indie",
    "37i9dQZF1DX6XceWZP1znY": "Bollywood Unplugged",
    "37i9dQZF1DWVwmhXMnVtrG": "Bollywood Sad Songs",
    "37i9dQZF1DX4g8Gs5nUhpp": "Desi Hip Hop",

    # Punjabi
    "37i9dQZF1DX5cZuAHLNjGz": "Punjabi 101",
    "37i9dQZF1DWVeMYnpcVRp2": "Punjabi Hits",
    "37i9dQZF1DX8Iw4Gu2xJ3F": "Punjabi Party",

    # English - Pop/Rock/Hip-Hop
    "37i9dQZF1DXcBWIGoYBM5M": "Today's Top Hits",
    "37i9dQZF1DX0kbJZpiYdZl": "Hot Hits USA",
    "37i9dQZF1DWXRqgorJj26U": "Rock Classics",
    "37i9dQZF1DX4SBhb3fqCJd": "All Out 80s",
    "37i9dQZF1DX4o1oenSJRJd": "All Out 2000s",
    "37i9dQZF1DX2Nc3B70tvx0": "All Out 90s",
    "37i9dQZF1DX186v583rmzp": "All Out 70s",
    "37i9dQZF1DX10zKzsJ2jva": "All Out 2010s",
    "37i9dQZF1DX18jTM2l2fJY": "Indie Pop",
    "37i9dQZF1DX0XUsuxWHRQd": "RapCaviar",
    "37i9dQZF1DWWEJlAGA9gs0": "Classical Essentials",
    "37i9dQZF1DX4dyzvuaRJ0n": "Jazz Classics",
    "37i9dQZF1DX1lVhptIYRda": "Hot Hits UK",

    # Haryanvi
    "37i9dQZF1DX0Tkc6ltcBfU": "Haryanvi Hits",
}

# Genre-based search queries for additional diversity
SEARCH_QUERIES = [
    # Hindi / Bollywood - Artists
    "arijit singh", "neha kakkar", "atif aslam", "shreya ghoshal",
    "kishore kumar", "lata mangeshkar", "ar rahman", "pritam",
    "vishal shekhar", "amit trivedi", "badshah", "honey singh",
    "sonu nigam", "kumar sanu", "udit narayan", "alka yagnik",
    "jubin nautiyal", "darshan raval", "armaan malik", "mohit chauhan",
    "sunidhi chauhan", "mika singh", "shankar mahadevan", "kk singer",
    "rahat fateh ali khan", "stebin ben", "b praak", "asees kaur",
    "sachet tandon", "tulsi kumar", "palak muchhal", "ankit tiwari",
    "guru randhawa bollywood", "raftaar", "divine rapper",
    # Hindi / Bollywood - Themes
    "bollywood hits", "hindi romantic", "hindi sad songs",
    "bollywood dance", "hindi unplugged", "bollywood 90s",
    "bollywood 2000s", "bollywood party", "hindi love songs",
    "bollywood wedding", "hindi devotional", "bollywood retro",
    "hindi lofi", "bollywood mashup", "hindi sufi songs",
    "bollywood rain songs", "hindi heartbreak", "bollywood item songs",
    "hindi ghazal", "bollywood qawwali", "hindi motivational",
    "bollywood new releases", "hindi pop", "bollywood rock",
    "hindi acoustic", "bollywood unplugged covers",
    # Punjabi - Artists
    "sidhu moose wala", "diljit dosanjh", "ap dhillon", "karan aujla",
    "babbu maan", "gurdas maan", "guru randhawa", "harrdy sandhu",
    "jassie gill", "ammy virk", "parmish verma", "jazzy b",
    "garry sandhu", "mankirt aulakh", "sharry mann", "ninja punjabi",
    "ranjit bawa", "kaur b", "nimrat khaira", "sunanda sharma",
    "jass manak", "kaka punjabi singer", "shubh singer",
    # Punjabi - Themes
    "punjabi bhangra", "punjabi romantic", "punjabi sad",
    "punjabi party", "punjabi wedding", "punjabi bass",
    "punjabi hip hop", "punjabi folk", "punjabi new songs",
    "punjabi love songs", "punjabi dance", "punjabi hits 2024",
    # Haryanvi
    "haryanvi dj", "haryanvi songs", "sapna choudhary",
    "haryanvi dance", "raju punjabi haryanvi", "haryanvi folk",
    "haryanvi new songs", "md kd haryanvi", "gulzaar chhaniwala",
    "haryanvi party", "haryanvi romantic", "renuka panwar",
    "haryanvi hits 2024", "haryanvi bass", "pranjal dahiya",
    "vishvajeet choudhary", "uk haryanvi", "haryanvi mashup",
    # English - Pop
    "pop hits 2024", "taylor swift", "ed sheeran", "dua lipa",
    "the weeknd", "billie eilish", "harry styles", "olivia rodrigo",
    "ariana grande", "justin bieber", "shawn mendes", "charlie puth",
    "bruno mars", "adele", "sam smith", "sia singer",
    "imagine dragons", "coldplay", "maroon 5", "one direction",
    # English - Hip-Hop/Rap
    "drake", "kendrick lamar", "eminem", "post malone",
    "travis scott", "j cole", "kanye west", "lil nas x",
    "doja cat", "megan thee stallion", "cardi b", "21 savage",
    # English - Rock
    "rock classics", "linkin park", "green day", "nirvana",
    "queen band", "ac dc", "metallica", "foo fighters",
    "arctic monkeys", "radiohead", "red hot chili peppers",
    # English - Other
    "edm dance", "indie folk", "r&b soul", "country hits",
    "jazz smooth", "classical piano", "electronic chill",
    "alternative indie", "reggaeton hits", "latin pop",
    # English - Decades
    "80s hits", "90s hits", "2000s hits", "2010s hits",
    "70s rock", "60s classics",
    # More variety
    "workout music", "study music", "chill vibes",
    "road trip songs", "party anthems", "sleep music",
    "morning motivation", "evening relaxation",
]

# Mood mapping based on audio features
MOOD_MAP = {
    "Energetic": {"min_energy": 0.7, "min_valence": 0.5},
    "Chill": {"max_energy": 0.5, "min_valence": 0.3},
    "Melancholic": {"max_valence": 0.3, "max_energy": 0.5},
    "Romantic": {"min_valence": 0.4, "max_energy": 0.6},
    "Dark": {"max_valence": 0.3, "min_energy": 0.4},
    "Happy": {"min_valence": 0.7, "min_energy": 0.5},
    "Aggressive": {"min_energy": 0.8, "max_valence": 0.4},
    "Peaceful": {"max_energy": 0.4, "min_valence": 0.4},
}


def determine_mood(features: Dict[str, Any]) -> str:
    """Determine song mood from audio features."""
    if not features:
        return "Unknown"

    energy = features.get("energy", 0.5)
    valence = features.get("valence", 0.5)

    if energy > 0.7 and valence > 0.6:
        return "Energetic"
    elif energy > 0.8 and valence < 0.4:
        return "Aggressive"
    elif energy < 0.4 and valence > 0.5:
        return "Peaceful"
    elif energy < 0.5 and valence < 0.3:
        return "Melancholic"
    elif valence > 0.7:
        return "Happy"
    elif valence < 0.3:
        return "Dark"
    elif energy < 0.5:
        return "Chill"
    elif 0.4 <= valence <= 0.7 and energy < 0.6:
        return "Romantic"
    else:
        return "Energetic"


def determine_language(track: Dict[str, Any], playlist_name: str = "") -> str:
    """Determine song language based on context."""
    # Check playlist context
    playlist_lower = playlist_name.lower()
    if any(word in playlist_lower for word in ["bollywood", "hindi", "desi"]):
        return "Hindi"
    elif "punjabi" in playlist_lower:
        return "Punjabi"
    elif "haryanvi" in playlist_lower:
        return "Haryanvi"

    # Check market availability and artist info
    markets = track.get("available_markets", [])
    artist_name = track.get("artists", [{}])[0].get("name", "").lower()

    # Known Hindi/Bollywood artists
    hindi_artists = [
        "arijit", "neha kakkar", "atif", "shreya", "kishore", "lata",
        "sonu nigam", "kumar sanu", "udit narayan", "alka yagnik",
        "pritam", "vishal", "amit trivedi", "ar rahman", "badshah",
    ]
    punjabi_artists = [
        "sidhu", "diljit", "ap dhillon", "karan aujla", "babbu maan",
        "gurdas maan", "guru randhawa", "harrdy sandhu", "jassie gill",
    ]
    haryanvi_artists = [
        "sapna choudhary", "raju punjabi", "md kd", "gulzaar",
    ]

    for a in hindi_artists:
        if a in artist_name:
            return "Hindi"
    for a in punjabi_artists:
        if a in artist_name:
            return "Punjabi"
    for a in haryanvi_artists:
        if a in artist_name:
            return "Haryanvi"

    return "English"


def determine_genre(track: Dict[str, Any], artist_genres: List[str]) -> tuple:
    """Determine genre and sub-genre from artist genres."""
    genre_mapping = {
        "Bollywood": ["bollywood", "filmi", "hindi"],
        "Pop": ["pop", "dance pop", "electropop", "synth-pop"],
        "Hip-Hop": ["hip hop", "rap", "trap", "drill"],
        "Rock": ["rock", "alternative", "punk", "grunge", "metal"],
        "R&B": ["r&b", "soul", "neo soul", "funk"],
        "Electronic": ["electronic", "edm", "house", "techno", "trance"],
        "Classical": ["classical", "orchestra", "piano"],
        "Jazz": ["jazz", "blues", "swing"],
        "Folk": ["folk", "acoustic", "singer-songwriter"],
        "Country": ["country", "americana"],
        "Punjabi": ["punjabi", "bhangra"],
        "Indie": ["indie", "lo-fi", "bedroom pop"],
        "Metal": ["metal", "heavy metal", "death metal"],
        "Reggae": ["reggae", "dancehall", "ska"],
    }

    genre = "Pop"  # Default
    sub_genre = ""

    for main_genre, keywords in genre_mapping.items():
        for ag in artist_genres:
            ag_lower = ag.lower()
            for keyword in keywords:
                if keyword in ag_lower:
                    genre = main_genre
                    sub_genre = ag
                    return genre, sub_genre

    return genre, sub_genre


def generate_description(track: Dict[str, Any], genre: str, mood: str, language: str) -> str:
    """Generate a brief description for the song."""
    artist = track.get("artists", [{}])[0].get("name", "Unknown")
    year = track.get("album", {}).get("release_date", "")[:4]
    album = track.get("album", {}).get("name", "")

    templates = [
        f"A {mood.lower()} {genre.lower()} track by {artist} from the album '{album}' ({year}). Perfect for {mood.lower()} vibes.",
        f"{artist}'s {mood.lower()} {language.lower()} {genre.lower()} song that captures the essence of {mood.lower()} energy.",
        f"Released in {year}, this {genre.lower()} gem by {artist} delivers {mood.lower()} vibes with its unique sound.",
        f"From '{album}', {artist} brings a {mood.lower()} {genre.lower()} experience in {language}.",
    ]

    return random.choice(templates)


def fetch_playlist_tracks(playlist_id: str, playlist_name: str) -> List[Dict[str, Any]]:
    """Fetch all tracks from a playlist."""
    tracks = []
    try:
        results = sp.playlist_tracks(playlist_id, limit=100)
        while results:
            for item in results.get("items", []):
                track = item.get("track")
                if track and track.get("id"):
                    track["_playlist_name"] = playlist_name
                    tracks.append(track)
            if results.get("next"):
                results = sp.next(results)
                time.sleep(0.1)  # Rate limit respect
            else:
                break
    except Exception as e:
        print(f"  Error fetching playlist {playlist_name}: {e}")

    return tracks


def fetch_search_tracks(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch tracks from search query with pagination."""
    tracks = []
    # Spotify dev mode limits to 10 per request, so paginate
    max_per_request = min(limit, 10)
    offsets = range(0, limit, max_per_request)

    for offset in offsets:
        try:
            results = sp.search(q=query, type="track", limit=max_per_request, offset=offset, market="IN")
            items = results.get("tracks", {}).get("items", [])
            if not items:
                break
            for item in items:
                if item.get("id"):
                    item["_playlist_name"] = query
                    tracks.append(item)
            time.sleep(0.2)
        except Exception as e:
            print(f"  Error searching '{query}' (offset {offset}): {e}")
            break

    return tracks


def get_audio_features_batch(track_ids: List[str]) -> Dict[str, Dict]:
    """Get audio features for a batch of tracks."""
    features_map = {}
    # Spotify allows max 100 IDs per request
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        try:
            features = sp.audio_features(batch)
            for f in features:
                if f:
                    features_map[f["id"]] = f
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching audio features: {e}")

    return features_map


def get_artist_genres(artist_ids: List[str]) -> Dict[str, List[str]]:
    """Get genres for a batch of artists."""
    genres_map = {}
    # Spotify allows max 50 artists per request
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        try:
            artists = sp.artists(batch)
            for artist in artists.get("artists", []):
                if artist:
                    genres_map[artist["id"]] = artist.get("genres", [])
            time.sleep(0.1)
        except Exception as e:
            print(f"  Error fetching artist genres: {e}")

    return genres_map


def process_tracks(raw_tracks: List[Dict[str, Any]], target_count: int = 5000) -> List[Dict[str, Any]]:
    """Process raw tracks into our dataset format."""
    print(f"\nProcessing {len(raw_tracks)} raw tracks...")

    # Deduplicate by track ID
    seen_ids = set()
    unique_tracks = []
    for track in raw_tracks:
        track_id = track.get("id")
        if track_id and track_id not in seen_ids:
            seen_ids.add(track_id)
            unique_tracks.append(track)

    print(f"Unique tracks after dedup: {len(unique_tracks)}")

    # Limit to target count
    if len(unique_tracks) > target_count:
        unique_tracks = random.sample(unique_tracks, target_count)

    # Get audio features
    track_ids = [t["id"] for t in unique_tracks]
    print("Fetching audio features...")
    audio_features = get_audio_features_batch(track_ids)

    # Get artist genres
    artist_ids = list(set(
        t.get("artists", [{}])[0].get("id", "")
        for t in unique_tracks
        if t.get("artists")
    ))
    artist_ids = [aid for aid in artist_ids if aid]
    print("Fetching artist genres...")
    artist_genres = get_artist_genres(artist_ids)

    # Process each track
    print("Building dataset...")
    songs = []
    for track in unique_tracks:
        try:
            track_id = track["id"]
            features = audio_features.get(track_id, {})
            artist = track.get("artists", [{}])[0]
            artist_id = artist.get("id", "")
            genres = artist_genres.get(artist_id, [])
            playlist_name = track.get("_playlist_name", "")

            # Determine attributes
            language = determine_language(track, playlist_name)
            genre, sub_genre = determine_genre(track, genres)
            mood = determine_mood(features)

            # Build song entry
            song = {
                "song_id": track_id,
                "title": track.get("name", "Unknown"),
                "artist": artist.get("name", "Unknown"),
                "album": track.get("album", {}).get("name", "Unknown"),
                "genre": genre,
                "sub_genre": sub_genre if sub_genre else genre,
                "year": int(track.get("album", {}).get("release_date", "2000")[:4]),
                "duration_ms": track.get("duration_ms", 200000),
                "mood": mood,
                "tempo": features.get("tempo", 120.0),
                "language": language,
                "popularity": track.get("popularity", 50),
                "description": generate_description(track, genre, mood, language),
            }
            songs.append(song)

        except Exception as e:
            continue

    return songs


def main():
    """Main function to fetch and process Spotify data."""
    print("=" * 60)
    print("🎵 GaanaPaglu - Spotify Data Fetcher")
    print("=" * 60)
    print(f"\nTarget: 5000 songs")
    print(f"Languages: Hindi, English, Punjabi, Haryanvi")
    print(f"Time range: All time")
    print()

    all_tracks = []

    # Fetch from search queries (primary method due to API restrictions)
    print("🔍 Fetching from search queries...")
    for i, query in enumerate(SEARCH_QUERIES):
        print(f"  [{i+1}/{len(SEARCH_QUERIES)}] '{query}'...", end=" ")
        tracks = fetch_search_tracks(query, limit=40)
        print(f"({len(tracks)} tracks)")
        all_tracks.extend(tracks)
        time.sleep(0.3)

        # Check if we have enough
        if len(all_tracks) >= 6000:
            print(f"\n  Reached {len(all_tracks)} tracks, stopping early.")
            break

    print(f"\nTotal raw tracks: {len(all_tracks)}")

    # Process into dataset
    songs = process_tracks(all_tracks, target_count=5000)

    # Save dataset
    output_path = Path("data/songs.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(songs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset saved: {output_path}")
    print(f"   Total songs: {len(songs)}")

    # Print stats
    languages = {}
    genres = {}
    moods = {}
    for song in songs:
        lang = song["language"]
        languages[lang] = languages.get(lang, 0) + 1
        g = song["genre"]
        genres[g] = genres.get(g, 0) + 1
        m = song["mood"]
        moods[m] = moods.get(m, 0) + 1

    print("\n📊 Dataset Statistics:")
    print("\n  Languages:")
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        print(f"    {lang}: {count} ({count*100//len(songs)}%)")

    print("\n  Top Genres:")
    for genre, count in sorted(genres.items(), key=lambda x: -x[1])[:10]:
        print(f"    {genre}: {count}")

    print("\n  Moods:")
    for mood, count in sorted(moods.items(), key=lambda x: -x[1]):
        print(f"    {mood}: {count}")


if __name__ == "__main__":
    main()
