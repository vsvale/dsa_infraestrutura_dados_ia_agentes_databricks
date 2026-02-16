-- Lakeflow Medallion Architecture Pipeline
-- Bronze -> Silver -> Gold layers with data quality expectations

-- Set default catalog and schema for the pipeline
USE CATALOG IDENTIFIER('${bundle.target}');
USE SCHEMA IDENTIFIER('${bundle.target}');

-- =====================================================
-- BRONZE LAYER - Raw Data Ingestion
-- =====================================================

-- Raw Events Streaming Table (Bronze)
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Raw events ingested from landing zone"
AS SELECT * FROM STREAM read_files(
  '/Volumes/${var.base_catalog}/${var.bronze_schema}/raw_events/',
  format => 'json',
  inferColumnTypes => true,
  includeExistingFiles => true,
  cloudFiles.schemaEvolutionMode => 'addNewColumns'
);

-- Raw Customers Streaming Table (Bronze)
CREATE OR REFRESH STREAMING TABLE bronze_customers
COMMENT "Raw customer data from CRM system"
AS SELECT * FROM STREAM read_files(
  '/Volumes/${var.base_catalog}/${var.bronze_schema}/raw_customers/',
  format => 'csv',
  header => true,
  inferSchema => true,
  includeExistingFiles => true
);

-- Raw Orders Streaming Table (Bronze)
CREATE OR REFRESH STREAMING TABLE bronze_orders
COMMENT "Raw order data from transaction system"
AS SELECT * FROM STREAM read_files(
  '/Volumes/${var.base_catalog}/${var.bronze_schema}/raw_orders/',
  format => 'parquet',
  includeExistingFiles => true
);

-- =====================================================
-- SILVER LAYER - Cleaned and Processed Data
-- =====================================================

-- Cleaned Events Materialized View (Silver)
CREATE OR REFRESH MATERIALIZED VIEW silver_events
COMMENT "Cleaned and validated events data"
AS SELECT 
  event_id,
  customer_id,
  event_type,
  timestamp,
  properties,
  processed_at,
  date(timestamp) as event_date
FROM LIVE.bronze_events
WHERE event_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND timestamp IS NOT NULL
  AND event_type IN ('page_view', 'purchase', 'add_to_cart', 'search');

-- Cleaned Customers Materialized View (Silver)
CREATE OR REFRESH MATERIALIZED VIEW silver_customers
COMMENT "Cleaned and standardized customer data"
AS SELECT 
  customer_id,
  upper(trim(email)) as email,
  upper(trim(first_name)) as first_name,
  upper(trim(last_name)) as last_name,
  phone,
  address,
  city,
  state,
  country,
  postal_code,
  created_at,
  updated_at,
  date(created_at) as signup_date
FROM LIVE.bronze_customers
WHERE customer_id IS NOT NULL
  AND email IS NOT NULL
  AND regexp_like(email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$');

-- Cleaned Orders Materialized View (Silver)
CREATE OR REFRESH MATERIALIZED VIEW silver_orders
COMMENT "Cleaned order data with validation"
AS SELECT 
  order_id,
  customer_id,
  product_id,
  quantity,
  unit_price,
  total_amount,
  order_status,
  order_date,
  shipped_date,
  delivered_date,
  date(order_date) as order_date_key
FROM LIVE.bronze_orders
WHERE order_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND quantity > 0
  AND unit_price > 0
  AND total_amount > 0
  AND order_status IN ('pending', 'shipped', 'delivered', 'cancelled');

-- =====================================================
-- GOLD LAYER - Business Aggregates and KPIs
-- =====================================================

-- Customer Analytics Materialized View (Gold)
CREATE OR REFRESH MATERIALIZED VIEW gold_customer_analytics
COMMENT "Customer-level analytics and metrics"
AS SELECT 
  c.customer_id,
  c.email,
  c.first_name,
  c.last_name,
  c.city,
  c.state,
  c.country,
  c.signup_date,
  COUNT(DISTINCT o.order_id) as total_orders,
  SUM(o.total_amount) as total_spent,
  AVG(o.total_amount) as avg_order_value,
  MIN(o.order_date) as first_order_date,
  MAX(o.order_date) as last_order_date,
  DATEDIFF(CURRENT_DATE(), c.signup_date) as days_since_signup,
  DATEDIFF(CURRENT_DATE(), MAX(o.order_date)) as days_since_last_order,
  CASE 
    WHEN DATEDIFF(CURRENT_DATE(), MAX(o.order_date)) <= 30 THEN 'Active'
    WHEN DATEDIFF(CURRENT_DATE(), MAX(o.order_date)) <= 90 THEN 'At Risk'
    ELSE 'Inactive'
  END as customer_segment
FROM LIVE.silver_customers c
LEFT JOIN LIVE.silver_orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.email, c.first_name, c.last_name, 
         c.city, c.state, c.country, c.signup_date;

-- Daily Sales Metrics Materialized View (Gold)
CREATE OR REFRESH MATERIALIZED VIEW gold_daily_sales_metrics
COMMENT "Daily sales performance metrics"
AS SELECT 
  order_date_key,
  COUNT(DISTINCT order_id) as total_orders,
  COUNT(DISTINCT customer_id) as unique_customers,
  SUM(total_amount) as total_revenue,
  AVG(total_amount) as avg_order_value,
  SUM(quantity) as total_items_sold,
  COUNT(DISTINCT product_id) as unique_products_sold
FROM LIVE.silver_orders
WHERE order_status != 'cancelled'
GROUP BY order_date_key
ORDER BY order_date_key DESC;

-- Product Performance Materialized View (Gold)
CREATE OR REFRESH MATERIALIZED VIEW gold_product_performance
COMMENT "Product-level performance metrics"
AS SELECT 
  product_id,
  COUNT(DISTINCT order_id) as order_count,
  SUM(quantity) as total_quantity_sold,
  SUM(total_amount) as total_revenue,
  AVG(unit_price) as avg_unit_price,
  COUNT(DISTINCT customer_id) as unique_customers,
  MIN(order_date) as first_order_date,
  MAX(order_date) as last_order_date
FROM LIVE.silver_orders
WHERE order_status != 'cancelled'
GROUP BY product_id
ORDER BY total_revenue DESC;

-- =====================================================
-- DATA QUALITY EXPECTATIONS
-- =====================================================

-- Add data quality expectations to bronze tables
ALTER TABLE bronze_events 
SET TBLPROPERTIES (
  'delta.expectations.valid_event_id' = 'event_id IS NOT NULL',
  'delta.expectations.valid_customer_id' = 'customer_id IS NOT NULL',
  'delta.expectations.valid_timestamp' = 'timestamp IS NOT NULL AND timestamp > "2020-01-01"',
  'delta.expectations.valid_event_type' = 'event_type IN ("page_view", "purchase", "add_to_cart", "search")'
);

ALTER TABLE bronze_customers
SET TBLPROPERTIES (
  'delta.expectations.valid_customer_id' = 'customer_id IS NOT NULL',
  'delta.expectations.valid_email' = 'email IS NOT NULL AND regexp_like(email, "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")',
  'delta.expectations.valid_created_date' = 'created_at IS NOT NULL'
);

ALTER TABLE bronze_orders
SET TBLPROPERTIES (
  'delta.expectations.valid_order_id' = 'order_id IS NOT NULL',
  'delta.expectations.positive_amounts' = 'total_amount > 0 AND unit_price > 0 AND quantity > 0',
  'delta.expectations.valid_status' = 'order_status IN ("pending", "shipped", "delivered", "cancelled")'
);
