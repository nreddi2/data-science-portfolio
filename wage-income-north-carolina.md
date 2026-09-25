---
layout: default
title: Wage Income in North Carolina
description: An analysis of annual wage and salary income using 2024 ACS PUMS data.
permalink: /projects/wage-income-north-carolina/
page_class: content-page prose
---

<span class="eyebrow">Project 01 · </span>

<p class="lede">A 2024 American Community Survey PUMS analysis of annual wage and salary income across education, age, and selected occupations.</p>

September 19, 2026

## Problem definition

My starting question was: “How does the gender pay gap change depending on factors such as education level, age, occupation, or years of work experience?” Due to the available Census data I decided to revise it to a narrower, measurable question:

> Among North Carolina residents ages 25–64 with positive wage and salary income, how does weighted median annual wage income differ by reported sex across education, age, and selected occupations?


The gender pay/wage gap has been a long standing gender inequality historically. Even today, it seems that this inequality continues to be prevalent. However, nowadays there is a lot more awareness about these topics, and there are rules and regulations put in place so that these injustices can be avoided to a better extent. I wanted to seek out these issues and find whether these gender inequalities seem to be as prevalent, and also see if certain other factors, such as an occupation, actually lead to different disparity levels of wages in the workforce.


## Data description

The data comes from the U.S. Census Bureau’s [2024 ACS 1-Year PUMS API](https://api.census.gov/data/2024/acs/acs1/pums.html). Since I decided to narrow the results for North Carolina residents, the data was queried for North Carolina (`state:37`). Each row is one sampled person. It should be noted that PUMS is a survey sample, so it is not a complete list of employee payroll records. [2024 PUMS data dictionary](https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2024.pdf) defines each variable and its codes.

The dataset contains 114,270 unweighted North Carolina person records. That number is the size of the downloaded sample, not the number of North Carolina residents. So after the age and positive wage restrictions (that will be further expanded on in the next section), **41,436 records** remain. I use the Census person weight `PWGTP` to calculate medians intended to describe people rather than treating every sampled record as equally representative. The record counts shown beside my charts are still unweighted counts.

“Unweighted” means this is the number of rows returned, not an estimate of the number of people living in North Carolina. After applying the age, sex code, education code, positive wage, adjustment factor, and survey weight requirements described below, 41,436 records remained in the main analytic sample.

| Detail | Value |
|:--|:--|
| Source | U.S. Census Bureau, 2024 ACS 1-Year PUMS person records |
| Geography | North Carolina residents |
| Unit of analysis | One sampled person |
| Downloaded rows | 114,270 |
| Rows after filters | 41,436 |
| Missing values in API response | 46,413 each in `OCCP` and `INDP`; zero blanks in the other requested fields |

| Dataset feature (column) | Census field | Operational definition in this project |
|:--|:--|:--|
| Reported sex | `SEX` | Census categories 1 and 2, displayed as men and women. This is not a direct measure of gender identity. |
| Annual wage income | `WAGP` + `ADJINC` | Wage and salary income in the prior 12 months, adjusted to constant 2024 dollars. The API returned `ADJINC` as a decimal multiplier (1.015250); the Census bulk CSV expresses the same factor with six implied decimal places (1015250). |
| Educational attainment | `SCHL` | Four groups: high school or less (01–17), some college or associate degree (18–20), bachelor’s (21), graduate or professional (22–24). |
| Age | `AGEP` | Ages 25–64, shown in four ten-year groups. |
| Work pattern | `WKHP`, `WKWN` | Usual hours per week and weeks worked during the past 12 months. These describe work time, not career experience. |
| Occupation | `OCCP` | Six common occupation codes with at least 100 unweighted records for each sex in the analytic sample; labels checked against the 2024 Census dictionary. |
| Industry | `INDP` | Downloaded for context but not analyzed in the current research question. |
| Survey weight | `PWGTP` | Person weight for weighted descriptive estimates. |

The features in my downloaded dataset are the columns I requested from the API: age (AGEP), reported sex (SEX), wage and salary income (WAGP), the income adjustment factor (ADJINC), education (SCHL), occupation (OCCP), industry (INDP), usual weekly hours (WKHP), weeks worked (WKWN), and person survey weight (PWGTP). Each row contains these values for one sampled person. During cleaning, I also created new columns, including adjusted wage income (wage_2024), education group, and age group, from the original features. The dataset does not have a feature that directly measures years of work experience.

## Data cleaning and preparation

To start my preparation of the data, I started by requesting the selected person-level fields from the 2024 ACS PUMS API for North Carolina, loading the response into a pandas DataFrame. I saved the 114270 downloaded records as a raw .csv file.

The notebook (linked at the end) shows the API request, missing value counts, a filter log, the income adjustment, and the group summaries. The analytic sample keeps records with ages 25–64, positive wage income, valid education and sex codes, a positive person weight, and a positive income adjustment factor.



The notebook creates `income_adjustment` after checking whether `ADJINC` arrived as a decimal multiplier or with six implied decimal places. This follows the Census documentation for [`WAGP`](https://api.census.gov/data/2024/acs/acs1/pums/variables/WAGP.json) and [`ADJINC`](https://api.census.gov/data/2024/acs/acs1/pums/variables/ADJINC.json). An initial API run applied the bulk-CSV scale to an already-decimal API value and produced dollar amounts near zero. Comparing a raw API row with the official bulk file exposed that error; the corrected notebook now checks the scale before calculating income. The four charts below were regenerated from the corrected data, not taken from that initial output.

Next, I prepared the fields for analysis. The API returned values as text, so I used pandas to convert age, wage income, education and sex codes, hours worked, weeks worked, the income adjustment factor, and the person weight into numeric values. I treated empty strings and the inapplicable value N in the occupation and industry fields as missing. I then counted missing values before filtering the data. OCCP and INDP each had 46,413 missing or inapplicable entries; the other requested fields had no blank entries in this check. A zero is not the same as a blank, though. For example, a person can have WAGP recorded as zero because they had no wage income.

After inspecting those values, I applied my sample rules one at a time and recorded the number of rows each rule removed:

| Cleaning step | Records remaining | Removed at step |
|:--|--:|--:|
| Downloaded North Carolina person records | 114,270 | — |
| Keep ages 25–64 | 55,533 | 58,737 |
| Keep valid `SEX` and `SCHL` codes | 55,533 | 0 |
| Keep positive `WAGP` | 41,436 | 14,097 |
| Keep positive `ADJINC` and `PWGTP` | 41,436 | 0 |

These filters left 41,436 records for the main analysis and excluded 72,834 downloaded records. The age restriction focuses the project on the range named in my research question. The positive-wage restriction means I compare people who reported wage and salary income, rather than mixing their income values with those of people who had no wages. It also limits my conclusion: the results do not describe all North Carolina adults. I did not remove everyone with a missing occupation or industry, because I did not need those fields for the overall, education, or age comparisons. I used occupation only for the selected-occupation figure.

<div class="draft-prompt"> I then created the income measure used in the charts by multiplying WAGP by an income adjustment factor. This had to be done so that the income amounts are put on one common price scale. The ACS asks people about income over the past 12 months throughout the year, so some answers include income from 2023 as well as 2024. The Census provides ADJINC to adjust those amounts to a consistent 2024 scale. </div>

In the API response examined for this project, the factor appeared as a decimal multiplier such as 1.015250; the Census bulk file documentation represents the equivalent factor as 1015250, with six implied decimal places. An earlier calculation divided the already decimal value again and produced implausibly small incomes. This was a problem I had to tackle, so I chose to check the factor’s scale, then calculate wage_2024 with the following code. (The Census definitions of WAGP and ADJINC explain the adjustment)

```python
df["wage_2024"] = df["WAGP"] * df["income_adjustment"]
```

The API represents some inapplicable numeric fields as zero rather than blank. Therefore the zero blank counts for `WAGP`, `WKHP`, and `WKWN` do not actually mean every respondent worked or had wage income. The 46,413 blank occupation and industry entries are preserved as missing; these fields are used only for the selected occupation comparison. The core sample excludes 72,834 records in total. A lot of these omissions were from the age restriction, but also from filtering the wages. Positive wages were specifically filtered for so that any adults who do not work or gets their income from other sources would not be accounted for.

Finally, I replaced Census number codes with readable labels. I put education into four groups and ages into four ten-year groups. I saved the cleaned data and a list showing how many records each step removed, so I could check how I reached my final results.

## Data understanding and visualizations

The corrected notebook produced four charts with titles, units, readable labels, and the underlying group counts. Each chart uses the person survey weight. Dollar and percentage gaps are calculated from the two group medians; they are descriptive comparisons, not paired differences or causal effects. The tables below report exact computed medians to two decimal places, while the chart labels are rounded for readability. Record counts are unweighted.

### Figure 1 · Overall comparison

<figure>
  <img src="{{ '/assets/images/figure1_overall.png' | relative_url }}" alt="Bar chart of weighted median annual wage income: men $60,915 and women about $45,686.">
  <figcaption>Figure 1. Weighted median annual wage and salary income in 2024 dollars among the 41436 included records. Men: $60,915.00 (21,164 records); women: $45686.25 (20,272 records). The difference between medians is $15228.75, or 25.0% of the men's median.</figcaption>
</figure>

<div class="draft-prompt"> The men's weighted median was found to be $60915.00, while the woman's weighted median was $45686.25. The difference between the two medians is $15,228.75, which is equal to 25.0% of the men's median. the dollar difference, and the percentage difference. The chart shows an overall difference in annual wages among the included people. </div>

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

<div class="draft-prompt"><strong></strong> In all four education groups, the men's weighted median is found to be higher than the women's. At a high school level, the men's median was $42,640.50 and the women's was $30,457.50. This gap increases the higher you go in education, jumping up to $81,220.00 for men and $56,854.00 for women at a bachelor's degree and a $106,601.25 for men and $71,067.50 for women at a graduate/professional degree. It was interesting to find that the gap would increase as the education levels went higher; I honestly expected it to be more even at a higher level.</div>

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

<div class="draft-prompt">The smallest difference between medians is $8,122.00 at ages 25–34 ($49,747.25 men; $41,625.25 women). The largest difference is $18,274.50 at ages 55–64 ($63,960.75 men; $45,686.25 women). It should be noted that age isn't the same as job experience. People can enter work, switch fields, or take time away from work at different ages. </div>

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

<div class="draft-prompt"><strong></strong> The selected occupation codes show very different-sized differences. Elementary/middle school teachers: $51,777.75 men versus $49,442.68 women; 133 men's and 898 women's records; 4.5% gap. Driver/sales workers and truck drivers: $52,793.00 men versus $25,381.25 women; 793 men's and 106 women's records; 51.9% gap. It should be noted that a difference within an occupation code does not necessarily a comparison of identical jobs, schedules, or responsibilities. The chart doesn't show that two people in identical roles receive different pay.</div>

## Work-time sensitivity check

The notebook repeats the overall comparison for respondents who reported at least 35 usual work hours per week and 50 weeks worked in the past 12 months. This is a narrower descriptive comparison, not an hourly-wage estimate or a control for experience, seniority, or job duties.

In this restricted group, the weighted medians are $65,991.25 for men (17,382 records) and $54,823.50 for women (14,459 records). The difference between medians is $11,167.75, or 16.9% of the men's median.

The change tells me that the result is sensitive to who is included when I consider reported work time. I cannot necessarily conclude that working time caused the full change from 25.0% to 16.9%. Applying the restriction also selects a different set of people, who may differ in occupation, seniority, job duties, and other characteristics. The calculation still uses annual income rather than a direct hourly wage. I decided to present this check so that the interpretation is more careful, not to claim that I have fully explained the overall difference.


## Storytelling and interpretation

After analyzing the data, the men's weighted median was found to be higher in the overall sample and in every displayed education, age, and selected occupation group. This was nothing new, as some degree of wage gap between gender inequality was, truthfully, to be expected. However, the size of the difference does notably change per group: education gaps are about 26.9%–33.3%, age-group dollar gaps are about $8,122–$18,275, and selected occupations range from about 4.5% to 51.9%. Additionally, the full time/year round comparison was found to be smaller than the overall comparison (16.9% vs 25%).

## Limitations, ethics, and reflection

When I started this project, I had assumed that the dataset should be more than sufficient to form a conclusion and answer my research question. And for the purposes of the project it was; but I found this topic was a bit more difficult to pinpoint the more I researched this project. I think I underestimated the amount of confounding factors that come into play when conducting an analysis on a topic as complex as this, although I think I did my best given the original scope of the project and the dataset that I used.

Several limits affect how much can be concluded. First, these results depend on self reported survey data and a person level sample. This can mean that the data could have been susceptible to certain survey biases. Additionally, the analysis uses `PWGTP` for weighted estimates but does not calculate margins of error with the PUMS replicate weights. `WAGP` also excludes self-employment income and benefits. Annual earnings reflect both pay rates and time worked. The occupation codes combine people with different job duties, schedules, and seniority; and direct career experience, which are not controlled for in the core charts. So to summarize, there are many factors that can potentially be impacting the data and the findings that we might not know about and are difficult to control. So, the results should not be used to judge individuals or claim that any group’s earnings reflect ability or effort.

I would not say there really was a limitation that personally surprised me or changed the way I read a chart. If I were to do a follow-up analysis of this, I would probably try to include industry into the equation. Something interesting to note that definitely could matter is that two people who have the same occupation don't necessarily work in the same industry. I think that's another detail we can use and it could definitely have some useful real world implications. I could see it being helpful data to gather to raise awareness regarding gender disparities in certain industries. It could be very helpful for young women who seek to enter certain industries.

## Code and transparency

The full analysis is in the [2024 ACS PUMS Jupyter notebook](https://github.com/nreddi2/data-science-portfolio/blob/main/analysis/wage_income_acs_2024.ipynb). The [summary tables and filter audit](https://github.com/nreddi2/data-science-portfolio/tree/main/analysis/results) let readers check the numbers behind the figures. The public [GitHub repository](https://github.com/nreddi2/data-science-portfolio) contains this page, the charts, and the resume.

AI (GPT Terra 5.6) was utilized in this project. AI provided guidance for the visualizations, aided in cleaning data, created citations and also used to check and locate syntax errors in my code. It also helped with the formatting and layout of the information and making the data look more presentable.

## References

Blau, F. D., & Kahn, L. M. (2017). The gender wage gap: Extent, trends, and explanations. *Journal of Economic Literature, 55*(3), 789–865. https://doi.org/10.1257/jel.20160995

England, P. (2010). The gender revolution: Uneven and stalled. *Gender & Society, 24*(2), 149–166. https://doi.org/10.1177/0891243210361475

Goldin, C. (2014). A grand gender convergence: Its last chapter. *American Economic Review, 104*(4), 1091–1119. https://doi.org/10.1257/aer.104.4.1091

U.S. Census Bureau. (2024). *2024 American Community Survey 1-Year Public Use Microdata Sample API*. https://api.census.gov/data/2024/acs/acs1/pums.html

U.S. Census Bureau. (2024). *2024 ACS PUMS data dictionary*. https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2024.pdf

[← Back to projects]({{ '/projects/' | relative_url }})
