# Vendor Performance & Sales Analysis Dashboard

An end-to-end data analytics project that ingests raw retail/distribution data into a MySQL database, builds a consolidated vendor performance summary using SQL and Python, performs exploratory data analysis, and visualizes business insights through an interactive two-page Power BI dashboard.

---

## 📌 Project Overview

This project analyzes purchasing, sales, and inventory data for a retail/beverage distribution business to answer key business questions:

- Which vendors and brands drive the most revenue and profit?
- Which brands are priced for a promotional push (low sales, high margin)?
- How efficiently is inventory being converted into sales?
- Which vendors have disproportionately high freight/logistics costs?
- Which vendors or brands are underperforming and need attention?

The pipeline moves data through four stages: **raw CSVs → MySQL database → Python cleaning & aggregation → Power BI dashboard.**

---

## 🗂️ Dataset

The source data consists of six CSV files loaded into a MySQL database (`inventory`):

| Table | Description |
|---|---|
| `begin_inventory` | Opening inventory snapshot |
| `end_inventory` | Closing inventory snapshot |
| `purchases` | Individual purchase transactions |
| `purchase_prices` | Price list per brand |
| `sales` | Individual sales transactions (~12.8M rows) |
| `vendor_invoice` | Vendor invoice and freight records |

> Dataset source: *(add the original dataset link / course / tutorial credit here)*

---

## 🛠️ Tech Stack

- **Python** — pandas, SQLAlchemy, PyMySQL, NumPy, logging, gc
- **MySQL** — relational database for staging and aggregation
- **Jupyter Notebook** — exploratory data analysis (matplotlib, seaborn, scipy)
- **Power BI Desktop** — interactive dashboard (DAX, Power Query)

---

## 🏗️ Pipeline Architecture

```
Raw CSVs (data/)
      │
      ▼
ingestion_db.py  ──► MySQL (inventory DB)
      │               • chunked CSV reads (avoids MemoryError on 12.8M-row file)
      │               • per-file error handling & logging
      ▼
Get_Vendor_Summary.py
      │               • joins purchases, sales & freight via SQL CTEs
      │               • cleans data (nulls, whitespace, inf/-inf)
      │               • derives Gross Profit, Profit Margin,
      │                 Stock Turnover, Sales-to-Purchase Ratio
      ▼
vendor_sales_summary (MySQL table)
      │
      ├──► Exploratory Data Analysis.ipynb   (distribution, outliers, correlation)
      │
      └──► Power BI Dashboard (.pbix)        (Page 1: Vendor Overview,
                                               Page 2: Brand Profitability)
```

---

## 📁 Repository Structure

```
├── data/                          # raw CSV files (not included — add your own)
├── logs/
│   ├── ingestion_db.log           # data ingestion run logs
│   └── get_vendor_summary.log     # vendor summary build logs
├── ingestion_db.py                # loads CSVs into MySQL with chunked processing
├── Get_Vendor_Summary.py          # builds vendor_sales_summary via SQL + cleaning
├── Exploratory Data Analysis.ipynb
├── Vendor Performance Dashboard.pbix
├── dark_gold_theme.json           # custom Power BI theme
└── README.md
```

---

## ⚙️ Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

**2. Install Python dependencies**
```bash
pip install pandas sqlalchemy pymysql numpy matplotlib seaborn scipy
```

**3. Set up MySQL**
- Install MySQL Server and MySQL Workbench
- Create a database:
```sql
CREATE DATABASE inventory;
```

**4. Add your data**
- Place the six source CSV files in a `data/` folder in the project root

**5. Update the connection string**
- In `ingestion_db.py` and `Get_Vendor_Summary.py`, update:
```python
engine = create_engine("mysql+pymysql://root:<your_password>@localhost:3306/inventory")
```

**6. Run the pipeline**
```bash
python ingestion_db.py          # loads all 6 CSVs into MySQL
python Get_Vendor_Summary.py    # builds the vendor_sales_summary table
```

**7. Explore the data**
```bash
jupyter notebook "Exploratory Data Analysis.ipynb"
```

**8. Open the dashboard**
- Open `Vendor Performance Dashboard.pbix` in Power BI Desktop
- Point the MySQL connection to your own `localhost:3306/inventory`
- (Optional) Import `dark_gold_theme.json` via **View → Themes → Browse for themes**

---

## 🔑 Key Features

- **Memory-safe ingestion**: the `sales` table (~12.8M rows) is read and inserted in configurable chunks, with explicit garbage collection between chunks, to run reliably on machines with limited RAM
- **Resilient pipeline**: each file is wrapped in try/except so a single failure doesn't halt the entire ingestion run
- **Full logging**: every stage (ingestion, summary build) writes timestamped logs for debugging and auditability
- **SQL-based aggregation**: vendor-level purchase, sales, and freight data are combined using SQL CTEs (`WITH` clauses) rather than slow in-memory merges
- **Data quality handling**: division-by-zero cases (which produce `inf`/`-inf`) are detected and replaced before loading into MySQL, since MySQL cannot store infinite values
- **Derived business metrics**: Gross Profit, Profit Margin, Stock Turnover, and Sales-to-Purchase Ratio are calculated for every vendor/brand combination
- **Outlier-aware analysis**: Top N / Bottom N views are filtered by a minimum sales threshold to exclude negligible-volume brands that would otherwise distort margin rankings

---

## 📊 Dashboard

### Page 1 — Vendor Performance Overview
- KPI cards: Total Sales, Total Purchase, Gross Profit, Profit Margin, Unsold Capital
- Purchase Contribution % — Top 10 vendors (donut chart)
- Top Vendors by Sales / Top Brands by Sales
- Low Performing Vendors — lowest stock turnover
- Low Performing Brands — scatter plot of sales vs. profit margin, flagging brands that are strong candidates for promotional or pricing adjustments

### Page 2 — Brand Profitability & Efficiency
- Top 10 / Bottom 10 brands by profit margin (restricted to brands with meaningful sales volume)
- Freight Cost % table — vendors with disproportionately high shipping cost relative to purchase size, with data-bar formatting
- Sales-to-Purchase Ratio — brands that convert purchased stock into revenue most efficiently
- Interactive vendor slicer across all visuals on the page

---

## 🧩 Key Challenges & Solutions

| Challenge | Solution |
|---|---|
| `FileNotFoundError` on first log write | Created the `logs/` folder programmatically with `os.makedirs(..., exist_ok=True)` before `logging.basicConfig` |
| `MemoryError` ingesting the 12.8M-row `sales.csv` on a memory-constrained machine | Switched to chunked `pd.read_csv()` + chunked `to_sql()` inserts, with `gc.collect()` after every chunk |
| `vendor_invoice.csv` silently skipped after a prior file crashed | Added per-file `try/except` around the ingestion loop so one failure doesn't block the rest |
| MySQL rejected insert with `ProgrammingError: -inf can not be used with MySQL` | Replaced `inf`/`-inf` values (from division-by-zero profit margins) with `0` before loading |
| Power BI's Top N filter initially inflated by negligible-volume outlier brands | Added a minimum `TotalSalesDollars` threshold filter alongside each Top N / Bottom N ranking |
| Power BI unable to connect to local MySQL | Installed the MySQL Connector/NET driver required for the native MySQL connector |

---

## 📈 Sample Insights

- A small core of vendors (~top 10) accounts for the majority of total purchase spend, indicating significant vendor concentration
- Several brands sell in high volume while operating at thin or negative profit margins, flagging potential pricing issues
- A distinct group of low-sales, high-margin brands were identified as strong candidates for promotional investment
- Certain vendors show freight costs that are disproportionately high relative to their purchase volume, suggesting room for logistics negotiation

---

## 🚀 Future Improvements

- Automate the ingestion pipeline on a schedule (e.g., Airflow, Windows Task Scheduler)
- Add a time-trend analysis page (monthly/seasonal sales patterns)
- Publish the dashboard to Power BI Service for scheduled refresh and sharing
- Add unit tests for the ingestion and cleaning functions
- Parameterize database credentials via environment variables instead of hardcoding

---

## 📬 Contact

**[Your Name]**
[LinkedIn] • [Email] • [Portfolio]

---

*This project was built as a hands-on exercise in end-to-end data analytics: database engineering, Python data pipelines, and business intelligence dashboarding.*
