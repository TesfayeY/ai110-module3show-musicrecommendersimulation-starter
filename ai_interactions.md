# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

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

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
