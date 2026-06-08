-- ============================================================
-- Marketing Attribution Model
-- PostgreSQL Schema
-- ============================================================

-- Drop existing tables
DROP TABLE IF EXISTS channel_attribution_summary CASCADE;
DROP TABLE IF EXISTS raw_customer_journeys CASCADE;

-- TABLE: raw_customer_journeys 
CREATE TABLE raw_customer_journeys (
    id                    SERIAL PRIMARY KEY,
    Customer_ID           VARCHAR(20)   NOT NULL,
    Journey_ID            VARCHAR(20)   NOT NULL,
    Marketing_Channel     VARCHAR(50)   NOT NULL,
    Interaction_Timestamp TIMESTAMP     NOT NULL,
    Conversion_Flag       SMALLINT      NOT NULL DEFAULT 0,
    Revenue_Amount        NUMERIC(10,2) NOT NULL DEFAULT 0.00
);

-- Indexes for faster querying
CREATE INDEX idx_journey_id      ON raw_customer_journeys(Journey_ID);
CREATE INDEX idx_customer_id     ON raw_customer_journeys(Customer_ID);
CREATE INDEX idx_channel         ON raw_customer_journeys(Marketing_Channel);
CREATE INDEX idx_timestamp       ON raw_customer_journeys(Interaction_Timestamp);
CREATE INDEX idx_conversion_flag ON raw_customer_journeys(Conversion_Flag);

-- TABLE: channel_attribution_summary 
CREATE TABLE channel_attribution_summary (
    Marketing_Channel      VARCHAR(50)   PRIMARY KEY,
    First_Touch_Revenue    NUMERIC(12,2),
    Last_Touch_Revenue     NUMERIC(12,2),
    Linear_Revenue         NUMERIC(12,2),
    Time_Decay_Revenue     NUMERIC(12,2),
    Position_Based_Revenue NUMERIC(12,2),
    Total_Conversions      INT,
    Total_Touchpoints      INT,
    First_Touch_Pct        NUMERIC(6,2),
    Last_Touch_Pct         NUMERIC(6,2),
    Linear_Pct             NUMERIC(6,2),
    Time_Decay_Pct         NUMERIC(6,2),
    Position_Based_Pct     NUMERIC(6,2)
);