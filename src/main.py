"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main               # baseline weights
    python -m src.main --experiment  # energy weight doubled, genre weight halved
"""

import sys

from src.recommender import DEFAULT_WEIGHTS, load_songs, recommend_songs

# Weight Shift experiment from Phase 4: double energy, halve genre
EXPERIMENT_WEIGHTS = {**DEFAULT_WEIGHTS, "genre": 1.0, "energy": 2.0}

PROFILES = {
    "Default Pop/Happy": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Adversarial / edge cases
    "Conflicted (sad but high energy)": {"genre": "folk", "mood": "sad", "energy": 0.9},
    "Unknown Genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    "Mood Only (no genre)": {"mood": "chill", "energy": 0.5},
}


def describe_profile(user_prefs: dict) -> str:
    """Format a user_prefs dict as a short one-line summary."""
    return ", ".join(f"{key}={value}" for key, value in user_prefs.items())


def print_recommendations(name: str, user_prefs: dict, songs: list, weights: dict, k: int = 5) -> None:
    """Print a ranked, explained list of recommendations for one profile."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(f"Prefs:   {describe_profile(user_prefs)}")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k, weights), start=1):
        print(f"{rank}. {song['title']} by {song['artist']} ({song['genre']}, {song['mood']})")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    weights = EXPERIMENT_WEIGHTS if "--experiment" in sys.argv else DEFAULT_WEIGHTS
    print(f"Weights: {weights}\n")

    for name, user_prefs in PROFILES.items():
        print_recommendations(name, user_prefs, songs, weights)


if __name__ == "__main__":
    main()
