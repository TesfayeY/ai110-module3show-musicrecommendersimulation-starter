from src.recommender import Song, UserProfile, Recommender, SCORING_MODES, load_songs, score_song, recommend_songs

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_load_songs_converts_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 18
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], float)


def test_score_song_rewards_matches_and_close_energy():
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    score, reasons = score_song(user_prefs, song)

    assert score == 4.0
    assert "genre match (+2.0)" in reasons
    assert "mood match (+1.0)" in reasons


def test_score_song_energy_closer_scores_higher():
    user_prefs = {"energy": 0.5}
    close, _ = score_song(user_prefs, {"genre": "x", "mood": "x", "energy": 0.55, "acousticness": 0.5})
    far, _ = score_song(user_prefs, {"genre": "x", "mood": "x", "energy": 0.95, "acousticness": 0.5})
    assert close > far


def test_recommend_songs_returns_top_k_sorted():
    songs = load_songs("data/songs.csv")
    results = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.35}, songs, k=3)

    assert len(results) == 3
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0][0]["genre"] == "lofi"


def test_load_songs_parses_advanced_features():
    song = load_songs("data/songs.csv")[0]
    assert isinstance(song["popularity"], int)
    assert isinstance(song["release_decade"], int)
    assert isinstance(song["instrumentalness"], float)
    assert song["mood_tags"] == ["euphoric", "sunny", "carefree"]


def test_score_song_advanced_preferences_add_points():
    song = load_songs("data/songs.csv")[7]  # Night Drive Loop, 1980s, nostalgic|nocturnal|driving
    basic, _ = score_song({"energy": 0.75}, song)
    advanced, reasons = score_song({"energy": 0.75, "decade": 1980, "mood_tags": ["nostalgic", "driving"]}, song)

    assert advanced == basic + 0.5 + 0.5
    assert "1980s release (+0.50)" in reasons


def test_scoring_modes_change_rankings():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    genre_first = [s["title"] for s, _, _ in recommend_songs(prefs, songs, 3, SCORING_MODES["genre-first"])]
    mood_first = [s["title"] for s, _, _ in recommend_songs(prefs, songs, 3, SCORING_MODES["mood-first"])]

    assert genre_first[1] == "Gym Hero"  # pop but intense
    assert mood_first[1] == "Rooftop Lights"  # happy but indie pop


def test_diversity_penalty_limits_repeat_artists():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}
    plain = recommend_songs(prefs, songs, 5)
    diverse = recommend_songs(prefs, songs, 5, diverse=True)

    assert sum(s["artist"] == "LoRoom" for s, _, _ in plain) == 2
    assert sum(s["artist"] == "LoRoom" for s, _, _ in diverse) == 1
    assert "diversity penalty" in diverse[1][2]
