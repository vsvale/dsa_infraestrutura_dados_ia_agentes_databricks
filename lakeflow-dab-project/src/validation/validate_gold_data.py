# Gold Layer Data Validation
# Validates business aggregates and KPIs

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when, isnan, isnull, datediff, current_date
import sys

def validate_customer_analytics_gold(spark, catalog: str, schema: str) -> bool:
    """Validate gold customer analytics table"""
    table_name = f"{catalog}.{schema}.gold_customer_analytics"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Gold Customer Analytics row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Gold customer analytics table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("customer_id").isNull() | isnan(col("customer_id")), 1).otherwise(0)).alias("null_customer_id"),
            sum(when(col("email").isNull(), 1).otherwise(0)).alias("null_email"),
            sum(when(col("customer_segment").isNull(), 1).otherwise(0)).alias("null_segment")
        ).collect()[0]
        
        print(f"Null counts - customer_id: {null_checks.null_customer_id}, "
              f"email: {null_checks.null_email}, "
              f"segment: {null_checks.null_segment}")
        
        # Validate customer segments
        valid_segments = ["Active", "At Risk", "Inactive"]
        invalid_segments = df.filter(~col("customer_segment").isin(valid_segments)).count()
        print(f"Invalid customer segments: {invalid_segments}")
        
        # Validate numeric fields
        negative_metrics = df.filter(
            (col("total_orders") < 0) |
            (col("total_spent") < 0) |
            (col("avg_order_value") < 0) |
            (col("days_since_signup") < 0) |
            (col("days_since_last_order") < 0)
        ).count()
        print(f"Negative metric values: {negative_metrics}")
        
        # Validate business logic
        invalid_aov = df.filter(col("total_orders") > 0).filter(
            col("avg_order_value") != col("total_spent") / col("total_orders")
        ).count()
        print(f"Incorrect average order value calculations: {invalid_aov}")
        
        # Check for duplicate customers
        duplicate_customers = df.groupBy("customer_id").count().filter(col("count") > 1).count()
        print(f"Duplicate customer IDs: {duplicate_customers}")
        
        return (null_checks.null_customer_id == 0 and 
                null_checks.null_email == 0 and 
                null_checks.null_segment == 0 and
                invalid_segments == 0 and
                negative_metrics == 0 and
                invalid_aov == 0 and
                duplicate_customers == 0)
        
    except Exception as e:
        print(f"Error validating gold customer analytics: {str(e)}")
        return False

def validate_daily_sales_metrics_gold(spark, catalog: str, schema: str) -> bool:
    """Validate gold daily sales metrics table"""
    table_name = f"{catalog}.{schema}.gold_daily_sales_metrics"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Gold Daily Sales Metrics row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Gold daily sales metrics table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("order_date_key").isNull(), 1).otherwise(0)).alias("null_date"),
            sum(when(col("total_orders").isNull() | isnan(col("total_orders")), 1).otherwise(0)).alias("null_orders"),
            sum(when(col("total_revenue").isNull() | isnan(col("total_revenue")), 1).otherwise(0)).alias("null_revenue")
        ).collect()[0]
        
        print(f"Null counts - date: {null_checks.null_date}, "
              f"orders: {null_checks.null_orders}, "
              f"revenue: {null_checks.null_revenue}")
        
        # Validate numeric fields
        negative_metrics = df.filter(
            (col("total_orders") < 0) |
            (col("unique_customers") < 0) |
            (col("total_revenue") < 0) |
            (col("avg_order_value") < 0) |
            (col("total_items_sold") < 0) |
            (col("unique_products_sold") < 0)
        ).count()
        print(f"Negative metric values: {negative_metrics}")
        
        # Validate business logic
        invalid_aov = df.filter(col("total_orders") > 0).filter(
            col("avg_order_value") != col("total_revenue") / col("total_orders")
        ).count()
        print(f"Incorrect average order value calculations: {invalid_aov}")
        
        # Validate that unique customers <= total orders
        invalid_customer_ratio = df.filter(
            col("unique_customers") > col("total_orders")
        ).count()
        print(f"Invalid customer/order ratios: {invalid_customer_ratio}")
        
        # Validate that unique products <= total items sold
        invalid_product_ratio = df.filter(
            col("unique_products_sold") > col("total_items_sold")
        ).count()
        print(f"Invalid product/item ratios: {invalid_product_ratio}")
        
        # Check for duplicate dates
        duplicate_dates = df.groupBy("order_date_key").count().filter(col("count") > 1).count()
        print(f"Duplicate dates: {duplicate_dates}")
        
        return (null_checks.null_date == 0 and 
                null_checks.null_orders == 0 and 
                null_checks.null_revenue == 0 and
                negative_metrics == 0 and
                invalid_aov == 0 and
                invalid_customer_ratio == 0 and
                invalid_product_ratio == 0 and
                duplicate_dates == 0)
        
    except Exception as e:
        print(f"Error validating gold daily sales metrics: {str(e)}")
        return False

def validate_product_performance_gold(spark, catalog: str, schema: str) -> bool:
    """Validate gold product performance table"""
    table_name = f"{catalog}.{schema}.gold_product_performance"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Gold Product Performance row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Gold product performance table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("product_id").isNull() | isnan(col("product_id")), 1).otherwise(0)).alias("null_product_id"),
            sum(when(col("order_count").isNull() | isnan(col("order_count")), 1).otherwise(0)).alias("null_orders"),
            sum(when(col("total_revenue").isNull() | isnan(col("total_revenue")), 1).otherwise(0)).alias("null_revenue")
        ).collect()[0]
        
        print(f"Null counts - product_id: {null_checks.null_product_id}, "
              f"orders: {null_checks.null_orders}, "
              f"revenue: {null_checks.null_revenue}")
        
        # Validate numeric fields
        negative_metrics = df.filter(
            (col("order_count") < 0) |
            (col("total_quantity_sold") < 0) |
            (col("total_revenue") < 0) |
            (col("avg_unit_price") < 0) |
            (col("unique_customers") < 0)
        ).count()
        print(f"Negative metric values: {negative_metrics}")
        
        # Validate business logic
        invalid_avg_price = df.filter(col("total_quantity_sold") > 0).filter(
            col("avg_unit_price") != col("total_revenue") / col("total_quantity_sold")
        ).count()
        print(f"Incorrect average unit price calculations: {invalid_avg_price}")
        
        # Validate that unique customers <= order count
        invalid_customer_ratio = df.filter(
            col("unique_customers") > col("order_count")
        ).count()
        print(f"Invalid customer/order ratios: {invalid_customer_ratio}")
        
        # Check for duplicate products
        duplicate_products = df.groupBy("product_id").count().filter(col("count") > 1).count()
        print(f"Duplicate product IDs: {duplicate_products}")
        
        return (null_checks.null_product_id == 0 and 
                null_checks.null_orders == 0 and 
                null_checks.null_revenue == 0 and
                negative_metrics == 0 and
                invalid_avg_price == 0 and
                invalid_customer_ratio == 0 and
                duplicate_products == 0)
        
    except Exception as e:
        print(f"Error validating gold product performance: {str(e)}")
        return False

def validate_data_freshness(spark, catalog: str, schema: str) -> bool:
    """Validate data freshness across gold tables"""
    try:
        # Check daily sales metrics freshness
        daily_sales = spark.read.table(f"{catalog}.{schema}.gold_daily_sales_metrics")
        latest_date = daily_sales.agg({"order_date_key": "max"}).collect()[0][0]
        days_old = datediff(current_date(), latest_date)
        
        print(f"Daily sales metrics latest date: {latest_date} ({days_old} days old)")
        
        # Data should be no more than 2 days old
        is_fresh = days_old <= 2
        print(f"Data freshness check: {'✅ PASS' if is_fresh else '❌ FAIL'}")
        
        return is_fresh
        
    except Exception as e:
        print(f"Error checking data freshness: {str(e)}")
        return False

def main():
    """Main validation function"""
    # Get parameters from Databricks job
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    
    print(f"Validating gold layer for {catalog}.{schema}")
    
    # Run all validations
    results = []
    results.append(validate_customer_analytics_gold(spark, catalog, schema))
    results.append(validate_daily_sales_metrics_gold(spark, catalog, schema))
    results.append(validate_product_performance_gold(spark, catalog, schema))
    results.append(validate_data_freshness(spark, catalog, schema))
    
    # Overall result
    all_passed = all(results)
    
    if all_passed:
        print("✅ All gold layer validations passed!")
    else:
        print("❌ Some gold layer validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
