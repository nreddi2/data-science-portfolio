---
layout: default
title: "Before the first move: predicting chess outcomes"
description: "A three-class chess prediction experiment using pre-game ratings and time controls, with an honest look at missed draws."
permalink: /projects/chess-outcome-prediction/
page_class: "content-page chess-page"
extra_css: /assets/css/chess.css
---

<div class="prose chess-project" markdown="1">

<span class="eyebrow">DTSC 2301 · Project 2 · Classification</span>

# Predicting a Chess game before the first move

<p class="lede">Ratings tell us who looks stronger. Can they also tell us when neither player will win?</p>

Before a chess game starts, the higher rated player seems like the obvious choice. I wanted to see if I could potentially challenge this presumption and make a machine learning model that can predict the outcome of a game; win, loss, or draw. Although it would have been a lot more straightforward for me to exclude the draw outcome of the game in my model, I kept draws in this project and tested whether ratings and time controls could distinguish all three outcomes. The models found some useful patterns, but they struggled to turn those patterns into reliable draw predictions.

<div class="hero-actions">
  <a class="button" href="https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/chess_outcomes.ipynb">Read the executed notebook</a>
  <a class="button secondary" href="https://github.com/nreddi2/data-science-portfolio/tree/main/analysis/chess">Data and code</a>
</div>

<div class="chess-summary">
  <div><strong>29,792 </strong><span>usable games in a bounded sample</span></div>
  <div><strong>3 outcomes </strong><span>White win, draw, Black win</span></div>
  <div><strong>0 of 217 </strong><span>test draws found by the selected model</span></div>
</div>

<p class="finding caution"><strong>Main finding:</strong> The selected logistic model slightly improved accuracy over the higher-rated-player rule, but the rule achieved better macro-F1. Class balancing found more draws at the cost of many false draw predictions. This is a limited experiment, not a successful draw-prediction system.</p>

<nav class="chess-toc" aria-label="Project contents">
  <strong>In this project</strong>
  <ol>
    <li><a href="#problem">Problem definition</a></li>
    <li><a href="#background">Background and context</a></li>
    <li><a href="#data">Data description</a></li>
    <li><a href="#exploration">Data understanding and exploration</a></li>
    <li><a href="#preparation">Preparation and feature selection</a></li>
    <li><a href="#models">Baselines and model development</a></li>
    <li><a href="#evaluation">Evaluation and selection</a></li>
    <li><a href="#interpretation">Interpretation and errors</a></li>
    <li><a href="#limitations">Limitations and reflection</a></li>
    <li><a href="#transparency">Code, references, and AI disclosure</a></li>
  </ol>
</nav>

<h2 id="problem">1. Problem definition</h2>

**Research question:** How well can pre-game player ratings and time controls predict a White win, a draw, or a Black win in a game of chess?

I treat this as **multiclass classification**. The target is the final recorded result: `1-0` for a White win, `1/2-1/2` for a draw, or `0-1` for a Black win. I use “White” and “Black” only to describe the pieces each player controls.

I also wanted to see whether draws occur more often in closely matched games, among stronger players, or in slower formats. These are hypotheses that I wanted to test, to hopefully see an improvement or variation between different formats of games. Removing draws would turn the task into a simpler question and hide an important weakness of a winner only prediction rule.

This question could potentially interest players or developers who want a pre-game probability display. It does not require an engine to inspect the position. That makes the prediction inexpensive, but it also limits what the model can know: before the first move, it cannot see a blunder, a repetition, or a player's decision to accept a draw.

<h2 id="background">2. Background and context</h2>

Chess ratings summarize past performance, not certainty about the next game. Lichess, as well as the majority of chess websites, uses the Glicko-2 rating system (although its game files label ratings WhiteElo and BlackElo). Glicko-2 also tracks rating deviation and volatility. The two published rating numbers alone leave out that uncertainty (Glickman, 2022). These ratings should not be treated as directly interchangeable with ratings from another chess platform.

It should be noted that a draw is also different from a 50% probability of winning. It is a separate outcome. For expected score comparisons, a White win will count as 1, a draw as 0.5, and a Black win as 0. Keeping separate outcome probabilities lets me distinguish a likely draw from an uncertain game that could end in either player's favor.

The two model families here offer a useful contrast. Multinomial logistic regression assigns probabilities using a linear combination of the inputs. A random forest combines decision trees and can represent nonlinear relationships and interactions (Breiman, 2001). Neither model receives the moves. I therefore ask what a few pre-game conditions can explain, rather than expect either model to understand chess positions.

<h2 id="data">3. Data description</h2>

### Source, collection, and unit of analysis

I use the **September 2026 rated standard-game archive** from the [Lichess open database](https://database.lichess.org/), which releases its exports under CC0 (Lichess, n.d.-c). This is a direct public archive download as opposed to a web scrape. It does not require an account or API key.

The full monthly archive is much larger than I figured would be necessary to train the model. I decided to take a systematic sample of the dataset in order to effectively utilize this data. The collector streams it, reads the first 300,000 game headers, and retains every tenth header. That produces **30,000 sampled rows before cleaning**. It selects rows before checking results, so it does not intentionally overrepresent wins or draws. A fixed sampling interval can also interact with archive ordering.

Each row represents **one game**, not one player, one move, or one board position. The retained games started between **September 1, 2026, 00:00:00 and 04:13:48 UTC**. This approximately four-hour window is a major limit on the conclusions. The [source record](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/data/source.json) preserves the URL, sampling rule, retrieval time, and file checksum.

### Features: what the columns measure

I kept separate the ideas I want to study from the columns I use to measure them. “Relative playing strength” is a concept which refers to the difference between two pre-game ratings is its numerical measurement. The table shows the original info as well as the engineered inputs.

| Concept | Source columns or saved field | Operational definition and role |
|---|---|---|
| Game outcome | `Result` → `result` | White win, Draw, or Black win. This is the target, never an input. |
| Each player's estimated strength | `WhiteElo`, `BlackElo` → `white_rating`, `black_rating` | Pre-game Glicko-2 ratings. I use them to calculate the three rating features below. |
| Direction of the rating advantage | `elo_diff` | White rating − Black rating. Positive means White has the higher rating. The variable name follows the PGN labels, not the true rating-system name. |
| Size of the mismatch | `abs_elo_diff` | Absolute value of the signed gap. It measures how far apart the ratings are without identifying the favorite. |
| Overall rating level | `average_rating` | Mean of the two player ratings. Two equally rated beginners and two equally rated experts both have a zero gap but different average ratings. |
| Starting clock allowance | `TimeControl` → `base_seconds` | Seconds each player starts with. The model uses `log(1 + base_seconds)`. |
| Extra time per move | `TimeControl` → `increment_seconds` | Seconds added after a move. The model uses `log(1 + increment_seconds)`. |
| Time format | Derived `speed` | UltraBullet, Bullet, Blitz, Rapid, or Classical, based on starting seconds + 40 × increment. I use this for grouped descriptions, not as an extra predictor. |
| When the game started | `UTCDate`, `UTCTime` → `timestamp` | A UTC timestamp used to order and split games, not to predict the result. |
| Identity and eligibility checks | Hashed game ID, pseudonymous player IDs, title, event, variant | Used for duplicate checks, known-bot filtering, and player-overlap reporting. Excluded from the model. |

For example, a `300+3` time control gives each player 300 starting seconds and adds 3 seconds per move. Lichess classifies the format using `300 + 40 × 3 = 420` estimated seconds, which falls in Blitz. That estimate is not an observed game duration (Lichess, n.d.-b).

### Dataset size and missing values

The saved sample has **30,000 rows and 14 metadata columns**. After cleaning, it has **29,792 games**. The model uses five engineered numerical inputs, not all metadata columns.

After removing tagged bots and an unfinished result, both rating columns and the timestamp have **zero missing or invalid values**. However, 17 remaining correspondence games have `-` instead of a timed `base+increment` control. Both parsed clock fields are therefore missing in those same 17 rows (not 34 separate games). I decided it would make sense to exclude these games because this analysis compares timed games.

Blank title fields normally indicate that no title was recorded. I did not ignore a game due to either players lacking titles. The [missing-value table](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/results/missing_values.csv) reports the exact stage of the check, and the cleaning log below accounts for every excluded row.

<h2 id="exploration">4. Data understanding and exploration</h2>

I reserve later games for testing before exploring relationships. The figures in this section use **only the 23,833 training games**. This keeps the later results from steering feature selection or the story I expect a model to learn.

### Start with the outcome imbalance

| Outcome | Training games | Training share | Test games |
|---|---:|---:|---:|
| White win | 11,900 | 49.9% | 3,062 |
| Draw | 839 | 3.5% | 217 |
| Black win | 11,094 | 46.5% | 2,680 |

Shares are rounded. Across training and test combined, the cleaned sample contains **1,056 draws**. The imbalance matters: a model can miss every draw and still get roughly half the games right. I therefore kept accuracy as context and made sure to emphasize macro-F1 and class specific results.

<figure>
  <a href="{{ '/assets/images/chess/01_class_balance.png' | relative_url }}"><img src="{{ '/assets/images/chess/01_class_balance.png' | relative_url }}" width="1460" height="848" alt="Training outcome shares: White wins 49.9 percent, draws 3.5 percent, and Black wins 46.5 percent." loading="lazy"></a>
  <figcaption>Figure 1. Training class distribution. Counts and percentages show why accuracy alone can hide missed draws. Select any chart to open its full-size image.</figcaption>
</figure>

### Most pairings are close, but not all of them

The median training rating gap is **1 point in White's favor**. The median absolute gap is **33 points**, and the middle half of absolute gaps lies between **13 and 71 points**. The average of the two players' ratings has a median of **1,662**. The full cleaned sample spans individual ratings from **400 to 3,211** and contains **22 games with gaps above 1,000 points**.

I keep the large gaps rather than assume they are mistakes. They remain valid numerical ratings, and deleting them would remove the easiest looking matchups. The histogram makes their rarity visible. The outcome chart shows a directional pattern: White wins more often when White has a large rating advantage, and less often when Black has the advantage. This inference was pretty expected from my prior knowledge and made a lot of sense intuitively speaking, but that does not imply most games are easy to predict, because most gaps cluster near zero.

<figure>
  <a href="{{ '/assets/images/chess/02_rating_gap.png' | relative_url }}"><img src="{{ '/assets/images/chess/02_rating_gap.png' | relative_url }}" width="2180" height="884" alt="A histogram concentrates near a zero rating gap; grouped outcome bars show White's win share rising as White's rating advantage increases." loading="lazy"></a>
  <figcaption>Figure 2. Signed rating gaps and result shares in training. The outer gap groups contain relatively few games; their result shares should not be read as precise population estimates.</figcaption>
</figure>

### Test the three draw hypotheses

The results are less tidy than “closer, stronger, slower always means more draws.”

- **Rating gap:** Games within 50 points draw **3.6%** of the time. The rate reaches **4.3%** in the 201–400 group, then falls to **1.1%** above 400. Only five of the 456 games in that last group are draws. The pattern is not a steady decline as the gap grows.
- **Average rating:** The rate is **2.8%** above 1,200 through 1,600, compared with **4.4%** above 2,000 through 2,400. It is **4.2%** above 2,400. This supports a broad association with stronger rating levels, not a perfectly increasing relationship.
- **Time format:** Bullet has a **2.6%** draw rate, compared with **4.1%** for Blitz and **3.9%** for Rapid. Classical reaches **4.4%**, but that estimate rests on only **six draws in 135 games**. This sample does not establish a simple rule that every slower category draws more often.

<figure>
  <a href="{{ '/assets/images/chess/03_draw_patterns.png' | relative_url }}"><img src="{{ '/assets/images/chess/03_draw_patterns.png' | relative_url }}" width="1460" height="2180" alt="Three panels compare draw rates by absolute rating gap, average rating, and time format, using a shared percentage scale and showing each group's game count." loading="lazy"></a>
  <figcaption>Figure 3. Training draw rates. All panels use the same vertical scale. Counts show where the evidence is thin; the bars describe associations and do not isolate causal effects.</figcaption>
</figure>

These comparisons motivate the rating-level and clock inputs alongside the signed gap. They do not promise that those inputs can pinpoint an individual draw. The [training summary statistics](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/results/training_summary.csv) and grouped-rate tables in the results folder provide the underlying numbers.

<h2 id="preparation">5. Data preparation and feature selection</h2>

### Step 1: Check eligibility and account for exclusions

I first checked game IDs and duplicates. A duplicate refers to a repeated game ID here, so two games that happen to share the same ratings are not considered duplicates. I then checked the variant and explicitly casual event labels. The source is already a rated-game archive; I do not require the word “Rated” in every event name, because some Swiss tournaments omit it.

Next, I removed games where either title equals `BOT`, remove the one unfinished result, and parse the ratings, timestamps, and clocks. A missing BOT tag does not prove that a player never used outside assistance; it only means this filter did not identify a registered bot account.

| Sequential check | Games removed | Games remaining |
|---|---:|---:|
| Starting sample | — | 30,000 |
| Missing game ID | 0 | 30,000 |
| Duplicate game ID | 0 | 30,000 |
| Nonstandard or explicitly casual game | 0 | 30,000 |
| Tagged bot account | 190 | 29,810 |
| Unfinished or unrecognized result | 1 | 29,809 |
| Missing/invalid required fields: untimed correspondence games | 17 | 29,792 |
| Nonpositive rating | 0 | 29,792 |
| Zero starting time and zero increment together | 0 | 29,792 |

The counts are sequential, so no removed row appears twice. Zero starting seconds can still be valid when there is a positive increment. I check the combination rather than remove every zero in either clock field.

### Step 2: Turn the source columns into five inputs

I use pandas to convert strings into numbers and dates, split the clock notation, and calculate the rating measures. For example:

```python
df["elo_diff"] = df.white_rating - df.black_rating
df["abs_elo_diff"] = df.elo_diff.abs()
df["average_rating"] = (df.white_rating + df.black_rating) / 2
df["log_base_seconds"] = np.log1p(df.base_seconds)
df["log_increment_seconds"] = np.log1p(df.increment_seconds)
```

The signed gap says which player has the advantage. Its absolute value distinguishes a close pairing from a mismatch. The average separates low-rated from high-rated pairings. Log transforms keep a very long clock from dominating the scale while preserving zero increments.

### Step 3: Keep post-game information out

I restrict the input matrix to those five columns. `Result` supplies the target but never enters the input matrix. I exclude rating changes, `Termination`, moves, opening names, ECO codes, and player names. Some fields plainly reveal the end of the game; others, such as the actual opening, are not known at the pre-game prediction moment. The collector does not save those unnecessary fields. Event labels, titles, IDs, and timestamps support checks but do not become predictors.

### Step 4: Split chronologically and fit preprocessing on training only

I sort games by UTC start time. The earliest **23,833** form the training set; the latest **5,959** form the test set. Training ends at **03:21:18 UTC**, and testing begins at **03:21:19 UTC**. I keep equal boundary timestamps together and verify that all three classes appear on each side and that no game ID crosses the split.

Within training, three expanding-window folds fit on earlier games and validate on later ones. Logistic regression's `StandardScaler` sits inside the pipeline, so each fold learns its means and standard deviations only from that fold's training rows. The forest does not need scaling. No test statistics set the preprocessing or hyperparameters. The notebook saves the [exact fold boundaries](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/results/validation_folds.csv).

This split prevents future **start times** from entering training, but it does not establish independent players or guarantee that every training game ended before testing started. I address both limits below rather than describe the split as completely leakage-free.

<h2 id="models">6. Baselines and model development</h2>

### Two simple checks before machine learning

1. **Majority class:** Always predict White win, the most common training outcome. For probability metrics, use the three training class frequencies. The hard prediction and the probability reference come from the same training-only baseline.
2. **Higher-rated player:** Predict White if White has the higher rating and Black if Black has the higher rating. Break exact ties with the training majority class. This rule never predicts a draw. It does not define three outcome probabilities, so I do not invent log loss or ROC-AUC values for it.

### Two model families, with and without balancing

I fit multinomial logistic regression and a random forest, using both ordinary weights and `class_weight="balanced"`. Balanced weights assign more importance to minority-class errors during fitting; they do not add evidence or change the test distribution. I leave every test game in its original class.

The small search tries the following settings:

| Model | Settings searched | Fixed choices |
|---|---|---|
| Logistic regression | `C`: 0.1, 1, 10 | `lbfgs` solver; 2,000 maximum iterations; training-only standardization |
| Random forest | Maximum depth: 8 or 16; minimum leaf size: 5 or 25 | 150 trees; seed 2301 |
| Both | Ordinary and balanced class weights | Same five inputs, same three chronological validation folds |

I select hyperparameters separately for each weighting configuration using mean validation **macro-F1**, then select the learned configuration with the highest mean macro-F1. Lower validation log loss breaks a tie between configuration winners. I do not select a model based on its final test score. This yields 42 validation fits plus four refits on the full training set. The approach follows the scikit-learn model and time-split interfaces (Scikit-learn developers, n.d.-a, n.d.-d, n.d.-e).

| Configuration | Validation macro-F1 | Validation log loss | Best setting |
|---|---:|---:|---|
| Logistic, ordinary | **0.358** | 0.803 | C = 1 |
| Forest, ordinary | 0.355 | 0.810 | Depth 16; minimum leaf 25 |
| Forest, balanced | 0.352 | 0.970 | Depth 16; minimum leaf 5 |
| Logistic, balanced | 0.320 | 1.080 | C = 1 |

**I select ordinary logistic regression before evaluating the test set.** Its validation advantage over the ordinary forest is small, not evidence of a decisive performance difference. Its simpler structure also makes the final explanation easier to inspect. The [complete grid results](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/results/grid_search.csv) include fold-to-fold variability.

<h2 id="evaluation">7. Model evaluation and selection</h2>

### What the metrics mean

Macro-F1 averages the three class F1 scores equally, so a rare draw counts as much as either win class. Precision measures how often a prediction of a class is correct; recall measures how many actual examples of that class the model finds. Multiclass log loss evaluates all three probabilities and penalizes confident mistakes. Lower log loss is better. One-vs-rest ROC-AUC measures ranking for one class against the others; it does not guarantee useful precision. These metrics answer different questions (Scikit-learn developers, n.d.-b).

### Results on the 5,959 later games

| Model or baseline | Accuracy | Macro-F1 | Draw precision | Draw recall | Log loss |
|---|---:|---:|---:|---:|---:|
| Majority / training priors | 51.38% | 0.226 | 0.0% | 0.0% | 0.823 |
| Higher-rated rule | 53.08% | **0.360** | 0.0% | 0.0% | Not defined |
| **Logistic, ordinary: selected** | **53.50%** | 0.351 | 0.0% | 0.0% | **0.808** |
| Forest, ordinary | 52.69% | 0.351 | 0.0% | 0.0% | 0.813 |
| Logistic, balanced | 35.29% | 0.312 | 4.8% | 51.6% | 1.086 |
| Forest, balanced | 42.64% | 0.337 | 4.5% | 22.1% | 0.984 |

The selected model has the highest test accuracy among these comparisons and the lowest log loss among the models that supply probabilities. However, **the higher-rated rule has the best test macro-F1**. The two ordinary learned models round to the same test macro-F1, although the forest's unrounded value is slightly higher. I retain the training-selected model rather than switch after seeing the test set. Nothing here establishes that the learned model is the best overall decision rule.

Balancing changes the behavior dramatically. Balanced logistic regression finds **112 of the 217 draws**, but its draw precision is only **4.8%**. Most games it labels “Draw” actually end in a win. Its probability loss and overall accuracy also worsen. The extra draw recall is real, but it comes with a substantial cost.

<figure>
  <a href="{{ '/assets/images/chess/04_model_comparison.png' | relative_url }}"><img src="{{ '/assets/images/chess/04_model_comparison.png' | relative_url }}" width="2180" height="956" alt="The higher-rated rule has the highest test macro-F1. Balanced models recover some draws while the selected ordinary logistic model has zero draw recall." loading="lazy"></a>
  <figcaption>Figure 4. Macro-F1 and draw recall tell different stories. Orange highlights the model selected from training validation, not a winner chosen after testing.</figcaption>
</figure>

### Results across each class

| Actual class | Precision | Recall | F1 | One-vs-rest ROC-AUC | Test games |
|---|---:|---:|---:|---:|---:|
| White win | 0.545 | 0.712 | 0.618 | 0.572 | 3,062 |
| Draw | 0.000 | 0.000 | 0.000 | 0.606 | 217 |
| Black win | 0.514 | 0.376 | 0.434 | 0.572 | 2,680 |

These are the selected model's results. When a model makes no predictions for a class, the notebook reports its undefined precision as zero using `zero_division=0`. The zero draw recall is not a software error: no draw probability becomes the largest of the three probabilities. A draw ROC-AUC of 0.606 shows some ranking information, but it does not turn into a successful draw classification at the default decision rule. The [per-class results for every comparison](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/results/per_class_metrics.csv) make that distinction auditable.

<figure>
  <a href="{{ '/assets/images/chess/05_confusion_matrix.png' | relative_url }}"><img src="{{ '/assets/images/chess/05_confusion_matrix.png' | relative_url }}" width="1876" height="884" alt="Confusion matrices for ordinary logistic regression. All 217 draws are missed: 146 become White-win predictions and 71 become Black-win predictions." loading="lazy"></a>
  <figcaption>Figure 5. Counts on the left and row percentages on the right. Rows are actual results; columns are predictions. The empty Draw column reveals a weakness that 53.5% accuracy alone would hide.</figcaption>
</figure>

### Expected score is a different prediction question

I calculate White's model-implied expected score as:

```text
P(White win) + 0.5 × P(Draw)
```

Then I compare it with the Elo-style reference:

```text
1 / (1 + 10 ** ((Black rating − White rating) / 400))
```

This reference uses the familiar Elo curve, but **it is not the full Glicko-2 algorithm Lichess uses**. It also supplies an expected score, not three separate outcome probabilities. I compare each predicted score with the observed 1, 0.5, or 0, rather than treat closeness between the two formulas as proof of success.

The selected model's test score mean squared error is **0.23442**, compared with **0.23591** for the Elo-style reference. The improvement is small. It does not prove a general advantage over a rating system, and score mean squared error is not the same metric as multiclass Brier loss.

<figure>
  <a href="{{ '/assets/images/chess/06_calibration.png' | relative_url }}"><img src="{{ '/assets/images/chess/06_calibration.png' | relative_url }}" width="2000" height="920" alt="Reliability plots compare predicted and observed White scores, then compare predicted draw probabilities with observed draw shares in six equal-count groups." loading="lazy"></a>
  <figcaption>Figure 6. The dashed line represents agreement between predictions and observations. The left panel uses fixed score intervals; the right uses six equal-count probability groups and a zoomed percentage scale. Small groups, especially near extreme scores, can fluctuate considerably.</figcaption>
</figure>

I use these plots to diagnose the fixed model, not to recalibrate it on the test set. Grouped agreement cannot establish perfect individual probabilities. The detailed bin counts are saved in the [results folder](https://github.com/nreddi2/data-science-portfolio/tree/main/analysis/chess/results).

<h2 id="interpretation">8. Model interpretation and insights</h2>

### What moves the logistic model toward each outcome?

The signed rating-gap coefficient is positive for White's class (**0.231**) and negative for Black's (**−0.215**), which matches the definition of the gap. A higher average rating has a positive draw-class coefficient (**0.137**), as does a longer starting clock on the log scale (**0.160**). The absolute-gap draw coefficient is much smaller (**0.007**), so the fitted linear model does not support a strong simple absolute-gap effect in this sample.

These coefficients describe changes in class logits per training standard deviation. They are not percentage-point changes in probability. All three class logits jointly determine the probabilities, and related features can share information. I interpret them as model behavior, not evidence that changing the clock would cause a specific game to become a draw.

<figure>
  <a href="{{ '/assets/images/chess/07_coefficients.png' | relative_url }}"><img src="{{ '/assets/images/chess/07_coefficients.png' | relative_url }}" width="1640" height="884" alt="Standardized logistic coefficients: signed rating gap favors White and disfavors Black, while average rating and longer starting clocks favor the draw logit." loading="lazy"></a>
  <figcaption>Figure 7. Coefficients for all three class logits in ordinary logistic regression. Scaling supports within-model comparison, but the coefficients do not measure causal effects.</figcaption>
</figure>

### Which inputs support draw probabilities versus win probabilities?

I shuffle one feature group at a time in the held-out data and measure the increase in each class's binary log loss. I shuffle signed and absolute gaps together so their relationship stays valid. I also move both clock features together. This gives a class-specific check, unlike a forest's single global importance ranking (Scikit-learn developers, n.d.-c).

For the selected model, shuffling the gap group increases White's class loss by about **0.0296** and Black's by **0.0285**. For the draw class, shuffling the clocks increases loss by about **0.0031**, compared with **0.0013** for average rating and **0.0004** for the gap group. The clock and rating level therefore contribute more to its draw probabilities than the gap does. That still does not make the draw predictions reliable.

<figure>
  <a href="{{ '/assets/images/chess/08_class_importance.png' | relative_url }}"><img src="{{ '/assets/images/chess/08_class_importance.png' | relative_url }}" width="1640" height="884" alt="Grouped permutation loss increases show rating gap supporting win-class probabilities, and clock settings and average rating contributing more to draw probabilities." loading="lazy"></a>
  <figcaption>Figure 8. Mean loss increase across five shuffles; error bars show shuffle standard deviations, not confidence intervals. Compare groups within each class. Class prevalence affects loss magnitudes, and negative values indicate no measured benefit under this test.</figcaption>
</figure>

Shuffling can create unusual feature combinations, so this is a descriptive sensitivity check, not a causal experiment. I do not use these test-set importances to remove features and refit the model.

### Where did the actual draws go?

The selected model labels **146 actual draws as White wins** and **71 as Black wins**. Their mean absolute rating gaps are approximately **35** and **67** points, respectively. Their mean predicted draw probabilities are only about **3.9%** and **4.0%**. In other words, the model can recognize slightly more draw-prone conditions without assigning a draw enough probability to choose it as the final label.

That distinction answers the central question: **these features contain some outcome information, but they do not reliably identify individual draws in this experiment.** The models never see the positions, decisions, or move sequences needed to explain why a particular game ended that way.

<h2 id="limitations">9. Limitations, ethics, and reflection</h2>

### What limits the conclusion?

This project has several limitations that affect how I interpret the results. The sample covers about four hours on a single date, so it may reflect the players and tournaments active during that period. Keeping every tenth game from the beginning of the archive also means the sample depends on how the archive orders its games. I therefore cannot assume these results represent the entire month or all chess games. Draws are uncommon, with only 217 in the test set, and the Classical and UltraBullet groups contain relatively few games. Their draw rates could change considerably with a larger sample. Repeated players create another concern: 45.9% of test games include at least one player who also appeared in training. Although I excluded player identities from the model’s inputs, games involving the same people may share patterns. When I checked the 3,225 test games where neither player appeared in training, the selected model’s macro-F1 fell from 0.351 to 0.345. This provides a useful comparison, but I would need to design a separate split around player identities to evaluate performance on unfamiliar players more carefully. I also split games by their start times without knowing when they finished. A long game in the training set could still have been running when a test game began, meaning its result would not yet have been available in a real prediction setting. The available inputs leave out information that could help explain outcomes. For example, the published ratings do not show how uncertain each rating is, and the model has no way to account for fatigue or connection problems. Ratings also come from separate pools for different time formats, which complicates comparisons across those formats. Removing accounts with BOT tags excludes registered bots, but it cannot identify every player who may have used outside assistance. Finally, I tested only two model families with a small range of settings. Another approach might perform better, and selecting a model using macro-F1 does not guarantee that it produces the most reliable probabilities. The selected model’s small validation advantage gives me limited evidence for preferring it over the alternatives.

### Responsible use

The official archive permits reuse under CC0. I avoided publishing original player names and game URLs in the saved modeling table. I just reported aggregate patterns; this is not meant to be a ranking or criticism of particular people.

The likely cost of an error is a misleading forecast or expected score display. That is relatively low stakes here, but inflated confidence could still play a part in a player's mental. I would not use this model to accuse someone of cheating, make claims about intelligence, or replace an engine's position analysis.

### What would improve the experiment?

The next useful step is broader sampling. I would collect games across multiple days, reserve a genuinely later period, and use completion times to ensure all training labels were available. Originally I wanted to use a different database that had around 1 million games, but I decided it would be better to use a smaller dataset for feasibility's sake. I'm not upset with this decision even though I think the model's metrics would have improved a lot, as I have still learned a lot from this analysis as a whole.

I would also compare a player disjoint split and include rating uncertainty if a suitable source provides it. Any threshold tuning or probability calibration would belong inside training validation, followed by a fresh untouched test set.

The main methodological lesson is that **a model can look acceptable on accuracy while failing one of the outcomes it was built to predict**. Keeping draws exposed that failure. Reporting it gives a more useful answer than deleting the difficult class or presenting the selected model as a clear improvement over a simple rule.

<h2 id="transparency">10. Code and transparency</h2>

### Reproducibility

The [executed notebook](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/chess_outcomes.ipynb) contains the full analysis, explanatory text, and saved outputs. The [analysis directory](https://github.com/nreddi2/data-science-portfolio/tree/main/analysis/chess) includes the saved sample, download script, pinned Python dependencies, cleaning log, split boundaries, model-selection results, and final predictions. The notebook checks the saved data's SHA-256 checksum before running. Seed 2301 controls randomized fitting and shuffling.

The normal rerun reads the included CSV, so it needs no API key and does not repeat the archive download. See the [reproduction instructions](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/chess/README.md). All numerical results on this page come from the saved run. Rounded values may differ slightly from the full precision CSVs.

### AI usage and disclosure

I used AI (GPT Terra 5.6) as a utility in this project. The assistance covered research planning, data collection and analysis code, debugging, guidance on producing charts, citations, and the overall formatting and organization of this page.

The analysis generated the numerical results by executing code against the saved Lichess data. The development process checked exclusions, split boundaries, model outputs, and charts, including correcting a filter that would have wrongly excluded Swiss tournament games. This disclosure does not claim that I personally reviewed every line.

### References

<div class="references" markdown="1">

Breiman, L. (2001). Random forests. *Machine Learning, 45*, 5–32. [https://doi.org/10.1023/A:1010933404324](https://doi.org/10.1023/A:1010933404324)

Glickman, M. E. (2022, March 22). *Example of the Glicko-2 system*. [https://www.glicko.net/glicko/glicko2.pdf](https://www.glicko.net/glicko/glicko2.pdf)

Lichess. (n.d.-a). *Chess rating systems*. [https://lichess.org/page/rating-systems](https://lichess.org/page/rating-systems)

Lichess. (n.d.-b). *Frequently asked questions*. [https://lichess.org/faq](https://lichess.org/faq)

Lichess. (n.d.-c). *Lichess open database* [Data set]. Retrieved October 5, 2026, from [https://database.lichess.org/](https://database.lichess.org/)

Scikit-learn developers. (n.d.-a). *LogisticRegression*. [Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

Scikit-learn developers. (n.d.-b). *Metrics and scoring: Quantifying the quality of predictions*. [Documentation](https://scikit-learn.org/stable/modules/model_evaluation.html)

Scikit-learn developers. (n.d.-c). *Permutation feature importance*. [Documentation](https://scikit-learn.org/stable/modules/permutation_importance.html)

Scikit-learn developers. (n.d.-d). *RandomForestClassifier*. [Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)

Scikit-learn developers. (n.d.-e). *TimeSeriesSplit*. [Documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)

</div>

[Back to all projects]({{ '/projects/' | relative_url }}) · [Repository](https://github.com/nreddi2/data-science-portfolio)

</div>
