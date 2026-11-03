import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict, field

# Algorithm Recipe: points awarded by score_song
DEFAULT_WEIGHTS = {
    "genre": 2.0,
    "mood": 1.0,
    "energy": 1.0,
    "acoustic": 0.5,
    # Advanced features: only scored when the user sets the matching preference
    "decade": 0.5,
    "mood_tag": 0.25,  # per shared tag, up to MAX_TAG_MATCHES
    "popularity": 0.5,
    "instrumental": 0.5,
    "liveness": 0.25,
}

MAX_TAG_MATCHES = 3

# Points subtracted per song already picked with the same artist / genre
DIVERSITY_PENALTY = {
    "artist": 1.0,
    "genre": 0.5,
}

INT_FIELDS = ("id", "popularity", "release_decade")
FLOAT_FIELDS = ("energy", "tempo_bpm", "valence", "danceability", "acousticness", "instrumentalness", "liveness")
LIST_FIELDS = ("mood_tags",)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2020
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    liveness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Convert the profile into the user_prefs dict used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
        }

@dataclass(frozen=True)
class ScoringMode:
    """A ranking strategy: a named set of weights that knows how to score a song."""
    name: str
    description: str
    weights: Dict[str, float]

    def score(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score one song using this mode's weights."""
        return score_song(user_prefs, song, self.weights)

SCORING_MODES = {
    mode.name: mode
    for mode in (
        ScoringMode("balanced", "genre first, then mood, then energy", DEFAULT_WEIGHTS),
        ScoringMode("genre-first", "genre outweighs everything", {**DEFAULT_WEIGHTS, "genre": 3.0, "mood": 0.5, "energy": 0.5}),
        ScoringMode("mood-first", "mood outweighs genre", {**DEFAULT_WEIGHTS, "genre": 0.5, "mood": 2.0}),
        ScoringMode("energy-focused", "energy x2, genre x1/2 (the Phase 4 experiment)", {**DEFAULT_WEIGHTS, "genre": 1.0, "energy": 2.0}),
    )
}

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for the user, highest score first."""
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(user.to_prefs(), asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation of how a song was scored for the user."""
        score, reasons = score_song(user.to_prefs(), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs from a CSV file into dicts with numeric and list fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for name in INT_FIELDS:
                if name in row:
                    row[name] = int(row[name])
            for name in FLOAT_FIELDS:
                if name in row:
                    row[name] = float(row[name])
            for name in LIST_FIELDS:
                if name in row:
                    row[name] = [tag for tag in row[name].split("|") if tag]
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict] = None) -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons)."""
    weights = weights or DEFAULT_WEIGHTS
    score = 0.0
    reasons = []

    genre = user_prefs.get("genre")
    if genre and song["genre"].lower() == genre.lower():
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.1f})")

    mood = user_prefs.get("mood")
    if mood and song["mood"].lower() == mood.lower():
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.1f})")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        # Closer to the target earns more; a gap of 1.0 earns nothing
        gap = abs(song["energy"] - target_energy)
        points = weights["energy"] * (1.0 - gap)
        score += points
        reasons.append(f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{points:.2f})")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1.0 - song["acousticness"]
        points = weights["acoustic"] * fit
        score += points
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"{label} preference (+{points:.2f})")

    decade = user_prefs.get("decade")
    if decade is not None and "release_decade" in song:
        # Exact decade earns full points, a neighboring decade earns half
        decades_off = abs(song["release_decade"] - decade) // 10
        if decades_off <= 1:
            points = weights["decade"] * (1.0 if decades_off == 0 else 0.5)
            score += points
            reasons.append(f"{song['release_decade']}s release (+{points:.2f})")

    wanted_tags = user_prefs.get("mood_tags")
    if wanted_tags and "mood_tags" in song:
        shared = [tag for tag in song["mood_tags"] if tag in wanted_tags][:MAX_TAG_MATCHES]
        if shared:
            points = weights["mood_tag"] * len(shared)
            score += points
            reasons.append(f"mood tags {', '.join(shared)} (+{points:.2f})")

    target_popularity = user_prefs.get("popularity")
    if target_popularity is not None and "popularity" in song:
        # Same closeness rule as energy, on a 0-100 scale
        gap = abs(song["popularity"] - target_popularity) / 100
        points = weights["popularity"] * (1.0 - gap)
        score += points
        reasons.append(f"popularity {song['popularity']} vs target {target_popularity} (+{points:.2f})")

    wants_instrumental = user_prefs.get("instrumental")
    if wants_instrumental is not None and "instrumentalness" in song:
        fit = song["instrumentalness"] if wants_instrumental else 1.0 - song["instrumentalness"]
        points = weights["instrumental"] * fit
        score += points
        label = "instrumental" if wants_instrumental else "vocals"
        reasons.append(f"{label} preference (+{points:.2f})")

    likes_live = user_prefs.get("likes_live")
    if likes_live is not None and "liveness" in song:
        fit = song["liveness"] if likes_live else 1.0 - song["liveness"]
        points = weights["liveness"] * fit
        score += points
        label = "live sound" if likes_live else "studio sound"
        reasons.append(f"{label} preference (+{points:.2f})")

    return score, reasons

def diversify(ranked: List[Tuple[Dict, float, List[str]]], k: int) -> List[Tuple[Dict, float, List[str]]]:
    """Greedily pick k songs, penalizing artists and genres already in the picks."""
    remaining = list(ranked)
    picked = []
    while remaining and len(picked) < k:
        best = None
        for candidate in remaining:
            song, score, reasons = candidate
            same_artist = sum(p[0]["artist"] == song["artist"] for p in picked)
            same_genre = sum(p[0]["genre"] == song["genre"] for p in picked)
            penalty = DIVERSITY_PENALTY["artist"] * same_artist + DIVERSITY_PENALTY["genre"] * same_genre
            if best is None or score - penalty > best[1]:
                best = (candidate, score - penalty, penalty, same_artist, same_genre)
        candidate, adjusted, penalty, same_artist, same_genre = best
        song, _, reasons = candidate
        if penalty:
            repeats = []
            if same_artist:
                repeats.append(f"artist x{same_artist}")
            if same_genre:
                repeats.append(f"genre x{same_genre}")
            reasons = reasons + [f"diversity penalty: {', '.join(repeats)} already picked (-{penalty:.2f})"]
        picked.append((song, adjusted, reasons))
        remaining.remove(candidate)
    return picked

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: Optional[ScoringMode] = None, diverse: bool = False) -> List[Tuple[Dict, float, str]]:
    """Score every song with a mode and return the top k as (song, score, explanation), highest first."""
    mode = mode or SCORING_MODES["balanced"]
    scored = []
    for song in songs:
        score, reasons = mode.score(user_prefs, song)
        scored.append((song, score, reasons))
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    top = diversify(ranked, k) if diverse else ranked[:k]
    return [(song, score, "; ".join(reasons)) for song, score, reasons in top]
