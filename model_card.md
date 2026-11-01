# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

**Goal / Task:** VibeFinder suggests the 5 songs from a small catalog that best fit a listener's stated taste. It doesn't learn anything. It compares each song's genre, mood, and energy to what the user says they want and ranks the closest matches.

**Intended use:** classroom exploration of how content-based recommenders turn data into rankings, and where they go wrong. It assumes the user can name one favorite genre, one favorite mood, and roughly how energetic they want the music to be.

**Not intended for:** real users or a real music app. The catalog is 18 made-up songs, the weights are hand-picked rather than learned, and it can't tell what anyone actually enjoys. It shouldn't be used to judge whether a song or artist is "good," or to make decisions about which artists get promoted.

---

## 3. How the Model Works  

Every song gets a score, and the highest scores win.

- If the song's genre is the user's favorite genre, it gets **2 points**.
- If the song's mood is the user's favorite mood, it gets **1 point**.
- Every song gets **up to 1 point for energy**. A song with exactly the energy the user wants gets the full point, and it loses points the further away it is. Energy that's "too high" counts as badly as energy that's "too low."
- If the user says whether they like acoustic music, songs get **up to half a point** for matching that.

The program scores all 18 songs this way, sorts them from highest to lowest, and shows the top 5 with a list of reasons, such as "genre match (+2.0)," so you can see why each song is there.

**Changes from the starter:** the starter code returned no songs at all. I implemented CSV loading, the scoring rule, the ranking, the reasons, and the class-based `Recommender`. I also added an acoustic preference (using the `likes_acoustic` field the starter `UserProfile` already had) and a way to swap the weights for experiments.

---

## 4. Data  

- **18 songs**: the 10 from the starter plus 8 I added.
- **Features:** genre, mood, energy (0–1), tempo, valence, danceability, acousticness. Only genre, mood, energy, and acousticness are used for scoring.
- **15 genres:** lofi (3), pop (2), and one song each for indie pop, rock, ambient, jazz, synthwave, metal, country, r&b, edm, classical, hip hop, reggae, and folk.
- **13 moods:** chill (3), happy (2), intense (2), relaxed (2), and one each for moody, focused, angry, nostalgic, romantic, euphoric, melancholy, energetic, and sad.
- **What I added:** metal/angry, country/nostalgic, r&b/romantic, edm/euphoric, classical/melancholy, hip hop/energetic, reggae/relaxed, and folk/sad, so the catalog covers sad and aggressive music, not just happy and chill.

**What's missing:** lyrics, language, artist popularity, release year, and any listening history. Energy has a gap: 8 songs are 0.75 or higher, 5 are below 0.40, and **no songs are between 0.55 and 0.75**. Most genres have only one song, so the catalog is very thin for anyone who isn't into lofi or pop.

---

## 5. Strengths  

- **Clear, common tastes work well.** The Chill Lofi profile gets all three lofi songs on top, followed by ambient and jazz, which feels right for a study playlist. Deep Intense Rock gets Storm Runner first and then other loud, high-energy songs.
- **Every result explains itself.** The reasons make it easy to see *why* something ranked where it did, which made debugging and evaluation much easier.
- **Energy closeness separates songs within a genre.** For the pop/happy user, Sunrise City (0.82 energy) beats Gym Hero (0.93) even though both are pop.

---

## 6. Limitations and Bias 

**Main weakness: a high-energy filter bubble.** Everyone gets up to 1 point for energy no matter what, and almost half the catalog (8 of 18 songs) is high energy. So once a user runs out of songs in their genre, the leftover spots fill with the same loud tracks. Gym Hero and Block Party Anthem each show up in 4 of my 7 test profiles, and Bass Cathedral in 3, even for a "sad folk" listener. A metal, folk, or classical fan gets exactly one real match and then four songs chosen only by energy, so the system serves niche-genre users much worse than lofi or pop fans.

**Other biases I found:**

- **Genre outweighs everything.** A genre match (+2) is worth as much as a perfect mood *and* perfect energy match combined. In the Conflicted profile, Empty Highway won with 0.30 energy even though the user asked for 0.90, because genre and mood matched.
- **Exact text matching.** "Indie pop" gets no credit as "pop," "relaxed" gets no credit as "chill," and a k-pop fan gets zero genre points from anything.
- **The energy gap treats users unequally.** A user who wants middle energy (0.5) can never be more than 0.5 away from any song, so every song gets at least 0.5 energy points. A user who wants 0.9 can be 0.7 away from the quietest songs. Extreme-energy users get sharper rankings, while middle-energy users get flatter ones where energy barely matters.
- **Ignored features.** Tempo, valence, and danceability are in the data but not scored, so a happy song and a melancholy song with the same energy look identical for energy purposes.

---

## 7. Evaluation  

I tested 7 profiles: 4 normal tastes and 3 adversarial or edge cases meant to trick the scoring. All output below is from `python -m src.main` with the default weights.

### Results

**Default Pop/Happy**

```
Profile: Default Pop/Happy
Prefs:   genre=pop, mood=happy, energy=0.8
------------------------------------------------------------
1. Sunrise City by Neon Echo (pop, happy)
   Score: 3.98
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.82 vs target 0.80 (+0.98)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 2.87
   - genre match (+2.0)
   - energy 0.93 vs target 0.80 (+0.87)
3. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 1.96
   - mood match (+1.0)
   - energy 0.76 vs target 0.80 (+0.96)
4. Block Party Anthem by MC Lumen (hip hop, energetic)
   Score: 0.96
   - energy 0.84 vs target 0.80 (+0.96)
5. Night Drive Loop by Neon Echo (synthwave, moody)
   Score: 0.95
   - energy 0.75 vs target 0.80 (+0.95)
```

**High-Energy Pop**

```
Profile: High-Energy Pop
Prefs:   genre=pop, mood=happy, energy=0.9, likes_acoustic=False
------------------------------------------------------------
1. Sunrise City by Neon Echo (pop, happy)
   Score: 4.33
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.82 vs target 0.90 (+0.92)
   - non-acoustic preference (+0.41)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 3.44
   - genre match (+2.0)
   - energy 0.93 vs target 0.90 (+0.97)
   - non-acoustic preference (+0.47)
3. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 2.19
   - mood match (+1.0)
   - energy 0.76 vs target 0.90 (+0.86)
   - non-acoustic preference (+0.33)
4. Storm Runner by Voltline (rock, intense)
   Score: 1.44
   - energy 0.91 vs target 0.90 (+0.99)
   - non-acoustic preference (+0.45)
5. Bass Cathedral by Kilowatt Kids (edm, euphoric)
   Score: 1.43
   - energy 0.95 vs target 0.90 (+0.95)
   - non-acoustic preference (+0.48)
```

**Chill Lofi**

```
Profile: Chill Lofi
Prefs:   genre=lofi, mood=chill, energy=0.35, likes_acoustic=True
------------------------------------------------------------
1. Library Rain by Paper Lanterns (lofi, chill)
   Score: 4.43
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.35 vs target 0.35 (+1.00)
   - acoustic preference (+0.43)
2. Midnight Coding by LoRoom (lofi, chill)
   Score: 4.29
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.42 vs target 0.35 (+0.93)
   - acoustic preference (+0.35)
3. Focus Flow by LoRoom (lofi, focused)
   Score: 3.34
   - genre match (+2.0)
   - energy 0.40 vs target 0.35 (+0.95)
   - acoustic preference (+0.39)
4. Spacewalk Thoughts by Orbit Bloom (ambient, chill)
   Score: 2.39
   - mood match (+1.0)
   - energy 0.28 vs target 0.35 (+0.93)
   - acoustic preference (+0.46)
5. Coffee Shop Stories by Slow Stereo (jazz, relaxed)
   Score: 1.43
   - energy 0.37 vs target 0.35 (+0.98)
   - acoustic preference (+0.45)
```

**Deep Intense Rock**

```
Profile: Deep Intense Rock
Prefs:   genre=rock, mood=intense, energy=0.9, likes_acoustic=False
------------------------------------------------------------
1. Storm Runner by Voltline (rock, intense)
   Score: 4.44
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.91 vs target 0.90 (+0.99)
   - non-acoustic preference (+0.45)
2. Gym Hero by Max Pulse (pop, intense)
   Score: 2.44
   - mood match (+1.0)
   - energy 0.93 vs target 0.90 (+0.97)
   - non-acoustic preference (+0.47)
3. Bass Cathedral by Kilowatt Kids (edm, euphoric)
   Score: 1.43
   - energy 0.95 vs target 0.90 (+0.95)
   - non-acoustic preference (+0.48)
4. Iron Verdict by Black Anvil (metal, angry)
   Score: 1.42
   - energy 0.97 vs target 0.90 (+0.93)
   - non-acoustic preference (+0.48)
5. Block Party Anthem by MC Lumen (hip hop, energetic)
   Score: 1.38
   - energy 0.84 vs target 0.90 (+0.94)
   - non-acoustic preference (+0.44)
```

**Conflicted (sad but high energy)**

```
Profile: Conflicted (sad but high energy)
Prefs:   genre=folk, mood=sad, energy=0.9
------------------------------------------------------------
1. Empty Highway by June Harlow (folk, sad)
   Score: 3.40
   - genre match (+2.0)
   - mood match (+1.0)
   - energy 0.30 vs target 0.90 (+0.40)
2. Storm Runner by Voltline (rock, intense)
   Score: 0.99
   - energy 0.91 vs target 0.90 (+0.99)
3. Gym Hero by Max Pulse (pop, intense)
   Score: 0.97
   - energy 0.93 vs target 0.90 (+0.97)
4. Bass Cathedral by Kilowatt Kids (edm, euphoric)
   Score: 0.95
   - energy 0.95 vs target 0.90 (+0.95)
5. Block Party Anthem by MC Lumen (hip hop, energetic)
   Score: 0.94
   - energy 0.84 vs target 0.90 (+0.94)
```

**Unknown Genre (k-pop)**

```
Profile: Unknown Genre (k-pop)
Prefs:   genre=k-pop, mood=happy, energy=0.7
------------------------------------------------------------
1. Rooftop Lights by Indigo Parade (indie pop, happy)
   Score: 1.94
   - mood match (+1.0)
   - energy 0.76 vs target 0.70 (+0.94)
2. Sunrise City by Neon Echo (pop, happy)
   Score: 1.88
   - mood match (+1.0)
   - energy 0.82 vs target 0.70 (+0.88)
3. Night Drive Loop by Neon Echo (synthwave, moody)
   Score: 0.95
   - energy 0.75 vs target 0.70 (+0.95)
4. Block Party Anthem by MC Lumen (hip hop, energetic)
   Score: 0.86
   - energy 0.84 vs target 0.70 (+0.86)
5. Velvet Hours by Amber Vale (r&b, romantic)
   Score: 0.85
   - energy 0.55 vs target 0.70 (+0.85)
```

**Mood Only (no genre)**

```
Profile: Mood Only (no genre)
Prefs:   mood=chill, energy=0.5
------------------------------------------------------------
1. Midnight Coding by LoRoom (lofi, chill)
   Score: 1.92
   - mood match (+1.0)
   - energy 0.42 vs target 0.50 (+0.92)
2. Library Rain by Paper Lanterns (lofi, chill)
   Score: 1.85
   - mood match (+1.0)
   - energy 0.35 vs target 0.50 (+0.85)
3. Spacewalk Thoughts by Orbit Bloom (ambient, chill)
   Score: 1.78
   - mood match (+1.0)
   - energy 0.28 vs target 0.50 (+0.78)
4. Island Time by Coral Sound System (reggae, relaxed)
   Score: 1.00
   - energy 0.50 vs target 0.50 (+1.00)
5. Porch Light Letters by Willow Creek (country, nostalgic)
   Score: 0.98
   - energy 0.52 vs target 0.50 (+0.98)
```

### Comparing profiles

- **Default Pop/Happy vs. High-Energy Pop:** the top 3 are identical (Sunrise City, Gym Hero, Rooftop Lights). Raising the energy target from 0.8 to 0.9 and adding a non-acoustic preference only changed spots 4–5, swapping hip hop and synthwave for rock and edm, the loudest songs in the catalog. That makes sense, because genre and mood points decide the top and energy only matters among songs with no matches.
- **Default Pop/Happy vs. Chill Lofi:** no overlap at all. Pop/happy pulls bright, high-energy songs, and lofi pulls quiet, acoustic ones (energy 0.28–0.42). This is the clearest sign the profile actually works.
- **Default Pop/Happy vs. Deep Intense Rock:** both lists include Gym Hero, but for different reasons. Pop fans get it for genre, and rock fans get it for mood ("intense") and energy. Same song, different explanation, which is what the reasons are for.
- **High-Energy Pop vs. Deep Intense Rock:** Storm Runner, Gym Hero, and Bass Cathedral show up in both. Once you ask for 0.9 energy and non-acoustic sound, the "other loud songs" pool is the same small group no matter which genre you like.
- **High-Energy Pop vs. Chill Lofi:** these are opposites on every signal, and the lists share nothing. The acoustic preference pushes them further apart (lofi songs earn +0.35 to +0.46 for being acoustic).
- **Chill Lofi vs. Deep Intense Rock:** no overlap. The rock list is all energy 0.84+, while the lofi list never goes above 0.42.
- **Chill Lofi vs. Mood Only (chill, no genre):** without a genre, Focus Flow (lofi but "focused") drops out, and reggae and country songs with mid energy fill in. Midnight Coding jumps over Library Rain because 0.42 energy is closer to 0.5.
- **Conflicted vs. Deep Intense Rock:** spots 2–5 are almost identical (Storm Runner, Gym Hero, Bass Cathedral, Block Party Anthem). After the single folk song, a "sad" listener gets the same workout playlist as a rock fan, which is the filter bubble from Section 6.
- **Unknown Genre (k-pop) vs. Default Pop/Happy:** with no genre match possible, Rooftop Lights (indie pop) beats Sunrise City (pop) because 0.76 energy is closer to 0.7. The system has no idea k-pop is close to pop.

### Why "Gym Hero" keeps showing up for Happy Pop fans

Gym Hero is labeled pop, so it gets the same 2-point genre bonus as the happiest pop song. It's labeled "intense," not "happy," so it misses the mood point, but its energy (0.93) is still close to what pop fans want (0.8), so it earns almost the full energy point too. Only 3 songs in the catalog have anything to do with pop, so a pop fan's list runs out of better options fast. In plain terms, the program sees "pop + upbeat" and doesn't know a workout anthem feels different from a sunny pop song.

### What surprised me

- The **Conflicted** user (sad but energy 0.9) got a quiet, sad folk song first. Two label matches beat a huge energy mismatch, and the catalog has no song that's both sad and high energy.
- Seven very different users still shared a lot of results. Gym Hero and Block Party Anthem each appear in four lists.
- The k-pop user got reasonable results without any genre points, just from mood and energy.

### Experiment: Weight Shift (energy ×2, genre ×½)

I changed the weights to genre +1.0 and energy up to +2.0 (`python -m src.main --experiment`). The math stays valid: energy is always between 0 and 1, so the gap is too, and the top possible score is still 4.5 (1 + 1 + 2 + 0.5).

| Profile | Baseline top 5 | Experiment top 5 |
|---|---|---|
| Default Pop/Happy | Sunrise City, **Gym Hero**, Rooftop Lights, Block Party Anthem, Night Drive Loop | Sunrise City, **Rooftop Lights**, Gym Hero, Block Party Anthem, Night Drive Loop |
| Chill Lofi | Library Rain, Midnight Coding, **Focus Flow**, Spacewalk Thoughts, Coffee Shop Stories | Library Rain, Midnight Coding, **Spacewalk Thoughts**, Focus Flow, Coffee Shop Stories |
| Conflicted | Empty Highway (3.40), Storm Runner (0.99), … | Empty Highway (2.80), Storm Runner (1.98), … |
| Deep Intense Rock | Storm Runner, Gym Hero, Bass Cathedral, Iron Verdict, Block Party Anthem | same order |

**More accurate or just different?** A bit of both. For pop/happy, Rooftop Lights (happy, right energy) moving above Gym Hero (intense) feels *more accurate*, and the same goes for the chill ambient track passing a "focused" lofi one. But the Conflicted user still gets the low-energy folk song first, only by a smaller margin, and the rock list didn't change at all. Halving genre helped the mood and energy signals matter more, but it didn't fix the filter bubble, because that comes from the thin catalog, not just the weights.

### Tests

`pytest` runs 6 automated checks: the two starter tests (the pop/happy song ranks first and explanations aren't empty), plus checks that the CSV numbers load as numbers, that a perfect match scores 4.0, that closer energy scores higher, and that results come back sorted.

---

## 8. Future Work  

1. **Partial credit for similar genres and moods.** Treat "indie pop" as close to "pop" and "relaxed" as close to "chill," instead of all-or-nothing matching.
2. **A diversity rule.** Penalize a song if its artist or genre is already in the top results, so lists don't fill up with the same loud songs.
3. **More data and more features.** Add enough songs that every genre has several options, fill the 0.55–0.75 energy gap, and score valence so "happy" vs. "sad" uses the music itself, not just a label.

---

## 9. Personal Reflection  

**Biggest learning moment:** the Conflicted test. I expected a sad-but-high-energy user to get something in between, but the system confidently picked a quiet folk song, because two label matches beat a huge energy mismatch. A recommender can look "confident" and still be wrong in a way the user would notice right away.

**How AI helped, and when I double-checked it:** I used Claude Code as an agent to research how Spotify and YouTube recommend music, suggest features, write the loading, scoring, and ranking code, and run every profile. I still had to check its work. I hand-calculated scores (Sunrise City: 2 + 1 + (1 − 0.02) = 3.98) to make sure the math matched the recipe. I also confirmed that the starter `main.py` import (`from recommender import ...`) would crash under `python -m src.main` before accepting the fix. And I made sure the experiment output was pasted from real runs rather than written from memory.

**What surprised me:** how much four simple rules already "feel" like recommendations. The lofi list looks like a real study playlist, and each "because" line makes the results seem smarter than they are. The same rules also produce obvious mistakes, like a sad listener getting a gym playlist.

**What I'd try next:** a diversity penalty and partial genre matching, then a tiny version of collaborative filtering with a few fake users' likes, to see how "people like you also liked" changes the results compared to pure song features.
