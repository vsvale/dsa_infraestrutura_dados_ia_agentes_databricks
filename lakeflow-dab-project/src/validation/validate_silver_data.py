# Silver Layer Data Validation
# Validates cleaned and processed data quality

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when, isnan, isnull, datediff, current_date
import sys

def validate_events_silver(spark, catalog: str, schema: str) -> bool:
    """Validate silver events table"""
    table_name = f"{catalog}.{schema}.silver_events"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Silver Events row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Silver events table is empty")
            return False
        
        # Null checks - should be no nulls in silver layer
        null_checks = df.select(
            sum(when(col("event_id").isNull() | isnan(col("event_id")), 1).otherwise(0)).alias("null_event_id"),
            sum(when(col("customer_id").isNull() | isnan(col("customer_id")), 1).otherwise(0)).alias("null_customer_id"),
            sum(when(col("timestamp").isNull(), 1).otherwise(0)).alias("null_timestamp"),
            sum(when(col("event_type").isNull(), 1).otherwise(0)).alias("null_event_type")
        ).collect()[0]
        
        print(f"Null counts - event_id: {null_checks.null_event_id}, "
              f"customer_id: {null_checks.null_customer_id}, "
              f"timestamp: {null_checks.null_timestamp}, "
              f"event_type: {null_checks.null_event_type}")
        
        # Check for duplicate event_ids
        duplicate_events = df.groupBy("event_id").count().filter(col("count") > 1).count()
        print(f"Duplicate event IDs: {duplicate_events}")
        
        # Validate event types are standardized
        valid_event_types = ["page_view", "purchase", "add_to_cart", "search"]
        invalid_event_types = df.filter(~col("event_type").isin(valid_event_types)).count()
        print(f"Invalid event types: {invalid_event_types}")
        
        # Check event_date consistency
        inconsistent_dates = df.filter(col("event_date") != col("timestamp").cast("date")).count()
        print(f"Inconsistent event_date: {inconsistent_dates}")
        
        return (null_checks.null_event_id == 0 and 
                null_checks.null_customer_id == 0 and 
                null_checks.null_timestamp == 0 and 
                null_checks.null_event_type == 0 and
                duplicate_events == 0 and
                invalid_event_types == 0 and
                inconsistent_dates == 0)
        
    except Exception as e:
        print(f"Error validating silver events: {str(e)}")
        return False

def validate_customers_silver(spark, catalog: str, schema: str) -> bool:
    """Validate silver customers table"""
    table_name = f"{catalog}.{schema}.silver_customers"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Silver Customers row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Silver customers table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("customer_id").isNull() | isnan(col("customer_id")), 1).otherwise(0)).alias("null_customer_id"),
            sum(when(col("email").isNull(), 1).otherwise(0)).alias("null_email"),
            sum(when(col("first_name").isNull(), 1).otherwise(0)).alias("null_first_name"),
            sum(when(col("last_name").isNull(), 1).otherwise(0)).alias("null_last_name")
        ).collect()[0]
        
        print(f"Null counts - customer_id: {null_checks.null_customer_id}, "
              f"email: {null_checks.null_email}, "
              f"first_name: {null_checks.null_first_name}, "
              f"last_name: {null_checks.null_last_name}")
        
        # Check email standardization (should be uppercase)
        non_uppercase_emails = df.filter(col("email") != upper(col("email"))).count()
        print(f"Non-uppercase emails: {non_uppercase_emails}")
        
        # Check name standardization (should be uppercase and trimmed)
        non_uppercase_first_names = df.filter(col("first_name") != upper(trim(col("first_name")))).count()
        non_uppercase_last_names = df.filter(col("last_name") != upper(trim(col("last_name")))).count()
        print(f"Non-uppercase first names: {non_uppercase_first_names}")
        print(f"Non-uppercase last names: {non_uppercase_last_names}")
        
        # Check for duplicate emails
        duplicate_emails = df.groupBy("email").count().filter(col("count") > 1).count()
        print(f"Duplicate emails: {duplicate_emails}")
        
        # Validate signup_date consistency
        inconsistent_dates = df.filter(col("signup_date") != col("created_at").cast("date")).count()
        print(f"Inconsistent signup_date: {inconsistent_dates}")
        
        return (null_checks.null_customer_id == 0 and 
                null_checks.null_email == 0 and 
                null_checks.null_first_name == 0 and 
                null_checks.null_last_name == 0 and
                non_uppercase_emails == 0 and
                non_uppercase_first_names == 0 and
                non_uppercase_last_names == 0 and
                duplicate_emails == 0 and
                inconsistent_dates == 0)
        
    except Exception as e:
        print(f"Error validating silver customers: {str(e)}")
        return False

def validate_orders_silver(spark, catalog: str, schema: str) -> bool:
    """Validate silver orders table"""
    table_name = f"{catalog}.{schema}.silver_orders"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Silver Orders row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Silver orders table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("order_id").isNull() | isnan(col("order_id")), 1).otherwise(0)).alias("null_order_id"),
            sum(when(col("customer_id").isNull() | isnan(col("customer_id")), 1).otherwise(0)).alias("null_customer_id"),
            sum(when(col("total_amount").isNull() | isnan(col("total_amount")), 1).otherwise(0)).alias("null_total_amount")
        ).collect()[0]
        
        print(f"Null counts - order_id: {null_checks.null_order_id}, "
              f"customer_id: {null_checks.null_customer_id}, "
              f"total_amount: {null_checks.null_total_amount}")
        
        # Business logic validation
        negative_amounts = df.filter(col("total_amount") <= 0).count()
        negative_quantities = df.filter(col("quantity") <= 0).count()
        negative_unit_prices = df.filter(col("unit_price") <= 0).count()
        
        print(f"Negative amounts: {negative_amounts}")
        print(f"Negative quantities: {negative_quantities}")
        print(f"Negative unit prices: {negative_unit_prices}")
        
        # Validate order status
        valid_statuses = ["pending", "shipped", "delivered", "cancelled"]
        invalid_statuses = df.filter(~col("order_status").isin(valid_statuses)).count()
        print(f"Invalid order statuses: {invalid_statuses}")
        
        # Check order_date_key consistency
        inconsistent_dates = df.filter(col("order_date_key") != col("order_date").cast("date")).count()
        print(f"Inconsistent order_date_key: {inconsistent_dates}")
        
        # Validate total_amount calculation
        incorrect_totals = df.filter(col("total_amount") != col("quantity") * col("unit_price")).count()
        print(f"Incorrect total_amount calculations: {incorrect_totals}")
        
        return (null_checks.null_order_id == 0 and 
                null_checks.null_customer_id == 0 and 
                null_checks.null_total_amount == 0 and
                negative_amounts == 0 and
                negative_quantities == 0 and
                negative_unit_prices == 0 and
                invalid_statuses == 0 and
                inconsistent_dates == 0 and
                incorrect_totals == 0)
        
    except Exception as e:
        print(f"Error validating silver orders: {str(e)}")
        return False

def main():
    """Main validation function"""
    # Get parameters from Databricks job
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    
    print(f"Validating silver layer for {catalog}.{schema}")
    
    # Run all validations
    results = []
    results.append(validate_events_silver(spark, catalog, schema))
    results.append(validate_customers_silver(spark, catalog, schema))
    results.append(validate_orders_silver(spark, catalog, schema))
    
    # Overall result
    all_passed = all(results)
    
    if all_passed:
        print("✅ All silver layer validations passed!")
    else:
        print("❌ Some silver layer validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
