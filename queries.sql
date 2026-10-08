-- 1. Overall Campaign Response Rate
SELECT 
    COUNT(*) AS total_customers,
    SUM(Response) AS total_responders,
    ROUND(CAST(SUM(Response) AS FLOAT) / COUNT(*) * 100, 2) AS response_rate_percentage
FROM customers;

-- 2. Campaign Response by Income and Children Segment (Key Finding)
SELECT 
    CASE 
        WHEN Income > 70000 AND (Kidhome + Teenhome) = 0 THEN 'High Income, No Kids'
        WHEN Income > 70000 AND (Kidhome + Teenhome) > 0 THEN 'High Income, With Kids'
        ELSE 'Other Segments'
    END AS customer_segment,
    COUNT(*) AS customer_count,
    SUM(Response) AS responders,
    ROUND(CAST(SUM(Response) AS FLOAT) / COUNT(*) * 100, 2) AS segment_response_rate
FROM customers
GROUP BY customer_segment
ORDER BY segment_response_rate DESC;

-- 3. Using Window Functions (NTILE) to segment customers by total spending
SELECT 
    ID,
    Year_Birth,
    Income,
    (MntWines + MntFruits + MntMeatProducts + MntFishProducts + MntSweetProducts + MntGoldProds) AS total_spent,
    NTILE(4) OVER (ORDER BY (MntWines + MntFruits + MntMeatProducts + MntFishProducts + MntSweetProducts + MntGoldProds) DESC) AS spending_quartile
FROM customers;
