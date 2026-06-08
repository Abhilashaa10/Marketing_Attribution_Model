#  Marketing Attribution Analysis

## Project Overview

This project analyzes customer journeys across multiple marketing channels to understand how different channels contribute to conversions and revenue.

A dataset containing over **200,000 campaign interactions** was processed using a custom Python pipeline to reconstruct **20,000 individual customer journeys**. Various attribution models were then applied to compare how marketing credit is distributed across channels.

### Dataset Summary

* Total Touchpoints: 49,633
* Total Customer Journeys: 20,000
* Unique Customers: 11,033
* Converted Journeys: 2,859
* Conversion Rate: 14.3%
* Total Revenue: $1.96M
* Average Order Value (AOV): $275.43

---

## Channel Performance Analysis

The dataset includes six marketing channels:

* Google Ads
* Email
* YouTube
* Facebook
* Instagram
* Website

### Key Findings

* **Google Ads** generated the highest overall revenue.
* **Email** showed the strongest conversion performance and frequently appeared near the final conversion stage.
* **YouTube** and **Instagram** played a significant role in customer acquisition and brand discovery.
* **Website** and **Email** were common conversion-driving touchpoints.
* Conversion rates across all channels remained relatively consistent (13–15%).

### Insight

Since channel conversion rates are similar, relying on a single-touch attribution model can lead to inaccurate conclusions. Multi-touch attribution provides a more complete view of channel contribution throughout the customer journey.

---

## Attribution Model Comparison

To evaluate channel effectiveness, five attribution models were implemented.

### First-Touch Attribution

Assigns 100% of conversion credit to the first customer interaction.

**Best For:**

* Measuring customer acquisition
* Evaluating awareness campaigns

### Last-Touch Attribution

Assigns 100% of conversion credit to the final interaction before purchase.

**Best For:**

* Measuring conversion-driving channels
* Executive-level reporting

**Limitation:**

* Tends to over-credit closing channels while ignoring earlier interactions.

### Linear Attribution

Distributes conversion credit equally across all touchpoints.

**Best For:**

* Balanced channel performance analysis
* Ongoing marketing reporting

### Time-Decay Attribution

Assigns greater credit to interactions occurring closer to conversion.

**Best For:**

* Promotional campaigns
* Short sales cycles

### Position-Based (U-Shaped) Attribution

Allocates:

* 40% credit to the first touchpoint
* 40% credit to the last touchpoint
* 20% credit across middle interactions

**Best For:**

* Organizations that value both acquisition and conversion activities

### Model Comparison Insight

Compared to Linear Attribution, the Last-Touch model increased credit allocation to closing channels such as Email and Website by approximately 3–5%.

This suggests that organizations relying solely on Last-Touch reporting may underestimate the contribution of upper-funnel channels such as YouTube and Instagram.

---

## Customer Journey Analysis

### Journey Characteristics

* Average Touchpoints Before Conversion: 2.48
* Most Common Journey Length: 2 Touchpoints
* Approximately 40% of journeys contain a single interaction

### Behavioral Insights

* Multi-touch journeys generally outperform single-touch journeys.
* Customers engaging across multiple channels tend to generate higher order values.
* Repeat interactions within the same channel are common among converting customers.
* Cross-channel journeys demonstrate stronger overall revenue performance.

### Example High-Performing Paths

* Google Ads → Google Ads
* YouTube → Email → Website
* Instagram → Google Ads → Email

---

## Revenue Trends

Revenue remained relatively stable throughout most of 2021.

### Strongest Months

* March
* May
* July

### Note on November

A noticeable decline appears in November; however, this is due to incomplete data coverage rather than an actual decrease in business performance.

---

## Business Recommendations

### 1. Adopt Multi-Touch Attribution

Avoid making budget decisions using Last-Touch Attribution alone. Linear and Position-Based models provide a more balanced representation of channel impact.

### 2. Maintain Awareness Investments

Channels such as YouTube, Instagram, and Google Ads frequently initiate converting journeys and support top-of-funnel customer acquisition.

### 3. Strengthen Email Marketing

Email consistently appears in high-value conversion paths and performs effectively as a closing channel.

### 4. Encourage Cross-Channel Engagement

Customers exposed to multiple channels tend to convert at higher values. Marketing strategies should intentionally guide users through awareness, consideration, and conversion stages.

### 5. Use Time-Decay for Campaign Analysis

For seasonal promotions and short-term campaigns, Time-Decay Attribution provides a more realistic view of channel influence near conversion.

---

## Recommended Attribution Models

| Business Objective            | Recommended Model          |
| ----------------------------- | -------------------------- |
| Monthly Performance Reporting | Linear Attribution         |
| Brand Awareness Measurement   | First-Touch Attribution    |
| Campaign ROI Analysis         | Time-Decay Attribution     |
| Budget Allocation Decisions   | Position-Based Attribution |
| Executive-Level Summaries     | Last-Touch Attribution     |

---

## Technology Stack

* Python
* Pandas
* NumPy
* PostgreSQL
* Matplotlib
* Seaborn
* VS Code

---

## Project Outcome

This project demonstrates the implementation and comparison of multiple attribution models to evaluate channel effectiveness, customer behavior, and revenue contribution across a multi-channel marketing ecosystem.

The analysis highlights how attribution methodology can significantly influence marketing decisions and budget allocation strategies.
