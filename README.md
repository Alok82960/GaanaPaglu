# 🎵 GaanaPaglu - AI-Powered Music Recommendation System

An intelligent music recommendation system that uses **GPT-Neo 1.3B** for natural language generation and **Sentence Transformers** for semantic similarity search. Built with FastAPI, Streamlit, and real Spotify data.

## ✨ Features

- **Natural Language Search** — "I want chill Hindi songs for a late night drive"
- **Similar Song Finder** — Find tracks similar to your favorites
- **Mood-Based Playlists** — Generate playlists by mood (Energetic, Chill, Romantic, etc.)
- **Preference-Based** — Get recommendations based on your genre/artist/mood preferences
- **History-Aware** — System learns from your likes/dislikes over time
- **AI Explanations** — Every recommendation comes with a reason why it was picked

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI Backend
                           ↓
              Sentence Transformers (semantic search)
                           ↓
              GPT-Neo 1.3B (natural language generation)
                           ↓
              Personalized recommendations with explanations
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI |
| Frontend | Streamlit |
| LLM | GPT-Neo 1.3B (Hugging Face) |
| Embeddings | all-MiniLM-L6-v2 (Sentence Transformers) |
| Database | SQLite (async) |
| Auth | JWT + bcrypt |
| Data Source | Spotify Web API |
| Rate Limiting | SlowAPI |

## 📋 Prerequisites

- Python 3.11+
- GPU with 8GB+ VRAM (recommended) or CPU (slower)
- Spotify Developer Account (for data fetching)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd GaanaPaglu
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and fill in:
- `SPOTIFY_CLIENT_ID` — Your Spotify app Client ID
- `SPOTIFY_CLIENT_SECRET` — Your Spotify app Client Secret
- `SECRET_KEY` — A random string for JWT signing (use: `python -c "import secrets; print(secrets.token_hex(32))"`)

### 3. Fetch Song Data from Spotify

```bash
python data/fetch_spotify_data.py
```

This fetches ~5000 songs from Spotify across Hindi, English, Punjabi, and Haryanvi playlists.

### 4. Start the API Server

```bash
python run.py
```

API will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 5. Start the Frontend

Open a new terminal:

```bash
streamlit run frontend/app.py
```

Frontend will be available at: http://localhost:8501

## 🐳 Docker

```bash
docker-compose up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:8501

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/me` | Get profile |
| POST | `/recommend/query` | Natural language search |
| POST | `/recommend/similar` | Find similar songs |
| POST | `/recommend/mood` | Mood-based playlist |
| POST | `/recommend/preferences` | Preference-based |
| GET | `/recommend/personalized` | History-aware |
| POST | `/user/like` | Like a song |
| POST | `/user/dislike` | Dislike a song |
| PUT | `/user/preferences` | Update preferences |
| GET | `/user/history` | View history |

## 📊 Dataset

- **5000 songs** from Spotify
- **Languages:** Hindi, English, Punjabi, Haryanvi
- **Attributes:** Title, Artist, Album, Genre, Sub-genre, Year, Duration, Mood, BPM, Language, Popularity, Description
- **Time range:** All time

## 🔒 Security

- Passwords hashed with bcrypt
- JWT token authentication
- Rate limiting (30 requests/minute)
- Input validation with Pydantic
- CORS protection

## 📁 Project Structure

```
GaanaPaglu/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings
│   ├── auth/                # Authentication
│   ├── recommendations/     # AI recommendation engine
│   ├── user/                # User preferences & history
│   ├── database/            # SQLite models & connection
│   └── middleware/          # Rate limiting
├── data/
│   ├── fetch_spotify_data.py  # Spotify data fetcher
│   └── songs.json           # Generated dataset
├── frontend/
│   └── app.py               # Streamlit UI
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── run.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## 📄 License

MIT License - feel free to use this project for learning and personal use.

---

Built with ❤️ by GaanaPaglu Team
