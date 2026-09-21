---
layout: default
title: Gender Wage Gap Project
---

# Exploring Gender Inequality in Wages in North Carolina

## Project summary

Wage inequality affects economic security and opportunity. This exploratory data analysis examines reported wage and salary income among working-age North Carolina residents using 2024 ACS 1-Year PUMS person-level survey data. It is descriptive: it identifies patterns in the sample and does not prove that gender causes a pay difference.

## Research questions

1. How does annual wage and salary income differ between men and women in North Carolina?
2. Does the observed wage and salary income gap vary by educational attainment?

## Data source and collection

The data source is the U.S. Census Bureau's **2024 ACS 1-Year PUMS API**. PUMS is a survey microdata file: each record represents a sampled person, not a complete administrative payroll record. The API request is limited to North Carolina (`state:37`). The notebook requests these fields:

| Field | Meaning | Use in this project |
|---|---|---|
| `AGEP` | Age | Restrict to ages 25-64 |
| `SEX` | Sex code reported in ACS | Comparison group |
| `WAGP` | Wage or salary income in the past 12 months | Outcome variable |
| `SCHL` | Educational attainment code | Education group |
| `WKHP` | Usual hours worked per week | Work-pattern context |
| `WKWN` | Weeks worked during the past 12 months | Work-pattern context |
| `PWGTP` | Person survey weight | Weighted descriptive statistics |

The API is documented by the Census Bureau, and the 2024 PUMS data dictionary defines the codes used in the analysis. The notebook stores a local raw-data snapshot only after you run it; it does not include data in this repository by default.

## Data cleaning and preparation

The analysis code:

1. Downloads the selected fields through the Census API.
2. Converts API text fields to numeric values and checks for missing or invalid values.
3. Keeps people ages 25-64 with positive wage/salary income and valid sex, education, hours, weeks, and person-weight values.
4. Replaces ACS education codes with readable education groups.
5. Calculates weighted medians and weighted means using `PWGTP`.
6. Saves a reproducible cleaned-data file and two chart images in `assets/images/`.

Keeping only positive wage/salary income makes the wage comparison easier to interpret, but it also means the project does not describe people with no wage income. That choice is documented in the code and should be discussed when presenting results.

## Visualizations and findings

The notebook creates two required visualizations:

1. A weighted median annual wage/salary-income comparison by sex.
2. A weighted median annual wage/salary-income comparison by sex and educational attainment.

Run the notebook before submitting, then replace the statements below with the values that the notebook prints. Do not make up values.

* **Overall result:** [After running the notebook, state the weighted median wage/salary income for women and men and the dollar difference.]
* **Education result:** [State which education group has the largest and smallest observed difference, using the chart/table output.]
* **Interpretation:** [Briefly explain what the descriptive results suggest, without claiming causation.]

![Weighted median wage and salary income by reported sex](assets/images/figure1_wages_by_sex.png)

*Figure 1. Replace this placeholder automatically by running the notebook; it writes `weighted_median_wages_by_sex.png`.*

![Weighted median wage and salary income by education and reported sex](assets/images/figure2_wages_by_education.png)

*Figure 2. Replace this placeholder automatically by running the notebook; it writes `weighted_median_wages_by_education.png`.*

## Limitations and ethics

* **Sex is not gender identity.** ACS `SEX` is a binary survey variable. It cannot represent every gender identity, so this project should not be described as a complete analysis of all gender identities.
* **No causal claim.** Differences may reflect occupation, industry, work experience, job tenure, discrimination, caregiving, hours, weeks worked, and other variables not adjusted for here.
* **Income measure.** `WAGP` captures wages and salaries in the prior 12 months, not total compensation, hourly pay, self-employment income, or benefits.
* **Survey uncertainty.** PUMS uses a sample and survey weights. Weighted summaries improve population representation but do not eliminate sampling error or response error.
* **Privacy and respect.** The project uses public, de-identified Census microdata. Results are reported as group summaries, not as claims about any individual or about the abilities of people in a group.
* **Reproducibility.** The exact result can change if the API data, filter rules, or software versions change. The notebook documents the request and transformation steps.

## Code and AI transparency

The reproducible notebook is available here: [gender_wage_gap_analysis.ipynb](analysis/gender_wage_gap_analysis.ipynb). It downloads data, cleans it, calculates weighted summaries, and creates the charts.

**AI disclosure:** Generative AI was used as a drafting and coding aid to help organize the project page and create a starting analysis workflow. I am responsible for reviewing the code, running the analysis, verifying every result, revising the written interpretation, and citing sources. No numerical result in this page was produced or approved without running the code.

## References

1. U.S. Census Bureau. (2024). *American Community Survey 1-Year Public Use Microdata Sample API.* https://www.census.gov/data/developers/data-sets/census-microdata-api/acs-1y-pums.html
2. U.S. Census Bureau. (2024). *2024 ACS PUMS data dictionary.* https://www.census.gov/programs-surveys/acs/microdata/documentation/2024.html
3. Blau, F. D., & Kahn, L. M. (2017). The gender wage gap: Extent, trends, and explanations. *Journal of Economic Literature, 55*(3), 789-865. https://doi.org/10.1257/jel.20160995
4. Goldin, C. (2014). A grand gender convergence: Its last chapter. *American Economic Review, 104*(4), 1091-1119. https://doi.org/10.1257/aer.104.4.1091
5. England, P. (2010). The gender revolution: Uneven and stalled. *Gender & Society, 24*(2), 149-166. https://doi.org/10.1177/0891243210361475

## How to reproduce this project

See the [repository README](README.md) for beginner-friendly instructions. You will need a free Census API key and Python with Jupyter installed. Run the notebook from top to bottom; then update the three bracketed findings above with your actual output.
