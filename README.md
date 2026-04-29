# Data Warehouse Sales

A production-style Data Warehouse built with Python, SQLAlchemy, and PostgreSQL, implementing a Star Schema with 10,000 synthetic sales records.

## Overview

This project demonstrates core Data Engineering concepts applied in practice:

- **Data Modeling** — Star Schema design with Fact and Dimension tables
- **SQLAlchemy Core** — Database abstraction layer for portable, professional ETL pipelines
- **Data Generation** — Realistic synthetic data using Faker, Pandas, and the `holidays` library
- **PostgreSQL** — Analytical database with Foreign Key constraints enforcing referential integrity

## Architecture

```
dim_customer ─── fact_sales ─── dim_date
                     │
                dim_product
```

The `fact_sales` table sits at the center of the star, holding metrics and foreign keys. Dimension tables provide the descriptive context for each sale.

## Schema

### dim_date
| Column | Type | Description |
|---|---|---|
| date_id | INTEGER (PK) | Format YYYYMMDD |
| date | DATE | Calendar date |
| day | INTEGER | Day of month |
| month | INTEGER | Month number |
| quarter | INTEGER | Quarter (1–4) |
| year | INTEGER | Year |
| day_of_week | INTEGER | 0=Monday, 6=Sunday |
| is_weekend | BOOLEAN | True for Saturday/Sunday |
| is_holiday | BOOLEAN | Brazilian public holidays |

### dim_customer
| Column | Type | Description |
|---|---|---|
| customer_id | INTEGER (PK) | Auto-incremented |
| customer_name | VARCHAR(200) | Full name |
| customer_email | VARCHAR(200) | Email address |
| city | VARCHAR(200) | City |
| country | VARCHAR(200) | Country |
| is_corporate | BOOLEAN | Corporate vs individual customer |

### dim_product
| Column | Type | Description |
|---|---|---|
| product_id | INTEGER (PK) | Auto-incremented |
| product_name | VARCHAR(200) | Product name |
| category | VARCHAR(200) | Electronics, Furniture, Clothing, Sports |
| price | NUMERIC(10,2) | Current list price |

### fact_sales
| Column | Type | Description |
|---|---|---|
| sale_id | INTEGER (PK) | Auto-incremented |
| date_id | INTEGER (FK) | References dim_date |
| customer_id | INTEGER (FK) | References dim_customer |
| product_id | INTEGER (FK) | References dim_product |
| quantity | INTEGER | Units sold |
| unit_price | NUMERIC(10,2) | Price at time of sale |
| total_amount | NUMERIC(10,2) | Pre-calculated: quantity × unit_price |

## Data Volume

| Table | Rows |
|---|---|
| dim_date | 365 (full year 2023) |
| dim_customer | 100 |
| dim_product | 50 |
| fact_sales | 10,000 |

## Tech Stack

- Python 3.14
- PostgreSQL 15
- SQLAlchemy 2.0 (Core)
- Pandas
- Faker
- holidays
- python-dotenv

## Project Structure

```
data-warehouse-sales/
├── src/
│   ├── database.py   # get_engine() — SQLAlchemy connection factory
│   ├── models.py     # Table definitions — Star Schema
│   ├── etl.py        # Data generation and loading functions
│   └── main.py       # Pipeline orchestrator
├── .env              # Credentials (not tracked)
├── .gitignore
└── README.md
```

## How to Run

**1. Clone the repository**
```bash
git clone https://github.com/RolandGDev/data-warehouse-sales.git
cd data-warehouse-sales
```

**2. Create and activate virtual environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install sqlalchemy psycopg2-binary python-dotenv pandas faker holidays
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_NAME=sales_dw
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_PORT=5432
```

**5. Create the database**
```bash
psql -U your_postgres_user -d postgres -c "CREATE DATABASE sales_dw;"
```

**6. Run the pipeline**
```bash
python src/main.py
```

This will create all tables and populate the warehouse with synthetic data.

**7. Verify the data**
```bash
psql -U your_postgres_user -d sales_dw -c "SELECT COUNT(*) FROM fact_sales;"
```

## Key Design Decisions

**Star Schema over 3NF normalization** — The warehouse is designed for analytical queries (OLAP), not transactional operations (OLTP). Denormalization enables fast aggregations without complex multi-table JOINs at query time.

**dim_date as a separate table** — Pre-computing date attributes (quarter, is_weekend, is_holiday) once at load time avoids recalculating them across millions of rows on every query.

**total_amount as a derived column** — Storing `quantity × unit_price` avoids recalculating this on every analytical query. Trades disk space for read performance — disk is cheap, query time is not.

**Single connection pattern** — All sequential database operations within `load_facts_sales` share one connection, following production ETL standards.

**Separation of generation and loading** — Data generation logic (`generate_facts_sales_records`) is decoupled from database access (`load_facts_sales`), making each function independently testable.

## Author

Garcia — Data Engineering Bootcamp
