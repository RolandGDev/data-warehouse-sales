"""
================================================================================
Data Warehouse Sales — Entry Point
================================================================================
Description : Orchestrates the full ETL pipeline for the sales data warehouse.
              Creates all schema tables and populates dimension and fact tables
              in the correct dependency order.

Load order:
    1. dim_date     — no foreign key dependencies
    2. dim_customer — no foreign key dependencies
    3. dim_product  — no foreign key dependencies
    4. fact_sales   — depends on all three dimensions above

Usage:
    Run from the project root:
        python -m src.main

Author      : Roland Garcia
Created     : 2026-01-01
================================================================================
"""

# ---------------------------------------------------------------------------
# Standard library
# ---------------------------------------------------------------------------
import logging
import sys

# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------
from database import get_engine
from etl import load_customer_records, load_dim_dates, load_facts_sales, load_products_records
from models import create_tables

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------
try:
    engine = get_engine()

    logging.info("Creating tables...")
    create_tables(engine)

    logging.info("Loading dimension tables...")
    load_dim_dates(engine)
    load_customer_records(engine)
    load_products_records(engine)

    logging.info("Loading fact table...")
    load_facts_sales(engine)

    logging.info("Pipeline completed successfully.")

except Exception as err:
    logging.exception("Pipeline failed: %s", err)
    sys.exit(1)
