"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main                       # balanced mode, all basic profiles
    python -m src.main --experiment          # shortcut for --mode energy-focused
    python -m src.main --mode mood-first     # balanced | genre-first | mood-first | energy-focused
    python -m src.main --diverse             # penalize repeated artists and genres
    python -m src.main --table               # ASCII table output
    python -m src.main --advanced            # profiles that use the advanced song features
"""

import argparse
import textwrap

from src.recommender import SCORING_MODES, load_songs, recommend_songs

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

# Profiles that use the Challenge 1 features (decade, mood tags, popularity, instrumental, liveness)
ADVANCED_PROFILES = {
    "Late-Night Study": {
        "genre": "lofi", "mood": "focused", "energy": 0.4,
        "mood_tags": ["calm", "nocturnal"], "instrumental": True, "likes_live": False,
    },
    "Throwback Road Trip": {
        "mood": "nostalgic", "energy": 0.6,
        "decade": 1980, "mood_tags": ["nostalgic", "driving", "warm"], "popularity": 60,
    },
    "Underground Headbanger": {
        "genre": "metal", "mood": "angry", "energy": 0.95,
        "mood_tags": ["aggressive", "rebellious"], "popularity": 30, "instrumental": False, "likes_live": True,
    },
}


def describe_profile(user_prefs: dict) -> str:
    """Format a user_prefs dict as a short one-line summary."""
    return ", ".join(f"{key}={value}" for key, value in user_prefs.items())


def print_list(recommendations: list) -> None:
    """Print recommendations as a numbered list with one reason per line."""
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']} ({song['genre']}, {song['mood']})")
        print(f"   Score: {score:.2f}")
        for reason in explanation.split("; "):
            print(f"   - {reason}")


def print_table(recommendations: list, reason_width: int = 46) -> None:
    """Print recommendations as an ASCII table, wrapping the reasons column."""
    headers = ["#", "Title", "Artist", "Genre / Mood", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reason_lines = []
        for reason in explanation.split("; "):
            reason_lines += textwrap.wrap(reason, reason_width, subsequent_indent="  ")
        rows.append([str(rank), song["title"], song["artist"], f"{song['genre']} / {song['mood']}", f"{score:.2f}", reason_lines])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row[:-1]):
            widths[i] = max(widths[i], len(cell))
    widths[-1] = max([len(headers[-1])] + [len(line) for row in rows for line in row[-1]])

    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def line(cells: list) -> str:
        return "| " + " | ".join(cell.ljust(w) for cell, w in zip(cells, widths)) + " |"

    print(border)
    print(line(headers))
    print(border.replace("-", "="))
    for row in rows:
        for i, reason in enumerate(row[-1]):
            print(line((row[:-1] if i == 0 else [""] * (len(row) - 1)) + [reason]))
        print(border)


def print_recommendations(name: str, user_prefs: dict, songs: list, mode, diverse: bool, table: bool, k: int = 5) -> None:
    """Print a ranked, explained list of recommendations for one profile."""
    print("=" * 60)
    print(f"Profile: {name}")
    print(f"Prefs:   {describe_profile(user_prefs)}")
    print("-" * 60)
    recommendations = recommend_songs(user_prefs, songs, k, mode, diverse)
    if table:
        print_table(recommendations)
    else:
        print_list(recommendations)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=SCORING_MODES, default="balanced", help="ranking strategy")
    parser.add_argument("--experiment", action="store_true", help="shortcut for --mode energy-focused")
    parser.add_argument("--diverse", action="store_true", help="penalize repeated artists and genres")
    parser.add_argument("--table", action="store_true", help="show results as an ASCII table")
    parser.add_argument("--advanced", action="store_true", help="use profiles with advanced song features")
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    mode = SCORING_MODES["energy-focused" if args.experiment else args.mode]
    print(f"Mode: {mode.name} ({mode.description})")
    print(f"Diversity penalty: {'on' if args.diverse else 'off'}\n")

    profiles = ADVANCED_PROFILES if args.advanced else PROFILES
    for name, user_prefs in profiles.items():
        print_recommendations(name, user_prefs, songs, mode, args.diverse, args.table)


if __name__ == "__main__":
    main()
