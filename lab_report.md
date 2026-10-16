# Weekly Excess Mortality: Geospatial-Temporal Lab

## Research question
How did excess mortality vary across countries and over time from 2020 to mid-2022, and how do population size, reporting coverage, and geographic distribution affect interpretation?

## Dataset verification and preparation
The supplied Economist CSV contains **5,770 rows and 17 source columns**, covering **46 countries** and **46 regions**. Dates run from 2019-12-28 to 2022-07-17; ISO labels run from 2020-W01 to 2022-W29. No source fields are missing, duplicate country-region-week records are zero, and `excess_deaths` matches `total_deaths - expected_deaths` to maximum absolute floating-point residual 5.4e-11. Population is constant within each country.

All 46 records sets are national-level (`region == country`); no subnational rows were found. The requested interval is **2020-W01 through 2021-W52 = 104 weeks**. ISO year 2020 contains W53, but W53 is outside the stated end of the selected range; it is kept in the full dataset and excluded from this assignment period. Forty-three countries had all 104 weeks (4,472 country-week rows); Guatemala, Montenegro, and Tunisia were excluded from balanced-panel analyses because coverage was incomplete. Missing weeks are not treated as zero.

Source `start_date` is not always the Monday of its stated ISO week: **378 rows** differ, in Britain (131), Canada (113), and South Africa (134). For alignment, the analysis derives `week_start` from ISO year/week, rather than trusting those inconsistent date labels. The first four analytical fields are `country`, ISO year/week (`year`, `week`), `excess_deaths`, and `excess_deaths_pct_change`; they identify geography, align time, measure count burden, and measure proportional burden.


## Results summary

| Finding | Calculated result |
|---|---|
| Source coverage | 5,770 rows, 17 columns; 46 countries; 2020-W01–2022-W29 |
| National-level countries | 46 |
| Balanced-panel countries | 43 |
| Valid weeks per panel country | 104 |
| Balanced-panel records | 4,472 |
| Top three weekly peaks | 2021-W01 (89,072); 2021-W02 (96,356); 2021-W03 (98,673) |
| Highest cumulative excess | United States: 980,150 |
| Lowest cumulative excess | New Zealand: -2,665 |
| Countries with negative cumulative excess | New Zealand |
| Mapped / eligible countries | 42 / 43 |
| Boundary-unmatched countries | Malta |

## Task 1 — Explore the data

**Question 1: Which countries have subnational rows, and how did you find them?**  
None. I compared each row’s `region` and `country`; they are equal for all 5,770 records.

**Question 2: Which 3–4 columns will you use most, and why?**  
`country` identifies each series, `year` and `week` define ISO time, `excess_deaths` measures the weekly difference in deaths, and `excess_deaths_pct_change` puts that difference relative to expected deaths.

## Task 2 — Prepare the data
Dates were parsed as datetimes, ISO weeks reconstructed using Monday-based dates, and a month field assigned from the month containing that Monday. A week crossing a calendar-month boundary therefore belongs wholly to its Monday’s month. This is consistent, but it is a calendar convention rather than a daily allocation.

**Question 1: Why must the week be a date for a time axis?**  
A real date sorts weeks chronologically, places gaps and year boundaries correctly, and spaces observations by elapsed time. It also avoids treating W01 from different years as the same point and handles ISO week 53 explicitly.

**Question 2: What would go wrong if you skipped the national-row filter or the consistent-panel filter?**  
Mixing national and subnational totals could count the same deaths twice; this file has no subnational rows, but the equality filter still verifies level. Summing countries with different coverage could make aggregate rises or falls reflect countries entering or leaving rather than mortality changes, so the weekly aggregate uses the same 43 complete countries.

## Task 3 — Temporal patterns
The balanced-panel aggregate’s three highest weekly totals are **2021-W01: 89,072; 2021-W02: 96,356; 2021-W03: 98,673 deaths**. All three occur in January 2021. This fixed-country sum improves week-to-week comparability but represents only 43 of 46 countries in the file, not the world. Ties would appear as separate rows in the ranked peak table; these three totals are distinct. Country-level peaks are not synchronized: the largest country-specific maximum is Mexico (2021-W03, 28,234), followed by the United States (2020-W53, 24,931) and South Africa (2021-W02, 15,629). The US 2020-W53 peak is from the full country series and is outside the aggregate panel’s selected interval.

**Question 1: When were the main waves, and did every country peak at the same time?**  
The selected panel’s highest totals cluster in 2021-W01–W03. No: individual maxima differ, including Spain and Italy in March 2020, the United States in 2020-W52, Mexico in 2021-W03, and Iran in August 2021 (2021-W34). These are maxima in the data, not necessarily each country’s only mortality wave.

**Question 2: What events could explain the peaks?**  
The January 2021 cluster coincides with the documented winter 2020–21 COVID-19 high-transmission period in the United States; later 2021 peaks coincide in time with periods often described as Delta waves. Those historical associations make pandemic activity a plausible context, but this chart cannot establish the cause of any country’s mortality peak. Excess mortality can reflect direct and indirect pandemic effects, as well as unrelated changes in mortality.

**Question 3: When is excess mortality higher than reported COVID-19 mortality in the selected country, and what might explain the gap?**  
For the United States, weekly excess deaths exceed reported COVID-19 deaths in 87 of 128 available weeks, with such weeks spanning 2020-02-24 to 2022-06-06; the largest weekly gap is about 10,240 in 2021-W34. The difference could reflect incomplete attribution/reporting, indirect pandemic effects, the modeled expected baseline, or other mortality changes; it is not a count of deaths proven to have been caused by COVID-19.

## Task 4 — Geographic distribution
The choropleth maps the **43 countries with complete 2020-W01–2021-W52 coverage**; 42 matched Natural Earth boundaries, and **Malta** did not match the boundary dataset. Highest absolute totals: United States: 980,150 (290.8/100k); Mexico: 609,900 (481.4/100k); Iran: 256,220 (291.4/100k); South Africa: 232,509 (391.5/100k); Peru: 184,194 (546.3/100k). New Zealand is the only negative cumulative total (-2,665; -52.0 per 100,000). By rate, the largest values are Bulgaria: 869.5/100k; Lithuania: 621.6/100k; Romania: 584.2/100k; Peru: 546.3/100k; Mexico: 481.4/100k. Rankings therefore change when population is considered. The map covers only countries in this dataset; the absent countries cannot be exhaustively enumerated without selecting a world-country reference universe, and 46 reporting countries are not a global sample.

**Question 1: Which countries and regions stand out, and which have negative excess?**  
The United States has the largest absolute cumulative excess, followed by Mexico, Iran, South Africa, and Peru. New Zealand alone has a negative cumulative value; population adjustment places Bulgaria and Lithuania above the United States in cumulative excess per 100,000, showing that count and rate answer different questions.

**Question 2: Which countries are missing from the dataset entirely, and how does that limit a global interpretation of the map?**  
The dataset itself includes only 46 countries, so all countries outside that supplied list are absent; a complete named list depends on which world-country standard is used. Separately, Malta is present in the dataset but unmatched to the selected boundary file. The map is therefore a comparison of reporting countries, not a complete global picture.

## Task 5 — Space and time
The heat map calculates monthly excess ratio as `(sum(total_deaths) - sum(expected_deaths)) / sum(expected_deaths)`, using each week’s Monday month. It uses 43 complete countries and a color scale centered at zero; missing values remain masked. This weighted ratio follows the dataset’s definition of weekly excess as observed minus expected over expected, and avoids the bias of a simple mean of weekly ratios.

**Question: How did the high-excess areas move between waves, and why did you choose this visualization design over the other two?**  
The heat map shows high-excess periods shifting across countries rather than a single uniform global wave: western European maxima occur early in 2020, while Mexico, South Africa, and many other series peak around late 2020/early 2021, with Iran’s maximum later in 2021. A heat map is readable as a static report figure and allows direct country-month comparison with one consistent scale; unlike small-multiple maps it does not require readers to match changing country shapes, and unlike animation it preserves every month in a printable image.

## Normalization, limitations, and conclusion
Absolute excess deaths emphasize populous countries. Per-100,000 rates and the ratio to expected deaths change comparisons because they scale by population or baseline mortality. They are not interchangeable: per-capita rate measures burden relative to population, while excess/expected measures deviation relative to usual deaths. Excess mortality also is not the same as reported COVID-19 deaths and does not prove that every excess death was pandemic-caused.

The data are a limited set of countries, include an expected-deaths model, and have source date-label inconsistencies for three countries. The 2020–2021 balanced period excludes three incomplete country series and excludes 2020-W53 by the assignment’s literal endpoint. Results are descriptive, not causal. The defensible conclusion is that excess deaths varied substantially in both timing and relative intensity, and that common-panel aggregation plus normalized country comparisons reveal different patterns than raw counts alone.

## References
- The Economist, *COVID-19 excess deaths tracker* data and source code (dataset attribution; CC BY 4.0): [GitHub repository](https://github.com/TheEconomist/covid-19-excess-deaths-tracker).
- US CDC, *Trends in Disease Severity and Health Care Utilization During the Early Omicron Variant Period Compared with Previous SARS-CoV-2 High Transmission Periods* (period labels for winter 2020–21 and Delta): [MMWR](https://www.cdc.gov/mmwr/volumes/71/wr/mm7104e4.htm).
- WHO, *Methods for estimating the excess mortality associated with the COVID-19 pandemic* (excess mortality and limits of reported COVID-19 deaths): [WHO methodology](https://www.who.int/publications/m/item/methods-for-estimating-the-excess-mortality-associatedwith-the-covid-19-pandemic/).
- Natural Earth, 1:110m country boundaries (mapping boundaries): [GeoJSON repository](https://github.com/nvkelso/natural-earth-vector).

## Reproducibility
Keep the provided CSV next to the notebook and Python script, or change `CSV` to its path. Install `pandas`, `numpy`, `matplotlib`, `seaborn`, and `geopandas` with pip; the choropleth also needs internet access to fetch the boundary GeoJSON. Run all cells in Jupyter Notebook or JupyterLab. The analysis script saves the PNG figures and CSV result tables in the same folder.
