---
layout: default
title: Wage Income in North Carolina
description: An analysis of annual wage and salary income using 2024 ACS PUMS data.
permalink: /projects/wage-income-north-carolina/
page_class: content-page prose
---

<span class="eyebrow">Project 01 · </span>

<p class="lede">A 2024 American Community Survey PUMS analysis of annual wage and salary income across education, age, and selected occupations.</p>

## Problem definition

My starting question was: “How does the gender pay gap change depending on factors such as education level, age, occupation, or years of work experience?” Due to the available Census data I decided to revise it to a narrower, measurable question:

> Among North Carolina residents ages 25–64 with positive wage and salary income, how does weighted median annual wage income differ by reported sex across education, age, and selected occupations?


<div class="draft-prompt"><light></light> The gender pay/wage gap has been a long standing gender inequality historically. Even today, it seems that this inequality continues to be prevalent. However, nowadays there is a lot more awareness about these topics, and there are rules and regulations put in place so that these injustices can be avoided to a better extent. I wanted to seek out these issues and find whether these gender inequalities seem to be as prevalent, and also see if certain other factors, such as an occupation, actually lead to different disparity levels of wages in the workforce.

</div>

## Data description

The data comes from the U.S. Census Bureau’s [2024 ACS 1-Year PUMS API](https://api.census.gov/data/2024/acs/acs1/pums.html). Since I decided to narrow the results for North Carolina residents, the data was queried for North Carolina (`state:37`). Each row is one sampled person. It should be noted that PUMS is a survey sample, so it is not a complete list of employee payroll records. [2024 PUMS data dictionary](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2024.pdf) defines each variable and its codes.

The dataset contains 114,270 unweighted North Carolina person records. That number is the size of the downloaded sample, not the number of North Carolina residents. So after the age and positive-wage restrictions (that will be further expanded on in the next section), **41,436 records** remain. I use the Census person weight `PWGTP` to calculate medians intended to describe people rather than treating every sampled record as equally representative. The record counts shown beside my charts are still unweighted counts.

| Detail | Value |
|:--|:--|
| Source | U.S. Census Bureau, 2024 ACS 1-Year PUMS person records |
| Geography | North Carolina residents |
| Unit of analysis | One sampled person |
| Downloaded rows | 114,270 |
| Rows after filters | 41,436 |
| Missing values in API response | 46,413 each in `OCCP` and `INDP`; zero blanks in the other requested fields |

| Concept | Census field | Operational definition in this project |
|:--|:--|:--|
| Reported sex | `SEX` | Census categories 1 and 2, displayed as men and women. This is not a direct measure of gender identity. |
| Annual wage income | `WAGP` + `ADJINC` | Wage and salary income in the prior 12 months, adjusted to constant 2024 dollars. The API returned `ADJINC` as a decimal multiplier (1.015250); the Census bulk CSV expresses the same factor with six implied decimal places (1015250). |
| Educational attainment | `SCHL` | Four groups: high school or less (01–17), some college or associate degree (18–20), bachelor’s (21), graduate or professional (22–24). |
| Age | `AGEP` | Ages 25–64, shown in four ten-year groups. |
| Work pattern | `WKHP`, `WKWN` | Usual hours per week and weeks worked during the past 12 months. These describe work time, not career experience. |
| Occupation | `OCCP` | Six common occupation codes with at least 100 unweighted records for each sex in the analytic sample; labels checked against the 2024 Census dictionary. |
| Industry | `INDP` | Downloaded for context but not analyzed in the current research question. |
| Survey weight | `PWGTP` | Person weight for weighted descriptive estimates. |

The ACS does not provide a direct measure of **years of work experience**. Age is not a substitute for experience. Because annual income also depends on the amount of time worked, the project does not interpret its annual-income comparisons as equal-pay-for-equal-work estimates.

## Data cleaning and preparation

The [analysis notebook](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/wage_income_acs_2024.ipynb) shows the API request, missing-value counts, a step-by-step filter log, the income adjustment, and the group summaries. The analytic sample keeps records with ages 25–64, positive wage income, valid education and sex codes, a positive person weight, and a positive income adjustment factor.

```python
df["wage_2024"] = df["WAGP"] * df["income_adjustment"]
```

The notebook creates `income_adjustment` after checking whether `ADJINC` arrived as a decimal multiplier or with six implied decimal places. This follows the Census documentation for [`WAGP`](https://api.census.gov/data/2024/acs/acs1/pums/variables/WAGP.json) and [`ADJINC`](https://api.census.gov/data/2024/acs/acs1/pums/variables/ADJINC.json). An initial API run applied the bulk-CSV scale to an already-decimal API value and produced dollar amounts near zero. Comparing a raw API row with the official bulk file exposed that error; the corrected notebook now checks the scale before calculating income. The four charts below were regenerated from the corrected data, not taken from that initial output.

| Cleaning step | Records remaining | Removed at step |
|:--|--:|--:|
| Downloaded North Carolina person records | 114,270 | — |
| Keep ages 25–64 | 55,533 | 58,737 |
| Keep valid `SEX` and `SCHL` codes | 55,533 | 0 |
| Keep positive `WAGP` | 41,436 | 14,097 |
| Keep positive `ADJINC` and `PWGTP` | 41,436 | 0 |

The API represents some inapplicable numeric fields as zero rather than blank. Thus, the zero blank counts for `WAGP`, `WKHP`, and `WKWN` do **not** mean every respondent worked or had wage income. The 46,413 blank occupation and industry entries are preserved as missing; these fields are used only for the selected-occupation comparison. The core sample excludes 72,834 records in total, mostly because of the age restriction and zero/nonpositive wage income.

<div class="draft-prompt"><strong>Your writing:</strong> Explain why you kept people with positive wage income in the past 12 months and whom that choice excludes. Describe one real choice you made while checking the corrected output.</div>

## Data understanding and visualizations

The corrected notebook produced four charts with titles, units, readable labels, and the underlying group counts. Each chart uses the person survey weight. Dollar and percentage gaps are calculated from the two group medians; they are descriptive comparisons, not paired differences or causal effects. The tables below report exact computed medians to two decimal places, while the chart labels are rounded for readability. Record counts are **unweighted**.

### Figure 1 · Overall comparison

<figure>
  <img src="{{ '/assets/images/figure1_overall.png' | relative_url }}" alt="Bar chart of weighted median annual wage income: men $60,915 and women about $45,686.">
  <figcaption>Figure 1. Weighted median annual wage and salary income in 2024 dollars among the 41,436 included records. Men: $60,915.00 (21,164 records); women: $45,686.25 (20,272 records). The difference between medians is $15,228.75, or 25.0% of the men's median.</figcaption>
</figure>

<div class="draft-prompt"><strong>Your writing:</strong> State the men’s and women’s weighted medians, the dollar difference, and the percentage difference. Explain what the chart directly shows in two or three sentences.</div>

### Figure 2 · Education groups

<figure>
  <img src="{{ '/assets/images/figure2_education.png' | relative_url }}" alt="Dumbbell plot of weighted median annual wage income for men and women in four education groups; the plotted gap percentages are 29, 27, 30, and 33 percent.">
  <figcaption>Figure 2. Weighted median annual wage income by educational attainment and reported sex. The right-hand labels show the gap as a percentage of the men's median within each education group.</figcaption>
</figure>

| Education group | Men’s median | Women’s median | Men’s records | Women’s records |
|:--|--:|--:|--:|--:|
| High school or less | $42,640.50 | $30,457.50 | 6,542 | 4,018 |
| Some college or associate degree | $54,823.50 | $40,102.38 | 5,762 | 5,983 |
| Bachelor’s degree | $81,220.00 | $56,854.00 | 5,551 | 5,946 |
| Graduate or professional degree | $106,601.25 | $71,067.50 | 3,309 | 4,325 |

<div class="draft-prompt"><strong>Your writing:</strong> Compare at least two education groups using exact values from the notebook. Explain whether the gap grows, shrinks, or varies irregularly across the groups. Describe one pattern you did not expect.</div>

### Figure 3 · Age groups

<figure>
  <img src="{{ '/assets/images/figure3_age.png' | relative_url }}" alt="Line chart of weighted median annual wage income by age group, with one line each for men and women. The plotted groups run from ages 25–34 to 55–64.">
  <figcaption>Figure 3. Weighted median annual wage income by age group and reported sex. The 25–34 group has 5,653 men’s records and 5,167 women’s records; the 35–44 group has 5,398 and 5,161; the 45–54 group has 5,140 and 5,096; and the 55–64 group has 4,973 and 4,848.</figcaption>
</figure>

| Age group | Men’s median | Women’s median | Difference between medians |
|:--|--:|--:|--:|
| 25–34 | $49,747.25 | $41,625.25 | $8,122.00 |
| 35–44 | $63,960.75 | $49,747.25 | $14,213.50 |
| 45–54 | $65,991.25 | $50,762.50 | $15,228.75 |
| 55–64 | $63,960.75 | $45,686.25 | $18,274.50 |

<div class="draft-prompt"><strong>Your writing:</strong> Name the age groups with the smallest and largest observed differences, with exact values. Say why age alone cannot establish years of work experience.</div>

### Figure 4 · Selected occupations

The occupation chart shows six common occupations that have at least 100 unweighted records for men and for women after all core filters. This is a selection rule, not a claim that these six represent every occupation. Some groups still have modest sample sizes, and no margin of error is calculated.

<figure>
  <img src="{{ '/assets/images/figure4_occupation.png' | relative_url }}" alt="Horizontal bar chart comparing weighted median annual wage income for men and women in six selected occupations.">
  <figcaption>Figure 4. Weighted median annual wage income in six selected occupations. The percent labels compare the two medians within each code; they do not adjust for job duties or work schedules.</figcaption>
</figure>

| Occupation | Men’s median | Women’s median | Men’s records | Women’s records |
|:--|--:|--:|--:|--:|
| Other managers | $101,525.00 | $78,174.25 | 890 | 631 |
| Registered nurses | $76,143.75 | $72,082.75 | 121 | 958 |
| Elementary/middle school teachers | $51,777.75 | $49,442.68 | 133 | 898 |
| Driver/sales workers and truck drivers | $52,793.00 | $25,381.25 | 793 | 106 |
| First-line retail sales supervisors | $60,915.00 | $40,610.00 | 431 | 333 |
| Customer service representatives | $47,107.60 | $37,056.63 | 250 | 503 |

<div class="draft-prompt"><strong>Your writing:</strong> Compare two occupations with exact values and group counts. Explain why a difference within an occupation code is not automatically a comparison of identical jobs, seniority, schedules, or responsibilities.</div>

## Work-time sensitivity check

The notebook repeats the overall comparison for respondents who reported at least 35 usual work hours per week and 50 weeks worked in the past 12 months. This is a narrower descriptive comparison, not an hourly-wage estimate or a control for experience, seniority, or job duties.

In this restricted group, the weighted medians are $65,991.25 for men (17,382 records) and $54,823.50 for women (14,459 records). The difference between medians is $11,167.75, or 16.9% of the men's median.

<div class="draft-prompt"><strong>Your writing:</strong> Compare the 16.9% restricted-group gap with the 25.0% overall gap. Say what this change might suggest and what it still cannot explain.</div>

## Storytelling and interpretation

<div class="draft-prompt"><strong>Write this section yourself after reviewing the charts.</strong> Connect the four figures into one answer to your research question. Explain what is consistent across figures and what changes by group. State a conclusion the data support and one tempting conclusion they do not support. Use concrete numbers, and avoid saying that the study proves discrimination or equal pay for equal work.</div>

## Limitations, ethics, and reflection

These results depend on self-reported survey data and a person-level sample. The analysis uses `PWGTP` for weighted estimates but does not calculate margins of error with the PUMS replicate weights. `WAGP` excludes self-employment income and benefits. Annual earnings reflect both pay rates and time worked. The `SEX` field has only two categories. The occupation codes combine people with different job duties, schedules, and seniority; industry, caregiving, tenure, and direct career experience are not controlled for in the core charts. Results should not be used to judge individuals or claim that any group’s earnings reflect ability or effort.

<div class="draft-prompt"><strong>Your reflection:</strong> Describe a limitation that surprised you, how it changed your interpretation, and one follow-up analysis you would attempt with more time. This should be your own account of working through the data, not a generic summary.</div>

## Code and transparency

The full analysis is in the [2024 ACS PUMS Jupyter notebook](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/wage_income_acs_2024.ipynb). The [summary tables and filter audit](https://github.com/nreddi2/data-science-portfolio/tree/main/analysis/results) let readers check the numbers behind the figures. The public [GitHub repository](https://github.com/nreddi2/data-science-portfolio) contains this page, the charts, and the resume.

<div class="draft-prompt"><strong>AI DISCLAIMER:strong> AI (GPT Terra 5.6) was utilized in this project. AI provided guidance for the visualizations, aided in cleaning data, and also used to check and locate syntax errors in my code. It also helped with the formatting of my information and making the data look more presentable.</div>

## References

Blau, F. D., & Kahn, L. M. (2017). The gender wage gap: Extent, trends, and explanations. *Journal of Economic Literature, 55*(3), 789–865. https://doi.org/10.1257/jel.20160995

England, P. (2010). The gender revolution: Uneven and stalled. *Gender & Society, 24*(2), 149–166. https://doi.org/10.1177/0891243210361475

Goldin, C. (2014). A grand gender convergence: Its last chapter. *American Economic Review, 104*(4), 1091–1119. https://doi.org/10.1257/aer.104.4.1091

U.S. Census Bureau. (2024). *2024 American Community Survey 1-Year Public Use Microdata Sample API*. https://api.census.gov/data/2024/acs/acs1/pums.html

U.S. Census Bureau. (2024). *2024 ACS PUMS data dictionary*. https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2024.pdf

[← Back to projects]({{ '/projects/' | relative_url }})
