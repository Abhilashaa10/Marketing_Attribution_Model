-- 1. OVERALL KPIs
SELECT
    COUNT(DISTINCT Customer_ID)                          AS total_customers,
    COUNT(DISTINCT Journey_ID)                           AS total_journeys,
    SUM(Conversion_Flag)                                 AS total_conversions,
    ROUND(SUM(Revenue_Amount)::NUMERIC, 2)               AS total_revenue,
    ROUND(AVG(Revenue_Amount)
          FILTER (WHERE Revenue_Amount > 0)::NUMERIC, 2) AS avg_order_value,
    ROUND(SUM(Conversion_Flag)::NUMERIC
          / COUNT(DISTINCT Journey_ID) * 100, 2)         AS conversion_rate_pct
FROM raw_customer_journeys;


--  2. CHANNEL PERFORMANCE 
SELECT
    Marketing_Channel,
    COUNT(*)                                             AS total_touchpoints,
    COUNT(DISTINCT Journey_ID)                           AS unique_journeys,
    SUM(Conversion_Flag)                                 AS conversions,
    ROUND(SUM(Revenue_Amount)::NUMERIC, 2)               AS total_revenue,
    ROUND(SUM(Conversion_Flag)::NUMERIC
          / COUNT(DISTINCT Journey_ID) * 100, 2)         AS conversion_rate_pct,
    ROUND(SUM(Revenue_Amount)::NUMERIC
          / NULLIF(SUM(Conversion_Flag), 0), 2)          AS avg_revenue_per_conversion
FROM raw_customer_journeys
GROUP BY Marketing_Channel
ORDER BY total_revenue DESC;


--  3. ATTRIBUTION MODEL COMPARISON 
SELECT
    Marketing_Channel,
    First_Touch_Revenue,
    Last_Touch_Revenue,
    Linear_Revenue,
    Time_Decay_Revenue,
    Position_Based_Revenue,
    First_Touch_Pct   AS first_touch_pct,
    Last_Touch_Pct    AS last_touch_pct,
    Linear_Pct        AS linear_pct,
    Time_Decay_Pct    AS time_decay_pct,
    Position_Based_Pct AS position_based_pct
FROM channel_attribution_summary
ORDER BY Linear_Revenue DESC;


--  4. MONTHLY REVENUE TREND 
SELECT
    DATE_TRUNC('month', Interaction_Timestamp)           AS month,
    COUNT(DISTINCT Journey_ID)                           AS journeys,
    SUM(Conversion_Flag)                                 AS conversions,
    ROUND(SUM(Revenue_Amount)::NUMERIC, 2)               AS revenue,
    ROUND(SUM(Conversion_Flag)::NUMERIC
          / COUNT(DISTINCT Journey_ID) * 100, 2)         AS conversion_rate_pct
FROM raw_customer_journeys
GROUP BY 1
ORDER BY 1;


--  5. JOURNEY LENGTH ANALYSIS 
WITH journey_lengths AS (
    SELECT
        Journey_ID,
        COUNT(*)            AS total_touchpoints,
        MAX(Conversion_Flag) AS converted,
        MAX(Revenue_Amount)  AS revenue
    FROM raw_customer_journeys
    GROUP BY Journey_ID
)
SELECT
    total_touchpoints,
    COUNT(*)                                             AS total_journeys,
    SUM(converted)                                       AS conversions,
    ROUND(SUM(converted)::NUMERIC
          / COUNT(*) * 100, 2)                           AS conversion_rate_pct,
    ROUND(SUM(revenue)::NUMERIC, 2)                      AS total_revenue,
    ROUND(AVG(revenue)
          FILTER (WHERE converted = 1)::NUMERIC, 2)      AS avg_revenue
FROM journey_lengths
GROUP BY total_touchpoints
ORDER BY total_touchpoints;


--  6. FIRST TOUCH CHANNEL ANALYSIS 
WITH first_touches AS (
    SELECT
        Journey_ID,
        Marketing_Channel,
        ROW_NUMBER() OVER (
            PARTITION BY Journey_ID
            ORDER BY Interaction_Timestamp ASC
        ) AS rn
    FROM raw_customer_journeys
),
journey_outcomes AS (
    SELECT
        Journey_ID,
        MAX(Conversion_Flag) AS converted,
        MAX(Revenue_Amount)  AS revenue
    FROM raw_customer_journeys
    GROUP BY Journey_ID
)
SELECT
    ft.Marketing_Channel                                 AS first_touch_channel,
    COUNT(*)                                             AS times_first_touch,
    SUM(jo.converted)                                    AS led_to_conversion,
    ROUND(SUM(jo.converted)::NUMERIC
          / COUNT(*) * 100, 2)                           AS discovery_conv_rate_pct,
    ROUND(SUM(jo.revenue)::NUMERIC, 2)                   AS revenue_driven
FROM first_touches ft
JOIN journey_outcomes jo USING (Journey_ID)
WHERE ft.rn = 1
GROUP BY ft.Marketing_Channel
ORDER BY revenue_driven DESC;


--7. LAST TOUCH CHANNEL ANALYSIS 
WITH last_touches AS (
    SELECT
        Journey_ID,
        Marketing_Channel,
        ROW_NUMBER() OVER (
            PARTITION BY Journey_ID
            ORDER BY Interaction_Timestamp DESC
        ) AS rn
    FROM raw_customer_journeys
)
SELECT
    lt.Marketing_Channel                                 AS last_touch_channel,
    COUNT(*)                                             AS times_closed,
    ROUND(SUM(r.Revenue_Amount)::NUMERIC, 2)             AS revenue_closed,
    ROUND(AVG(r.Revenue_Amount)::NUMERIC, 2)             AS avg_close_revenue
FROM last_touches lt
JOIN raw_customer_journeys r USING (Journey_ID)
WHERE lt.rn = 1
  AND r.Conversion_Flag = 1
  AND r.Revenue_Amount > 0
GROUP BY lt.Marketing_Channel
ORDER BY revenue_closed DESC;


--  8. TOP CONVERSION PATHS
WITH ordered_touches AS (
    SELECT
        Journey_ID,
        Marketing_Channel,
        ROW_NUMBER() OVER (
            PARTITION BY Journey_ID
            ORDER BY Interaction_Timestamp ASC
        ) AS position
    FROM raw_customer_journeys
),
journey_paths AS (
    SELECT
        Journey_ID,
        STRING_AGG(Marketing_Channel, ' → '
                   ORDER BY position)                    AS path
    FROM ordered_touches
    GROUP BY Journey_ID
),
converted_journeys AS (
    SELECT
        Journey_ID,
        MAX(Revenue_Amount) AS revenue
    FROM raw_customer_journeys
    WHERE Conversion_Flag = 1
    GROUP BY Journey_ID
)
SELECT
    jp.path,
    COUNT(*)                                             AS conversions,
    ROUND(SUM(cj.revenue)::NUMERIC, 2)                   AS total_revenue,
    ROUND(AVG(cj.revenue)::NUMERIC, 2)                   AS avg_revenue
FROM journey_paths jp
JOIN converted_journeys cj USING (Journey_ID)
GROUP BY jp.path
ORDER BY conversions DESC
LIMIT 15;