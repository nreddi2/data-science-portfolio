# Chess outcome prediction

The [project page](https://nreddi2.github.io/data-science-portfolio/projects/chess-outcome-prediction/) explains the experiment. `chess_outcomes.ipynb` contains the executed analysis, including code, tables, and figures.

## Data and scope

The source is the [official Lichess open database](https://database.lichess.org/), released under CC0. `fetch_games.py` streams the September 2026 rated standard-game archive and saves every tenth complete header block among its first 300,000 headers. It stops after 30,000 saved rows; it does not download the entire month. This systematic prefix sample is not random or representative of all Lichess games.

The cleaned sample covers September 1, 2026, from 00:00:00 to 04:13:48 UTC. Cleaning retains 29,792 games. Player names are replaced with within-sample IDs and game URLs with hashes. These are pseudonyms, not a guarantee of anonymity. Event fields may retain public tournament links. Identities and events are not model inputs.

Files:

- `data/games_raw.csv`: the saved 30,000-row header sample before cleaning, with unnecessary post-game fields omitted at collection.
- `data/source.json`: source URL, retrieval time, sampling method, and SHA-256 checksum.
- `results/cleaning_audit.csv`: sequential exclusions.
- `results/games_clean.csv`: retained games and engineered features.
- `results/model_selection.csv` and `grid_search.csv`: training-only validation scores and parameters.
- `results/test_metrics.csv` and `per_class_metrics.csv`: held-out performance for every comparison.
- `results/test_predictions.csv`: selected-model outcomes and probabilities, without player identifiers.
- `results/run_summary.json`: split dates, environment versions, seed, and sample counts.

## Reproduce locally

Use Python 3.12 and open a terminal in this directory. Install the environment:

```sh
python -m pip install -r requirements.txt
```

Open `chess_outcomes.ipynb` in Jupyter or a notebook-capable editor, choose that Python environment, and run all cells in order. A command-line alternative, using the included nbclient dependency, is:

```sh
python run_notebook.py
```

The normal run reads the included CSV and checks its checksum; no API key or new download is needed. The notebook runs from this directory or the repository root. It writes tables into `results/` and plots into `assets/images/chess/`. A full run trains 42 validation fits plus four final fitted models; runtime depends on the machine.

The submitted notebook was executed from top to bottom in a local Jupyter kernel using the included runner. Its displayed outputs come from those executions. The runner saves a separate `chess_outcomes_rerun.ipynb` and refreshes the result tables and charts. The seed is 2301. Minor numerical differences can occur across operating systems or package versions. The exact tested versions appear in `requirements.txt` and `results/run_summary.json`.

## Optional: collect the same source again

```sh
python fetch_games.py
```

This overwrites `data/games_raw.csv` and `data/source.json`. Back up those two files first if preserving the submitted run matters. It streams part of a very large compressed archive; canceling leaves the original data untouched until collection finishes. Do not download the full monthly archive just to run the notebook. Lichess may revise its archive, so a later recollection is not guaranteed to match the saved checksum.

## Modeling choices

The five inputs are signed rating difference, absolute rating difference, average rating, log(1 + starting seconds), and log(1 + increment seconds). The target maps White win to 0, Draw to 1, and Black win to 2. The PGN Elo tags contain Glicko-2 ratings.

The notebook uses approximately 80% earlier starts for training and 20% later starts for testing. Three expanding-window training folds select hyperparameters with macro-F1. Scaling occurs inside each training fold. Ordinary and balanced weighting are compared for both logistic regression and random forests. The higher-rated rule and majority/training-prior baseline provide reference performance.

Blank probability metrics for the higher-rated rule mean “not applicable”: that hard rule does not define probabilities. Class precision/F1 is reported as zero when there are no predictions of that class. The selected ordinary logistic model has zero draw recall; that is a measured limitation, not a missing output. Missing means in an error-summary category with zero games mean “no observations,” not a data cleaning failure.

The split uses start times, not finish times, and repeated players remain possible. Therefore it is not a strict live-deployment or player-independent evaluation. Test-set permutation importance is descriptive; it is not used to tune the model. See the project page for limitations and references.

## AI disclosure

OpenAI Codex with GPT-6 Astra (the model-selector label confirmed by the author) assisted with the design, implementation, debugging, execution, visualizations, interpretation, writing, and integration. This was substantive generative-AI assistance. The notebook does not claim that the author independently wrote or manually reviewed every line.
