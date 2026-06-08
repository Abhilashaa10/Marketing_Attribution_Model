# Marketing Attribution Model Comparison

End-to-End Data Analytics Project using Python, PostgreSQL, SQL, Pandas, and Data Visualization.

---

## Project Overview

Modern businesses use multiple marketing channels such as Google Ads, Instagram, YouTube, Facebook, Email, and Website to acquire customers. Since customers often interact with several channels before making a purchase, determining which channel deserves credit for a conversion becomes a key business challenge.

This project builds a complete marketing attribution pipeline that:

* Transforms campaign-level data into customer journey data
* Simulates multi-touch customer interactions
* Implements five industry-standard attribution models
* Evaluates channel contribution to conversions and revenue
* Generates business insights and visual reports

---

## Project Structure

```text
MARKETING_ATTRIBUTION_MODEL/
│
├── data/
├── scripts/
├── sql/
├── screenshots/
├── reports/
├── main.py
├── README.md
└── requirements.txt
```

### Data

* marketing_campaign_dataset.csv – Original campaign dataset
* customer_journeys.csv – Generated customer journey data
* attribution_results.csv – Attribution model outputs
* channel_performance.csv – Channel-level KPIs
* monthly_trend.csv – Revenue trend analysis
* top_conversion_paths.csv – Most common conversion journeys

### Scripts

* generate_journeys.py – Creates customer journey data
* load_to_postgres.py – Loads data into PostgreSQL
* calculate_attribution.py – Calculates attribution models
* analysis.py – Generates KPIs and business insights
* visualizations.py – Produces charts and dashboards

### SQL

* schema.sql – Database schema
* analysis_queries.sql – Analytical SQL queries

---

## Technology Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Data processing and analytics |
| Pandas     | Data transformation           |
| NumPy      | Numerical computations        |
| PostgreSQL | Data storage                  |
| SQLAlchemy | Database connectivity         |
| SQL        | Data analysis                 |
| Matplotlib | Data visualization            |
| Seaborn    | Heatmaps and advanced charts  |
| VS Code    | Development environment       |

---

## Dataset

The source dataset contains approximately 200,000 marketing campaign records with information such as channel usage, impressions, clicks, conversion rates, acquisition cost, ROI, customer segment, and campaign dates.

Because the data exists at campaign level rather than customer level, a custom Python pipeline was developed to generate realistic customer journeys using observed channel distributions, conversion probabilities, and revenue patterns.

### Generated Dataset Summary

| Metric            | Value  |
| ----------------- | ------ |
| Customer Journeys | 20,000 |
| Total Touchpoints | 49,633 |
| Unique Customers  | 11,033 |
| Conversions       | 2,859  |
| Conversion Rate   | 14.3%  |

---

## Attribution Models Implemented

### First-Touch Attribution

Assigns 100% of conversion credit to the first interaction in the customer journey.

**Use Case:** Customer acquisition and brand awareness analysis.

### Last-Touch Attribution

Assigns 100% of conversion credit to the final interaction before conversion.

**Use Case:** Measuring conversion-driving channels.

**Limitation:** Ignores the contribution of earlier touchpoints.

### Linear Attribution

Distributes conversion credit equally across all touchpoints.

**Use Case:** Balanced channel performance evaluation.

### Time-Decay Attribution

Assigns progressively more credit to interactions occurring closer to conversion.

**Formula:**

`weight = e^(-0.1 × days_before_conversion)`

**Use Case:** Promotional and short sales-cycle campaigns.

### Position-Based Attribution (U-Shaped)

* 40% credit to the first touchpoint
* 40% credit to the last touchpoint
* 20% distributed across middle interactions

**Use Case:** Organizations that value both acquisition and conversion stages.

---

## Analysis and Key Findings

### Channel Performance

* Google Ads generated the highest revenue contribution.
* Email consistently appeared as a high-performing closing channel.
* YouTube and Instagram played a significant role in customer acquisition.
* Conversion rates across channels remained relatively consistent (13–15%).

### Attribution Insights

* Last-Touch Attribution over-credited closing channels such as Email and Website by approximately 3–5% compared to Linear Attribution.
* Multi-touch attribution provided a more accurate representation of channel contribution than single-touch models.

### Customer Journey Insights

* Average touchpoints before conversion: 2.48
* Most common journey length: 2 touchpoints
* Customers interacting with 3–4 channels generated higher average order values than single-touch customers.
* Cross-channel journeys outperformed single-channel journeys in revenue generation.

---

## Business Recommendations

### Use Multi-Touch Attribution

Linear and Position-Based Attribution provide a more balanced view of channel performance than Last-Touch Attribution.

### Protect Awareness Channels

Channels such as YouTube, Instagram, and Google Ads frequently initiate customer journeys and contribute to top-of-funnel acquisition.

### Strengthen Email Marketing

Email consistently appears in high-value conversion paths and performs effectively as a closing channel.

### Encourage Cross-Channel Engagement

Customers exposed to multiple marketing channels tend to generate higher revenue and stronger conversion outcomes.

### Apply Time-Decay for Campaign Analysis

Time-Decay Attribution is particularly useful for evaluating promotional and seasonal campaigns where recent interactions have greater influence on purchase decisions.

---

## Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Database

```bash
psql -U postgres -d marketing_attribution -f sql/schema.sql
```

### Execute Pipeline

```bash
python main.py
```

Or run individual modules:

```bash
python scripts/generate_journeys.py
python scripts/load_to_postgres.py
python scripts/calculate_attribution.py
python scripts/analysis.py
python scripts/visualizations.py
```

---

## Outputs

The project generates:

* Customer journey dataset
* Attribution model comparison results
* Channel performance metrics
* Revenue trend analysis
* Conversion path analysis
* Business insight report
* Data visualizations and dashboards

---

## Report

Detailed findings, attribution analysis, and business recommendations are available in:

`reports/business_insights.md`

---

Data Period: January 2021 – November 2021

Tools Used: Python, Pandas, NumPy, PostgreSQL, SQL, Matplotlib, Seaborn, SQLAlchemy
