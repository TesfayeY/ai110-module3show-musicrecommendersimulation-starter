# AI Interactions Log

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (agent mode in the terminal) to work through Phases 1–5 of the project, starting at Phase 1 Step 2: analyze `songs.csv` for useful features, expand the dataset, design the scoring and ranking rules, implement `load_songs`, `score_song`, and `recommend_songs`, test multiple user profiles including adversarial ones, run a weight-shift experiment, and document everything in the README and model card.

**Prompts used:**

- "Starting from Phase 1 Step 2, complete these tasks" (with the full project instructions pasted in).
- The instructions' own prompts guided each step, for example: which `songs.csv` features work best for a content-based recommender; how to score a numerical feature so that being *closer* to the target is rewarded, rather than just being higher or lower; why a recommender needs both a Scoring Rule and a Ranking Rule; the most Pythonic way to score and rank every song; the difference between `.sort()` and `sorted()`; adversarial user profiles; and filter bubbles in the scoring logic.

**What did the agent generate or change?**

- `data/songs.csv`: added 8 songs in genres and moods the starter didn't have.
- `src/recommender.py`: implemented CSV loading with numeric conversion, the weighted `score_song` (returns a score and reasons), `recommend_songs`, and the `Recommender` class (which reuses `score_song`).
- `src/main.py`: seven profiles, formatted output with reasons, and a `--experiment` flag for the weight shift.
- `tests/test_recommender.py` and `pytest.ini`: four new tests, plus config so pytest can import `src`.
- `README.md` and `model_card.md`: design, sample output, experiments, evaluation, bias, and reflection.
- Commands: `python -m src.main`, `python -m src.main --experiment`, and `pytest`.

**Key explanations from the AI:**

- *Scoring vs. ranking:* the scoring rule judges one song in isolation, and the ranking rule compares all the scores to decide what to show and in what order. You need both, because a score alone doesn't say whether a song is in the top 5.
- *`.sort()` vs. `sorted()`:* `list.sort()` reorders the list in place and returns `None`. `sorted()` returns a new sorted list and leaves the original alone. I used `sorted()` so the loaded catalog keeps its CSV order. Both are stable, so songs with tied scores stay in catalog order.

**What did you verify or fix manually?**

- The starter `main.py` imported with `from recommender import ...`, which crashes under `python -m src.main`. I confirmed it failed and switched it to `from src.recommender import ...`.
- The starter tests couldn't import `src` when running plain `pytest`, which `pytest.ini` fixes.
- I checked scores by hand against the recipe (for example, Sunrise City for pop/happy/0.8 = 2.0 + 1.0 + 0.98 = 3.98) and checked that the experiment weights keep the maximum score at 4.5.
- I made sure all terminal output in the docs was pasted from real runs, not written from memory.

### Optional extensions (Challenges 1–4)

**Prompt:** "Commit my new updates and complete the optional ones." Each challenge's own instructions shaped the work, for example:

- Challenge 1: add 5+ attributes not in the baseline (popularity 0–100, release decade, detailed mood tags, and so on), and update both `songs.csv` and the scoring logic.
- Challenge 2: brainstorm a design pattern so users can switch between Genre-First, Mood-First, and Energy-Focused ranking while keeping the code modular.
- Challenge 3: "Penalize a song's score if its artist is already present in the top recommendations list." I extended this to genre too, with a smaller penalty.
- Challenge 4: a terminal table that must include the reasons for each score.

**What the agent changed:**

- `data/songs.csv`: five new columns (`popularity`, `release_decade`, `mood_tags`, `instrumentalness`, `liveness`) filled in for all 18 songs. Mood tags are separated by `|` so they don't break the CSV's commas.
- `src/recommender.py`: `load_songs` parses the new int, float, and list fields. `score_song` has five new optional scoring rules. It also adds `ScoringMode` with `SCORING_MODES`, plus `diversify()`, and `recommend_songs` now takes `mode` and `diverse`.
- `src/main.py`: argparse flags `--mode`, `--diverse`, `--table`, and `--advanced`, plus three advanced profiles and an ASCII table printer using `textwrap` (no new dependency). `--experiment` still works.
- `tests/test_recommender.py`: four new tests (10 total).

**Manual verification notes:**

- **No regressions:** I diffed the seven basic profiles' output, in both balanced and experiment mode, against the runs from before the change, and they were identical. This works because every new preference is optional, which keeps the README and model card output accurate.
- **Starter tests still construct `Song` with only 10 fields**, so the new `Song` fields have defaults.
- **Hand-checked an advanced score:** Night Drive Loop for `energy=0.75, decade=1980, mood_tags=[nostalgic, driving]` = 1.0 + 0.5 + 0.5 = 2.0, which is now a test.
- **Diversity order stays sorted:** penalties only grow as songs are picked, so each later pick's adjusted score can't beat an earlier one's. I confirmed the `--diverse` output scores never go up down the list.
- **Read the diversity results critically** instead of assuming "more diverse = better." For Chill Lofi, it swapped in a sad folk song, which I documented as a trade-off in the README and model card.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy.** Each ranking mode is an interchangeable object, and the recommender uses whichever one it's given without knowing which mode it is.

**How did AI help you brainstorm or implement it?**

I asked the AI how to support Genre-First, Mood-First, and Energy-Focused modes without copy-pasting the scoring code. It compared three options:

1. **`if mode == ...` branches inside `score_song`:** quick, but every new mode makes one function longer and harder to test.
2. **A separate scoring function per mode:** clearer, but the genre, mood, and energy rules would be duplicated in each one, so a bug fix would have to be made several times.
3. **Strategy objects:** each mode is a small object that holds its weights and exposes `score(user_prefs, song)`.

We chose option 3, in a lightweight form. The modes only differ by *how much* each signal counts, not *what* is counted, so each strategy wraps the one shared `score_song` with its own weights. There's still a single source of truth for the scoring math, and adding a mode is one line. If a future mode needed totally different logic (for example, collaborative filtering), it could be a new class with the same `score` method, and `recommend_songs` wouldn't change.

**How does the pattern appear in your final code?**

- `ScoringMode` in `src/recommender.py`: a frozen dataclass with `name`, `description`, `weights`, and a `score()` method.
- `SCORING_MODES`: the registry of the four strategies (`balanced`, `genre-first`, `mood-first`, `energy-focused`).
- `recommend_songs(..., mode=...)` calls `mode.score(user_prefs, song)` for every song.
- In `src/main.py`, `--mode` picks a strategy by name (argparse's `choices` comes from `SCORING_MODES`, so a new mode shows up in the CLI automatically).
