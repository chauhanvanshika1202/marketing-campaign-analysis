-- Marketing campaign analysis: SQL queries (SQLite)
-- Table: customers (one row per customer). Response = 1 if the customer accepted the LAST campaign.
-- Each query starts with a "-- name:" line, followed by a "-- question:" line.

-- name: 01_overall_response
-- question: How many customers did we contact and what share responded to the last campaign?
SELECT COUNT(*)                                   AS customers,
       SUM(Response)                              AS responders,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers;

-- name: 02_response_by_education
-- question: Which education level responds best?
SELECT Education,
       COUNT(*)                                   AS customers,
       SUM(Response)                              AS responders,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Education
ORDER BY response_rate_pct DESC;

-- name: 03_response_by_marital_status
-- question: Does marital status change the response rate?
SELECT Marital_Status,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Marital_Status
ORDER BY response_rate_pct DESC;

-- name: 04_response_by_income_group
-- question: How does response change across income quartiles?
SELECT Income_Group,
       COUNT(*)                                   AS customers,
       ROUND(AVG(Income), 0)                      AS avg_income,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Income_Group
ORDER BY avg_income;

-- name: 05_response_by_age_group
-- question: Which age group is most responsive?
SELECT Age_Group,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Age_Group
ORDER BY response_rate_pct DESC;

-- name: 06_response_by_children
-- question: Do customers with children respond differently?
SELECT Children,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Children
ORDER BY Children;

-- name: 07_response_by_recency
-- question: Are recently active customers more likely to respond?
SELECT Recency_Band,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Recency_Band
ORDER BY MIN(Recency);

-- name: 08_response_by_previous_campaigns
-- question: Do customers who accepted earlier campaigns respond again?
SELECT Prev_Campaigns_Accepted,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Prev_Campaigns_Accepted
ORDER BY Prev_Campaigns_Accepted;

-- name: 09_spend_responders_vs_non
-- question: How much more do responders spend than non-responders?
SELECT CASE Response WHEN 1 THEN 'Responder' ELSE 'Non-responder' END AS customer_type,
       COUNT(*)                         AS customers,
       ROUND(AVG(Income), 0)            AS avg_income,
       ROUND(AVG(Total_Spend), 0)       AS avg_total_spend,
       ROUND(AVG(MntWines), 0)          AS avg_wine_spend,
       ROUND(AVG(MntMeatProducts), 0)   AS avg_meat_spend
FROM customers
GROUP BY Response;

-- name: 10_channel_mix_by_response
-- question: Which purchase channel do responders use most?
SELECT CASE Response WHEN 1 THEN 'Responder' ELSE 'Non-responder' END AS customer_type,
       ROUND(AVG(NumWebPurchases), 2)     AS avg_web,
       ROUND(AVG(NumCatalogPurchases), 2) AS avg_catalog,
       ROUND(AVG(NumStorePurchases), 2)   AS avg_store,
       ROUND(AVG(NumDealsPurchases), 2)   AS avg_deals,
       ROUND(AVG(NumWebVisitsMonth), 2)   AS avg_web_visits_month
FROM customers
GROUP BY Response;

-- name: 11_category_share_of_spend
-- question: Which product categories make up total spend?
SELECT 'Wines' AS category, SUM(MntWines) AS spend FROM customers
UNION ALL SELECT 'Meat',    SUM(MntMeatProducts)  FROM customers
UNION ALL SELECT 'Gold',    SUM(MntGoldProds)     FROM customers
UNION ALL SELECT 'Fish',    SUM(MntFishProducts)  FROM customers
UNION ALL SELECT 'Sweets',  SUM(MntSweetProducts) FROM customers
UNION ALL SELECT 'Fruits',  SUM(MntFruits)        FROM customers
ORDER BY spend DESC;

-- name: 12_top_decile_spend_share
-- question: How much of total spend comes from the top 10% of customers? (window function)
WITH ranked AS (
    SELECT ID, Total_Spend, Response,
           NTILE(10) OVER (ORDER BY Total_Spend DESC) AS spend_decile
    FROM customers
)
SELECT spend_decile,
       COUNT(*)                                                   AS customers,
       SUM(Total_Spend)                                           AS spend,
       ROUND(100.0 * SUM(Total_Spend) / SUM(SUM(Total_Spend)) OVER (), 1) AS spend_share_pct,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1)                 AS response_rate_pct
FROM ranked
GROUP BY spend_decile
ORDER BY spend_decile;

-- name: 13_high_value_target_profile
-- question: What is the response rate of a "high-value, recently active" profile vs everyone else? (CTE)
WITH flagged AS (
    SELECT *,
           CASE WHEN Income_Group = 'High' AND Recency <= 49 AND Children = 0
                THEN 'High income, no children, active in last 50 days'
                ELSE 'Everyone else' END AS profile
    FROM customers
)
SELECT profile,
       COUNT(*)                                   AS customers,
       ROUND(AVG(Total_Spend), 0)                 AS avg_spend,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM flagged
GROUP BY profile
ORDER BY response_rate_pct DESC;

-- name: 14_complaints_vs_response
-- question: Do customers who complained still respond?
SELECT CASE Complain WHEN 1 THEN 'Complained' ELSE 'No complaint' END AS complaint_status,
       COUNT(*)                                   AS customers,
       ROUND(100.0 * SUM(Response) / COUNT(*), 1) AS response_rate_pct
FROM customers
GROUP BY Complain;

-- name: 15_campaign_acceptance_trend
-- question: How many customers accepted each of the 6 campaigns?
SELECT 'Campaign 1' AS campaign, SUM(AcceptedCmp1) AS accepted FROM customers
UNION ALL SELECT 'Campaign 2', SUM(AcceptedCmp2) FROM customers
UNION ALL SELECT 'Campaign 3', SUM(AcceptedCmp3) FROM customers
UNION ALL SELECT 'Campaign 4', SUM(AcceptedCmp4) FROM customers
UNION ALL SELECT 'Campaign 5', SUM(AcceptedCmp5) FROM customers
UNION ALL SELECT 'Campaign 6 (last)', SUM(Response) FROM customers;
