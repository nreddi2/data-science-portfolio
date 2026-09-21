# Data Science Portfolio

This repository is a GitHub Pages portfolio for DTSC 2301. It uses the `jekyll-theme-minimal` theme required in the uploaded course instructions and contains a reproducible project about wage and salary income differences in North Carolina.

## Files you will edit personally

* `index.md`: review the About Me section and add a resume only if you want one public.
* `blog/blog1.md`: replace the reflection placeholder with your own writing.
* `gender-wage-gap.md`: run the notebook, then replace the three bracketed findings with your actual results.
* Add your own resume only if you want it public, and add the link on `index.md`.

## Run the analysis in simple steps

1. Create a free Census API key at https://api.census.gov/data/key_signup.html. Keep the key private; never paste it into a public GitHub file.
2. Download this repository or open it in GitHub Codespaces/Jupyter on your computer.
3. Open a terminal in this folder and install the packages: `python -m pip install -r requirements.txt`.
4. Start Jupyter: `jupyter lab`.
5. Open `analysis/gender_wage_gap_analysis.ipynb` and put your key into the `CENSUS_API_KEY` variable in the first code cell. Do not save or commit the notebook with the real key.
6. Choose **Run > Run All Cells**. The notebook creates `data/cleaned_north_carolina_wages.csv` and two PNG charts in `assets/images/`.
7. Read the printed summary table. Copy only the actual values into the bracketed findings on `gender-wage-gap.md`.
8. Commit/upload the changed notebook, page, and two chart PNG files to GitHub.

## Site organization

The files match the structure in the course instructions:

```text
index.md                 homepage
_config.yml              GitHub Pages and Minimal theme settings
projects.md              project index
gender-wage-gap.md       complete DTSC 2301 project page
blog.md                  blog index
blog/blog1.md            first reflection
analysis/                reproducible Jupyter notebook
assets/images/           chart placeholders and generated charts
```

## Publish the website with GitHub Pages

1. On GitHub, open the `data-science-portfolio` repository.
2. Select **Settings**, then **Pages** in the left sidebar.
3. Under **Build and deployment**, choose **Deploy from a branch**.
4. Choose the `main` branch and the `/ (root)` folder, then press **Save**.
5. Wait one or two minutes and refresh the Pages screen. GitHub displays the live address.

For a repository named `data-science-portfolio` owned by `nreddi2`, the normal project-site address is:

`https://nreddi2.github.io/data-science-portfolio/`

That is the expected address. You do not configure it to become `https://nreddi2.github.io/` unless you create a separate repository named exactly `nreddi2.github.io`; that separate repository is called a user site.

## Academic integrity and AI

AI assisted with an initial project structure and code draft. The student must run and verify the analysis, replace every placeholder with personally checked work, and follow the course's policy on AI use.
