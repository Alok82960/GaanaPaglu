"""GaanaPaglu - Production-Ready Music Recommendation UI."""

import streamlit as st
import streamlit.components.v1 as components
import requests
from typing import Optional, Dict

# --- Config ---
import os
API = os.environ.get("API_URL", "https://gaanapaglu.onrender.com")
st.set_page_config(page_title="GaanaPaglu", page_icon="🎵", layout="wide", initial_sidebar_state="expanded")

# --- Session ---
defaults = {"token": None, "username": None, "page": "home", "now_playing": None, "np_title": "", "np_artist": "", "sel_mood": None}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Professional CSS ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*{font-family:'Inter',sans-serif}
.stApp{background:linear-gradient(180deg,#0d1117 0%,#010409 100%)}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1117 0%,#000 100%);border-right:1px solid rgba(255,255,255,0.05)}
.block-container{padding:1.5rem 2rem}

/* Typography */
h1,h2,h3{color:#e6edf3!important;font-weight:600!important;letter-spacing:-0.02em}
p,.stMarkdown{color:#8b949e}

/* Inputs */
.stTextInput input{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.1)!important;color:#e6edf3!important;border-radius:12px!important;padding:12px 16px!important;font-size:0.9em!important;transition:border .2s}
.stTextInput input:focus{border-color:#1DB954!important;box-shadow:0 0 0 2px rgba(29,185,84,0.15)!important}

/* Buttons */
.stButton>button{background:linear-gradient(135deg,#1DB954,#1aa34a)!important;color:#fff!important;border:none!important;border-radius:24px!important;font-weight:600!important;padding:8px 24px!important;font-size:0.85em!important;transition:all .2s!important;box-shadow:0 4px 12px rgba(29,185,84,0.3)!important}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(29,185,84,0.4)!important}

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,0.05)!important;color:#e6edf3!important;box-shadow:none!important;border-radius:8px!important;text-align:left!important;justify-content:flex-start!important}
[data-testid="stSidebar"] .stButton>button:hover{background:rgba(29,185,84,0.15)!important;color:#1DB954!important}

/* Select */
.stSelectbox>div>div{background:rgba(255,255,255,0.05)!important;color:#e6edf3!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:8px!important}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{background:transparent;border-bottom:1px solid rgba(255,255,255,0.05)}
.stTabs [data-baseweb="tab"]{color:#8b949e;background:transparent;font-weight:500}
.stTabs [aria-selected="true"]{color:#1DB954!important;border-bottom:2px solid #1DB954!important}

/* Metrics */
.stMetric{background:rgba(255,255,255,0.03);border-radius:16px;padding:20px;border:1px solid rgba(255,255,255,0.06)}
.stMetric label{color:#8b949e!important;font-size:0.8em!important}
.stMetric [data-testid="stMetricValue"]{color:#1DB954!important;font-weight:700!important}

/* Multiselect */
.stMultiSelect>div>div{background:rgba(255,255,255,0.05)!important;border:1px solid rgba(255,255,255,0.1)!important;border-radius:8px!important}

/* Custom Components */
.hero-card{background:linear-gradient(135deg,#1DB954 0%,#0d4020 50%,#0d1117 100%);border-radius:20px;padding:40px 36px;margin-bottom:28px;position:relative;overflow:hidden}
.hero-card::before{content:'';position:absolute;top:-50%;right:-20%;width:300px;height:300px;background:radial-gradient(circle,rgba(29,185,84,0.3),transparent);border-radius:50%}
.hero-card h1{color:#fff!important;font-size:2.2em!important;margin:0!important;position:relative;z-index:1}
.hero-card p{color:rgba(255,255,255,0.8)!important;margin:8px 0 0!important;font-size:1em;position:relative;z-index:1}

.song-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:14px 18px;margin:8px 0;transition:all .2s}
.song-card:hover{background:rgba(29,185,84,0.05);border-color:rgba(29,185,84,0.2);transform:translateX(2px)}
.song-title{color:#e6edf3;font-size:0.92em;font-weight:500}
.song-artist{color:#8b949e;font-size:0.8em;margin-top:2px}
.song-badge{background:linear-gradient(135deg,#1DB954,#1aa34a);color:#fff;padding:3px 10px;border-radius:12px;font-size:0.7em;font-weight:700;display:inline-block}
.song-tag{background:rgba(255,255,255,0.06);color:#8b949e;padding:3px 8px;border-radius:8px;font-size:0.68em;display:inline-block;margin:0 2px}
.song-explain{color:#6e7681;font-size:0.78em;font-style:italic;margin-top:6px;padding:8px 12px;background:rgba(29,185,84,0.05);border-left:2px solid #1DB954;border-radius:0 6px 6px 0}

.mood-card{border-radius:14px;padding:24px 16px;text-align:center;min-height:100px;display:flex;flex-direction:column;align-items:center;justify-content:center;transition:all .25s;border:1px solid rgba(255,255,255,0.06);cursor:pointer}
.mood-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.4)}
.mood-emoji{font-size:1.8em;margin-bottom:6px}
.mood-label{color:#e6edf3;font-weight:500;font-size:0.85em}

.np-container{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:12px 16px;margin-top:20px}
.np-text{color:#e6edf3;font-size:0.85em;margin-bottom:8px}
.np-text span{color:#1DB954;font-weight:600}

.login-container{max-width:420px;margin:0 auto;padding:20px}
.brand-text{text-align:center;margin-bottom:32px}
.brand-text h1{font-size:2.5em!important;margin:0!important}
.brand-text p{color:#8b949e;font-size:1em}
.green{color:#1DB954}

.section-title{color:#e6edf3;font-size:1.3em;font-weight:600;margin:24px 0 12px;letter-spacing:-0.01em}
.section-desc{color:#8b949e;font-size:0.85em;margin-bottom:16px}
</style>""", unsafe_allow_html=True)


# --- API ---
def api(method, endpoint, data=None, auth=True):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if auth and st.session_state.token else {}
    try:
        r = getattr(requests, method.lower())(f"{API}{endpoint}", json=data, headers=headers, timeout=15)
        return r.json() if r.status_code in (200, 201) else None
    except:
        return None


# --- Song Card ---
def song_card(song, idx):
    sid = song.get("song_id", "")
    dur = f"{song.get('duration_ms',0)//60000}:{(song.get('duration_ms',0)%60000)//1000:02d}"
    score = song.get("match_score", 0)

    st.markdown(f"""<div class="song-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
            <div style="flex:1;min-width:200px">
                <div class="song-title">{song.get('title','Unknown')}</div>
                <div class="song-artist">{song.get('artist','Unknown')} · {song.get('album','')}</div>
            </div>
            <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
                <span class="song-badge">{score:.0f}% match</span>
                <span class="song-tag">{song.get('genre','')}</span>
                <span class="song-tag">{song.get('mood','')}</span>
                <span class="song-tag">{song.get('language','')}</span>
                <span class="song-tag">⏱ {dur}</span>
            </div>
        </div>
        <div class="song-explain">💡 {song.get('explanation','')}</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3, _ = st.columns([1.3, 0.7, 0.7, 8])
    with c1:
        if st.button("▶ Play", key=f"p{idx}{sid}"):
            st.session_state.now_playing = sid
            st.session_state.np_title = song.get("title", "")
            st.session_state.np_artist = song.get("artist", "")
    with c2:
        if st.button("♥", key=f"l{idx}{sid}"):
            api("POST", "/user/like", {"song_id": sid, "song_title": song.get("title",""), "song_artist": song.get("artist","")})
            st.toast("❤️ Added to Liked Songs")
    with c3:
        if st.button("✕", key=f"d{idx}{sid}"):
            api("POST", "/user/dislike", {"song_id": sid, "song_title": song.get("title",""), "song_artist": song.get("artist","")})
            st.toast("Removed")


# --- Pages ---
def page_login():
    _, col, _ = st.columns([1.2, 2, 1.2])
    with col:
        st.markdown("""<div class="brand-text">
            <h1>🎵 <span class="green">Gaana</span>Paglu</h1>
            <p>Discover music you'll love with AI-powered recommendations</p>
        </div>""", unsafe_allow_html=True)

        t1, t2 = st.tabs(["Log In", "Create Account"])
        with t1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Continue", use_container_width=True):
                    r = api("POST", "/auth/login", {"username": u, "password": p}, False)
                    if r:
                        st.session_state.token = r["access_token"]
                        st.session_state.username = u
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        with t2:
            with st.form("reg"):
                u = st.text_input("Username", key="ru")
                e = st.text_input("Email", key="re")
                n = st.text_input("Full Name", key="rn")
                p = st.text_input("Password (min 8 chars)", type="password", key="rp")
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if len(p) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        r = api("POST", "/auth/register", {"username": u, "email": e, "password": p, "full_name": n}, False)
                        if r:
                            st.success("✅ Account created! Switch to Log In tab.")
                        else:
                            st.error("Username or email already taken")


def page_home():
    st.markdown(f"""<div class="hero-card">
        <h1>Good to see you, {st.session_state.username} 👋</h1>
        <p>Discover new music tailored just for you</p>
    </div>""", unsafe_allow_html=True)

    # Quick mood access
    st.markdown('<div class="section-title">Quick Mood Mix</div>', unsafe_allow_html=True)
    moods_data = [("🔥","Energetic","#e91e63"),("😌","Chill","#00bcd4"),("💕","Romantic","#ff5252"),("😊","Happy","#ffc107"),("🌙","Dark","#7c4dff")]
    cols = st.columns(5)
    for i,(emoji,mood,color) in enumerate(moods_data):
        with cols[i]:
            st.markdown(f'<div class="mood-card" style="background:linear-gradient(135deg,{color}22,{color}08)"><div class="mood-emoji">{emoji}</div><div class="mood-label">{mood}</div></div>', unsafe_allow_html=True)
            if st.button(f"{mood}", key=f"qm_{mood}", use_container_width=True):
                st.session_state.page = "mood"
                st.session_state.sel_mood = mood
                st.rerun()

    # Personalized
    st.markdown('<div class="section-title">🎯 Made For You</div>', unsafe_allow_html=True)
    r = api("GET", "/recommend/personalized")
    if r and r.get("recommendations"):
        st.markdown(f'<div class="section-desc">{r.get("ai_summary","")}</div>', unsafe_allow_html=True)
        for i, s in enumerate(r["recommendations"][:8], 1):
            song_card(s, i)
    else:
        st.info("🎵 Start by searching for music or setting your preferences. The more you interact, the better recommendations get!")


def page_search():
    st.markdown('<div class="section-title">🔍 Search Music</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Tell me what you\'re in the mood for — I\'ll find the perfect songs</div>', unsafe_allow_html=True)

    q = st.text_input("", placeholder="Try: 'chill bollywood for studying', 'punjabi party songs', 'sad romantic hindi'...", label_visibility="collapsed")
    c1, c2 = st.columns([5, 1])
    with c2:
        n = st.selectbox("", [5, 10, 15, 20], index=1, label_visibility="collapsed")

    if st.button("✨ Find Music", use_container_width=True):
        if q:
            with st.spinner("🎵 Searching..."):
                r = api("POST", "/recommend/query", {"query": q, "num_results": n})
            if r and r.get("recommendations"):
                st.markdown(f'<div class="section-desc">💡 {r.get("ai_summary","")}</div>', unsafe_allow_html=True)
                for i, s in enumerate(r["recommendations"], 1):
                    song_card(s, 100+i)
            else:
                st.warning("No results. Try different keywords!")
        else:
            st.warning("Type something to search")


def page_similar():
    st.markdown('<div class="section-title">🎶 Find Similar Songs</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Enter a song you love and discover similar tracks</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        title = st.text_input("Song Title", placeholder="e.g. Tum Hi Ho, Blinding Lights")
    with c2:
        artist = st.text_input("Artist (optional)", placeholder="e.g. Arijit Singh")

    if st.button("🔍 Find Similar", use_container_width=True):
        if title:
            with st.spinner("Searching..."):
                r = api("POST", "/recommend/similar", {"song_title": title, "artist": artist or None, "num_results": 10})
            if r and r.get("recommendations"):
                st.markdown(f'<div class="section-desc">💡 {r.get("ai_summary","")}</div>', unsafe_allow_html=True)
                for i, s in enumerate(r["recommendations"], 1):
                    song_card(s, 200+i)


def page_mood():
    st.markdown('<div class="section-title">🎭 Mood Playlists</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Select a mood and get an instant playlist</div>', unsafe_allow_html=True)

    moods = [("🔥","Energetic","#e91e63"),("😌","Chill","#00bcd4"),("😢","Melancholic","#7c4dff"),("💕","Romantic","#ff5252"),
             ("🌙","Dark","#424242"),("😊","Happy","#ffc107"),("💪","Aggressive","#ff3d00"),("🧘","Peaceful","#4caf50")]

    cols = st.columns(4)
    for i,(emoji,mood,color) in enumerate(moods):
        with cols[i%4]:
            st.markdown(f'<div class="mood-card" style="background:linear-gradient(135deg,{color}22,{color}08);border-color:{color}33"><div class="mood-emoji">{emoji}</div><div class="mood-label">{mood}</div></div>', unsafe_allow_html=True)
            if st.button(mood, key=f"mood_{mood}", use_container_width=True):
                st.session_state.sel_mood = mood

    if st.session_state.sel_mood:
        with st.spinner(f"Creating {st.session_state.sel_mood} playlist..."):
            r = api("POST", "/recommend/mood", {"mood": st.session_state.sel_mood, "num_results": 10})
        if r and r.get("recommendations"):
            st.markdown(f'<div class="section-title">{st.session_state.sel_mood} Playlist</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-desc">💡 {r.get("ai_summary","")}</div>', unsafe_allow_html=True)
            for i, s in enumerate(r["recommendations"], 1):
                song_card(s, 300+i)


def page_prefs():
    st.markdown('<div class="section-title">⚙️ Your Preferences</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Help us understand your taste for better recommendations</div>', unsafe_allow_html=True)

    with st.form("prefs"):
        g = st.multiselect("Favorite Genres", ["Bollywood","Pop","Hip-Hop","Rock","R&B","Electronic","Punjabi","Haryanvi","Indie","Folk","Classical"])
        m = st.multiselect("Preferred Moods", ["Energetic","Chill","Melancholic","Romantic","Happy","Peaceful","Dark"])
        l = st.multiselect("Languages", ["Hindi","English","Punjabi","Haryanvi"])
        a = st.text_input("Favorite Artists", placeholder="e.g. Arijit Singh, Diljit Dosanjh, The Weeknd")
        if st.form_submit_button("💾 Save Preferences", use_container_width=True):
            api("PUT", "/user/preferences", {
                "favorite_genres": g, "favorite_moods": m, "preferred_languages": l,
                "favorite_artists": [x.strip() for x in a.split(",") if x.strip()]
            })
            st.success("✅ Preferences saved! Your recommendations will improve.")


def page_history():
    st.markdown('<div class="section-title">📜 Your Activity</div>', unsafe_allow_html=True)
    r = api("GET", "/user/history")
    if r:
        c1, c2, c3 = st.columns(3)
        c1.metric("❤️ Liked Songs", r.get("total_likes", 0))
        c2.metric("👎 Disliked", r.get("total_dislikes", 0))
        c3.metric("🔍 Searches", r.get("total_queries", 0))

        if r.get("likes"):
            st.markdown('<div class="section-title" style="font-size:1.1em">❤️ Liked Songs</div>', unsafe_allow_html=True)
            for like in r["likes"][:20]:
                st.markdown(f'<div class="song-card" style="padding:10px 14px"><span class="song-title">{like["song_title"]}</span> <span class="song-artist">— {like["song_artist"]}</span></div>', unsafe_allow_html=True)
    else:
        st.info("No activity yet. Start exploring music!")


# --- Sidebar ---
def sidebar():
    with st.sidebar:
        st.markdown("""<div style="padding:8px 0 16px">
            <h2 style="margin:0;font-size:1.4em">🎵 <span class="green">Gaana</span>Paglu</h2>
            <p style="font-size:0.75em;margin:4px 0 0;color:#6e7681">AI Music Recommendations</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        nav = [("🏠 Home","home"),("🔍 Search","search"),("🎶 Similar Songs","similar"),
               ("🎭 Mood Playlists","mood"),("⚙️ Preferences","prefs"),("📜 History","history")]
        for label, key in nav:
            if st.button(label, use_container_width=True, key=f"n_{key}"):
                st.session_state.page = key
                st.session_state.sel_mood = None
                st.rerun()

        st.markdown("---")
        st.markdown(f'<p style="font-size:0.8em;color:#6e7681">👤 Logged in as <strong style="color:#e6edf3">{st.session_state.username}</strong></p>', unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()


# --- Now Playing ---
def now_playing():
    if st.session_state.now_playing:
        st.markdown(f"""<div class="np-container">
            <div class="np-text">🎵 Now Playing: <span>{st.session_state.np_title}</span> — {st.session_state.np_artist}</div>
        </div>""", unsafe_allow_html=True)
        components.iframe(
            f"https://open.spotify.com/embed/track/{st.session_state.now_playing}?utm_source=generator&theme=0",
            height=80, scrolling=False
        )


# --- Main ---
def main():
    if not st.session_state.token:
        page_login()
    else:
        sidebar()
        pages = {"home": page_home, "search": page_search, "similar": page_similar,
                 "mood": page_mood, "prefs": page_prefs, "history": page_history}
        pages.get(st.session_state.page, page_home)()
        now_playing()

if __name__ == "__main__":
    main()
