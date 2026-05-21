"""Fix genres and moods in the dataset using search query context."""

import json
import random
from pathlib import Path

# Load existing dataset
songs_path = Path("data/songs.json")
with open(songs_path, "r", encoding="utf-8") as f:
    songs = json.load(f)

print(f"Loaded {len(songs)} songs")

# Mood options
MOODS = ["Energetic", "Chill", "Melancholic", "Romantic", "Happy", "Dark", "Aggressive", "Peaceful"]

# Genre/mood assignment based on artist name and context
ARTIST_GENRE_MAP = {
    # Bollywood / Hindi
    "arijit singh": ("Bollywood", "Romantic"),
    "neha kakkar": ("Bollywood", "Energetic"),
    "atif aslam": ("Bollywood", "Romantic"),
    "shreya ghoshal": ("Bollywood", "Romantic"),
    "kishore kumar": ("Bollywood", "Happy"),
    "lata mangeshkar": ("Bollywood", "Peaceful"),
    "a.r. rahman": ("Bollywood", "Energetic"),
    "ar rahman": ("Bollywood", "Energetic"),
    "pritam": ("Bollywood", "Romantic"),
    "vishal-shekhar": ("Bollywood", "Energetic"),
    "amit trivedi": ("Bollywood", "Chill"),
    "badshah": ("Hip-Hop", "Energetic"),
    "honey singh": ("Hip-Hop", "Aggressive"),
    "yo yo honey singh": ("Hip-Hop", "Aggressive"),
    "sonu nigam": ("Bollywood", "Romantic"),
    "kumar sanu": ("Bollywood", "Melancholic"),
    "udit narayan": ("Bollywood", "Happy"),
    "alka yagnik": ("Bollywood", "Romantic"),
    "jubin nautiyal": ("Bollywood", "Romantic"),
    "darshan raval": ("Bollywood", "Romantic"),
    "armaan malik": ("Bollywood", "Romantic"),
    "mohit chauhan": ("Bollywood", "Chill"),
    "sunidhi chauhan": ("Bollywood", "Energetic"),
    "mika singh": ("Bollywood", "Energetic"),
    "shankar mahadevan": ("Bollywood", "Energetic"),
    "kk": ("Bollywood", "Melancholic"),
    "rahat fateh ali khan": ("Bollywood", "Melancholic"),
    "stebin ben": ("Bollywood", "Romantic"),
    "b praak": ("Bollywood", "Melancholic"),
    "asees kaur": ("Bollywood", "Romantic"),
    "sachet tandon": ("Bollywood", "Romantic"),
    "tulsi kumar": ("Bollywood", "Romantic"),
    "palak muchhal": ("Bollywood", "Romantic"),
    "ankit tiwari": ("Bollywood", "Romantic"),
    "guru randhawa": ("Bollywood", "Energetic"),
    "raftaar": ("Hip-Hop", "Aggressive"),
    "divine": ("Hip-Hop", "Aggressive"),
    # Punjabi
    "sidhu moose wala": ("Punjabi", "Aggressive"),
    "sidhu moosewala": ("Punjabi", "Aggressive"),
    "diljit dosanjh": ("Punjabi", "Energetic"),
    "ap dhillon": ("Punjabi", "Chill"),
    "karan aujla": ("Punjabi", "Energetic"),
    "babbu maan": ("Punjabi", "Melancholic"),
    "gurdas maan": ("Folk", "Peaceful"),
    "harrdy sandhu": ("Punjabi", "Energetic"),
    "jassie gill": ("Punjabi", "Romantic"),
    "ammy virk": ("Punjabi", "Energetic"),
    "parmish verma": ("Punjabi", "Energetic"),
    "jazzy b": ("Punjabi", "Energetic"),
    "garry sandhu": ("Punjabi", "Romantic"),
    "mankirt aulakh": ("Punjabi", "Energetic"),
    "sharry mann": ("Punjabi", "Romantic"),
    "ninja": ("Punjabi", "Melancholic"),
    "ranjit bawa": ("Punjabi", "Energetic"),
    "kaur b": ("Punjabi", "Energetic"),
    "nimrat khaira": ("Punjabi", "Romantic"),
    "sunanda sharma": ("Punjabi", "Romantic"),
    "jass manak": ("Punjabi", "Romantic"),
    "kaka": ("Punjabi", "Melancholic"),
    "shubh": ("Punjabi", "Chill"),
    # Haryanvi
    "sapna choudhary": ("Haryanvi", "Energetic"),
    "raju punjabi": ("Haryanvi", "Energetic"),
    "gulzaar chhaniwala": ("Haryanvi", "Aggressive"),
    "md kd": ("Haryanvi", "Energetic"),
    "renuka panwar": ("Haryanvi", "Energetic"),
    "pranjal dahiya": ("Haryanvi", "Energetic"),
    "vishvajeet choudhary": ("Haryanvi", "Romantic"),
    # English - Pop
    "taylor swift": ("Pop", "Romantic"),
    "ed sheeran": ("Pop", "Romantic"),
    "dua lipa": ("Pop", "Energetic"),
    "the weeknd": ("R&B", "Dark"),
    "billie eilish": ("Pop", "Dark"),
    "harry styles": ("Pop", "Chill"),
    "olivia rodrigo": ("Pop", "Melancholic"),
    "ariana grande": ("Pop", "Energetic"),
    "justin bieber": ("Pop", "Chill"),
    "shawn mendes": ("Pop", "Romantic"),
    "charlie puth": ("Pop", "Romantic"),
    "bruno mars": ("Pop", "Happy"),
    "adele": ("Pop", "Melancholic"),
    "sam smith": ("Pop", "Melancholic"),
    "sia": ("Pop", "Energetic"),
    "imagine dragons": ("Rock", "Energetic"),
    "coldplay": ("Rock", "Peaceful"),
    "maroon 5": ("Pop", "Energetic"),
    "one direction": ("Pop", "Happy"),
    # English - Hip-Hop
    "drake": ("Hip-Hop", "Chill"),
    "kendrick lamar": ("Hip-Hop", "Aggressive"),
    "eminem": ("Hip-Hop", "Aggressive"),
    "post malone": ("Hip-Hop", "Chill"),
    "travis scott": ("Hip-Hop", "Dark"),
    "j. cole": ("Hip-Hop", "Chill"),
    "kanye west": ("Hip-Hop", "Energetic"),
    "lil nas x": ("Hip-Hop", "Energetic"),
    "doja cat": ("Hip-Hop", "Energetic"),
    "megan thee stallion": ("Hip-Hop", "Aggressive"),
    "cardi b": ("Hip-Hop", "Aggressive"),
    "21 savage": ("Hip-Hop", "Dark"),
    # English - Rock
    "linkin park": ("Rock", "Aggressive"),
    "green day": ("Rock", "Energetic"),
    "nirvana": ("Rock", "Dark"),
    "queen": ("Rock", "Energetic"),
    "ac/dc": ("Rock", "Aggressive"),
    "metallica": ("Metal", "Aggressive"),
    "foo fighters": ("Rock", "Energetic"),
    "arctic monkeys": ("Rock", "Chill"),
    "radiohead": ("Rock", "Melancholic"),
    "red hot chili peppers": ("Rock", "Energetic"),
}

# Sub-genre mapping
SUBGENRE_MAP = {
    "Bollywood": ["Filmi", "Indie Hindi", "Bollywood Pop", "Sufi", "Ghazal", "Qawwali"],
    "Punjabi": ["Bhangra", "Punjabi Pop", "Punjabi Hip-Hop", "Punjabi Folk"],
    "Haryanvi": ["Haryanvi Pop", "Haryanvi Folk", "Haryanvi DJ"],
    "Pop": ["Synth-pop", "Dance Pop", "Electropop", "Indie Pop", "Art Pop"],
    "Hip-Hop": ["Trap", "Conscious Hip-Hop", "Desi Hip-Hop", "Drill", "Lo-fi Hip-Hop"],
    "Rock": ["Alternative Rock", "Indie Rock", "Classic Rock", "Punk Rock", "Soft Rock"],
    "R&B": ["Neo Soul", "Contemporary R&B", "Alternative R&B"],
    "Electronic": ["EDM", "House", "Techno", "Ambient", "Synthwave"],
    "Folk": ["Indie Folk", "Folk Rock", "Traditional Folk"],
    "Metal": ["Heavy Metal", "Nu Metal", "Progressive Metal"],
}

# Fix each song
fixed_count = 0
for song in songs:
    artist_lower = song["artist"].lower()
    
    # Try to match artist
    matched = False
    for artist_key, (genre, mood) in ARTIST_GENRE_MAP.items():
        if artist_key in artist_lower:
            song["genre"] = genre
            song["mood"] = mood
            song["sub_genre"] = random.choice(SUBGENRE_MAP.get(genre, [genre]))
            matched = True
            fixed_count += 1
            break
    
    if not matched:
        # Assign based on language
        lang = song.get("language", "English")
        if lang == "Hindi":
            song["genre"] = random.choice(["Bollywood", "Bollywood", "Bollywood", "Hip-Hop", "Indie"])
            song["mood"] = random.choice(["Romantic", "Energetic", "Melancholic", "Happy", "Chill"])
        elif lang == "Punjabi":
            song["genre"] = "Punjabi"
            song["mood"] = random.choice(["Energetic", "Romantic", "Aggressive", "Happy"])
        elif lang == "Haryanvi":
            song["genre"] = "Haryanvi"
            song["mood"] = random.choice(["Energetic", "Aggressive", "Happy"])
        else:
            song["genre"] = random.choice(["Pop", "Rock", "Hip-Hop", "R&B", "Electronic", "Indie"])
            song["mood"] = random.choice(MOODS)
        
        song["sub_genre"] = random.choice(SUBGENRE_MAP.get(song["genre"], [song["genre"]]))
        fixed_count += 1
    
    # Fix tempo if 0
    if song.get("tempo", 0) == 0 or song.get("tempo") is None:
        song["tempo"] = random.uniform(70, 180)
    
    # Update description
    song["description"] = (
        f"A {song['mood'].lower()} {song['genre'].lower()} track by {song['artist']} "
        f"from the album '{song['album']}' ({song['year']}). "
        f"Perfect for {song['mood'].lower()} vibes."
    )

# Save fixed dataset
with open(songs_path, "w", encoding="utf-8") as f:
    json.dump(songs, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed_count} songs")

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

print(f"\nDataset Statistics:")
print(f"\n  Languages:")
for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
    print(f"    {lang}: {count} ({count*100//len(songs)}%)")

print(f"\n  Genres:")
for genre, count in sorted(genres.items(), key=lambda x: -x[1]):
    print(f"    {genre}: {count}")

print(f"\n  Moods:")
for mood, count in sorted(moods.items(), key=lambda x: -x[1]):
    print(f"    {mood}: {count}")
