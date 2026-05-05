-- Data Warehouse Sales — Analytical Queries
-- sales_dw | Garcia | 2026

-- ================================================
-- Query 1: Total revenue by product category
-- ================================================
SELECT dpt.category, SUM(fct.total_amount) AS total_revenue
FROM fact_sales AS fct
INNER JOIN dim_product dpt ON fct.product_id = dpt.product_id
GROUP BY dpt.category
ORDER BY SUM(fct.total_amount) DESC;

-- ================================================
-- Query 2: Top 5 customers by revenue
-- ================================================
SELECT dc.customer_name, SUM(fct.total_amount) AS total_revenue
FROM fact_sales AS fct
INNER JOIN dim_customer dc ON fct.customer_id = dc.customer_id
GROUP BY dc.customer_name
ORDER BY SUM(fct.total_amount) DESC
LIMIT 5;

-- ================================================
-- Query 3: Monthly sales distribution (2023)
-- ================================================
SELECT dd.month, SUM(fct.total_amount) AS total_revenue
FROM fact_sales fct
INNER JOIN dim_date dd ON fct.date_id = dd.date_id
GROUP BY dd.month
ORDER BY dd.month ASC;

-- ================================================
-- Query 4: Revenue on holidays vs working days
-- ================================================
SELECT dd.is_holiday, SUM(fct.total_amount) AS total_revenue
FROM fact_sales fct
INNER JOIN dim_date dd ON fct.date_id = dd.date_id
GROUP BY dd.is_holiday
ORDER BY dd.is_holiday;