# Marketing Campaign Response Analysis (SQL + Python + Streamlit)

**Which customers accept a marketing campaign, and who should we target next?**
I cleaned a real customer dataset, answered 15 business questions with **SQL**, and built an interactive **Streamlit dashboard** that turns the findings into targeting recommendations.

**Live dashboard:** _paste your Streamlit link here_

![What drives response](charts/response_drivers.png)

## Dataset
Kaggle "Customer Personality Analysis": 2,240 customers of a food and wine retailer (joined 2012-2014) with demographics, spend per product category, purchases per channel, and whether each customer accepted 6 marketing campaigns.
`Response` = accepted the **last** campaign (14.9% of customers did).

## Data cleaning (`src/clean.py`)
| Problem found | Fix |
|---|---|
| Join dates in two formats; spreadsheet had swapped day and month for some rows (dates ran to Dec 2014 although the data ends Jun 2014) | Parsed both formats, swapped back; range is now 2012-07-30 to 2014-06-29 |
| 4 rows with invalid Marital_Status ("Absurd", "YOLO"); "Alone" duplicates "Single" | Removed 4 rows; merged "Alone" into "Single" |
| 3 impossible birth years (1893, 1899, 1900) | Removed |
| 1 income outlier (666,666 vs median about 51,000) | Removed |
| 24 missing Income values | Filled with median income of the same education group |
| Constant columns (Z_CostContact, Z_Revenue) | Dropped |

Result: 2,240 to 2,232 rows. Added features: Age, Age_Group, Total_Spend, Total_Purchases, Children, Prev_Campaigns_Accepted, Tenure_Days, Income_Group (quartiles), Recency_Band.

## Key findings (all from the SQL queries in `sql/queries.sql`)
1. **Past behaviour is the strongest signal.** Customers who accepted no earlier campaign responded at 8.2%; with 1 earlier acceptance, 31.2%; with 2, 50.0%; with 3 or more, about 80-90% (the 4-campaign group has only 11 customers).
2. **Income, children and recency matter.** Top income quartile: 26.7% (other quartiles 10-12%). No children: 26.5% vs about 10% with one or two. Bought in the last 24 days: 26.5% vs 7.5% at 75-99 days.
3. **A concrete target profile:** high income + no children + active in the last 50 days = **190 customers (8.5% of the base) with a 45.3% response rate vs 12.0% for everyone else**, and about 2.8x the average spend.
4. **Responders are more valuable.** Average total spend 988 vs 539 (1.8x); they also buy about 1.8x more through the catalog.
5. **Spend is concentrated.** The top 10% of customers make about 30% of total spend and the top 20% about 52%. Wine and meat are about 78% of all spend.
6. Complaints made no difference to response (15.0% vs 14.9%, but only 20 complainers).

![Spend concentration and target profile](charts/spend_and_target_profile.png)

## Recommendations
- Build the next campaign list from customers who accepted earlier campaigns, then the high-income / no-children / recently active profile.
- Use catalog and web for high-value responders, and lead with wine and meat offers.
- Spend less on customers inactive 75+ days (7.5% response); test a cheaper win-back offer instead.
- Run the next campaign as a **test**: contact the profile group vs a random group, so the lift can be measured properly.

## Limitations (what this analysis cannot say)
- These are patterns in past data, not proof of cause.
- The target profile (finding 3) was chosen after exploring this same data, so the 45.3% is likely optimistic. It is a hypothesis for a test campaign.
- No cost or revenue per campaign in the data, so ROI cannot be calculated.
- Only one campaign (the last) is used as the outcome; single retailer, 2012-2014 data.
- Some groups are small (for example 3 children: 53 customers). Marital status differences were not checked for overlap with income or other factors.

## Tech stack
Python (pandas, matplotlib, Plotly), SQL (SQLite, including CTEs, window functions and UNION), Streamlit.

## Project structure
```
app.py                       Streamlit dashboard (4 tabs, filters, SQL explorer)
sql/queries.sql              15 SQL queries, each with the business question
src/clean.py                 Cleaning and feature engineering
src/build_db.py              Loads clean data into SQLite (data/marketing.db)
src/sql_utils.py             Reads queries.sql and runs them
src/analysis.py              Runs all queries, saves results and charts
results/query_results.md     Every query with its output
charts/                      Charts used in this README
data/                        Raw CSV, clean CSV, SQLite database
```

## Run it yourself
```bash
pip install -r requirements.txt
python src/clean.py
python src/build_db.py
python src/analysis.py
streamlit run app.py
```

## Deploy (free)
1. Push this folder to a GitHub repository.
2. Go to share.streamlit.io, sign in with GitHub, choose the repo, set the main file to `app.py`, and deploy.
3. Paste the live link at the top of this README and on your resume.

_Dataset credit: Kaggle, "Customer Personality Analysis"._
