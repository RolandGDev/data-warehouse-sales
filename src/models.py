"""
================================================================================
Models Module — Data Warehouse Sales
================================================================================
Description : Defines the star schema data model for the sales data warehouse
              using SQLAlchemy Core Table definitions.

Schema overview:
    Dimensions:
        - dim_product  : Product catalog with category and price.
        - dim_customer : Customer profiles with location and corporate flag.
        - dim_date     : Date dimension with calendar and holiday attributes.

    Facts:
        - fact_sales   : Sales transactions referencing all three dimensions.

    Staging:
        - products     : Staging table for raw product data.

Author      : Roland Garcia
Created     : 2026-01-01
================================================================================
"""

# ---------------------------------------------------------------------------
# Third-party
# ---------------------------------------------------------------------------
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
)
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# Shared metadata registry
# ---------------------------------------------------------------------------
metadata = MetaData()

# ---------------------------------------------------------------------------
# Staging table
# ---------------------------------------------------------------------------

products = Table(
    "products",
    metadata,
    Column("product_id",   Integer,      primary_key=True),
    Column("product_name", String(200)),
    Column("category",     String(200)),
    Column("price",        Numeric(10, 2)),
)

# ---------------------------------------------------------------------------
# Dimension tables
# ---------------------------------------------------------------------------

dim_product = Table(
    "dim_product",
    metadata,
    Column("product_id",   Integer,      primary_key=True),
    Column("product_name", String(200),  nullable=False),
    Column("category",     String(200),  nullable=False),
    Column("price",        Numeric(10, 2), nullable=False),
)

dim_customer = Table(
    "dim_customer",
    metadata,
    Column("customer_id",    Integer,     primary_key=True),
    Column("customer_name",  String(200), nullable=False),
    Column("customer_email", String(200), nullable=False),
    Column("city",           String(200)),
    Column("country",        String(200)),
    Column("is_corporate",   Boolean,     default=False),
)

dim_date = Table(
    "dim_date",
    metadata,
    # Primary key in YYYYMMDD integer format for fast joins
    Column("date_id",     Integer, primary_key=True),
    Column("date",        Date,    nullable=False, unique=True),
    Column("day",         Integer, nullable=False),
    Column("month",       Integer, nullable=False),
    Column("quarter",     Integer, nullable=False),
    Column("year",        Integer, nullable=False),
    Column("day_of_week", Integer, nullable=False),
    Column("is_weekend",  Boolean, default=False),
    Column("is_holiday",  Boolean, default=False),
)

# ---------------------------------------------------------------------------
# Fact table
# ---------------------------------------------------------------------------

fact_sales = Table(
    "fact_sales",
    metadata,
    # Primary key
    Column("sale_id", Integer, primary_key=True),

    # Foreign keys (dimensions)
    Column("date_id",     Integer, ForeignKey("dim_date.date_id"),         nullable=False),
    Column("customer_id", Integer, ForeignKey("dim_customer.customer_id"), nullable=False),
    Column("product_id",  Integer, ForeignKey("dim_product.product_id"),   nullable=False),

    # Metrics (facts)
    Column("quantity",     Integer,        nullable=False),
    Column("unit_price",   Numeric(10, 2), nullable=False),
    Column("total_amount", Numeric(10, 2), nullable=False),
)


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------

def create_tables(engine: Engine) -> None:
    """
    Create all tables defined in the metadata registry if they do not exist.

    Args:
        engine (Engine): SQLAlchemy engine connected to the target database.
    """
    metadata.create_all(engine)
