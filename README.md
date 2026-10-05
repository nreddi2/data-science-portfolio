# Data Science Portfolio

My public DTSC 2301 portfolio: [Visit the website](https://nreddi2.github.io/data-science-portfolio/).

## Projects

- [Project 1: Wage income in North Carolina](https://nreddi2.github.io/data-science-portfolio/projects/wage-income-north-carolina/)
- [Project 2: Before the first move—predicting chess outcomes](https://nreddi2.github.io/data-science-portfolio/projects/chess-outcome-prediction/)

## Project 2 materials

- [Executed Jupyter notebook](analysis/chess/chess_outcomes.ipynb)
- [Saved game-header sample](analysis/chess/data/games_raw.csv)
- [Source, sampling method, and checksum](analysis/chess/data/source.json)
- [Download script](analysis/chess/fetch_games.py)
- [Reproduction instructions](analysis/chess/README.md)
- [Detailed model results](analysis/chess/results/)

Project 2 uses a systematic sample from part of the official September 2026 Lichess rated standard-game archive, released under CC0. It retains draws and compares two baselines with ordinary and class-balanced versions of logistic regression and random forests. Its conclusions apply to this limited sample, not all chess games.

## Site

GitHub Pages builds the site from the repository root. `_config.yml` sets the project-site base URL to `/data-science-portfolio`. `_layouts/default.html` and `assets/css/style.css` provide the shared design; `assets/css/chess.css` adds styles only to the chess page. `resume.pdf` is the downloadable resume.

## AI transparency

Project 2 used OpenAI Codex with GPT-6 Astra for substantive assistance with planning, code generation, debugging, execution, figures, interpretation, writing, and website integration. The project page and notebook disclose that assistance. The results were calculated from the saved data; they were not invented. Project 1 retains its separate disclosure.
