# Bronze Layer Data Validation
# Validates raw data quality and completeness

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, sum, when, isnan, isnull
import sys

def validate_events_bronze(spark, catalog: str, schema: str) -> bool:
    """Validate bronze events table"""
    table_name = f"{catalog}.{schema}.bronze_events"
    
    try:
        df = spark.read.table(table_name)
        
        # Basic row count check
        row_count = df.count()
        print(f"Bronze Events row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Bronze events table is empty")
            return False
        
        # Null checks
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
        
        # Validate event types
        valid_event_types = ["page_view", "purchase", "add_to_cart", "search"]
        invalid_event_types = df.filter(~col("event_type").isin(valid_event_types)).count()
        print(f"Invalid event types: {invalid_event_types}")
        
        # Data freshness check
        max_timestamp = df.agg({"timestamp": "max"}).collect()[0][0]
        print(f"Latest event timestamp: {max_timestamp}")
        
        return (null_checks.null_event_id == 0 and 
                null_checks.null_customer_id == 0 and 
                null_checks.null_timestamp == 0 and 
                null_checks.null_event_type == 0 and
                invalid_event_types == 0)
        
    except Exception as e:
        print(f"Error validating bronze events: {str(e)}")
        return False

def validate_customers_bronze(spark, catalog: str, schema: str) -> bool:
    """Validate bronze customers table"""
    table_name = f"{catalog}.{schema}.bronze_customers"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Bronze Customers row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Bronze customers table is empty")
            return False
        
        # Null checks
        null_checks = df.select(
            sum(when(col("customer_id").isNull() | isnan(col("customer_id")), 1).otherwise(0)).alias("null_customer_id"),
            sum(when(col("email").isNull(), 1).otherwise(0)).alias("null_email"),
            sum(when(col("created_at").isNull(), 1).otherwise(0)).alias("null_created_at")
        ).collect()[0]
        
        print(f"Null counts - customer_id: {null_checks.null_customer_id}, "
              f"email: {null_checks.null_email}, "
              f"created_at: {null_checks.null_created_at}")
        
        # Email format validation
        import re
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        
        # Create a temporary view for SQL validation
        df.createOrReplaceTempView("temp_customers")
        invalid_emails = spark.sql(f"""
            SELECT COUNT(*) as invalid_count
            FROM temp_customers
            WHERE email IS NULL OR NOT regexp_like(email, '{email_pattern}')
        """).collect()[0].invalid_count
        
        print(f"Invalid email formats: {invalid_emails}")
        
        return (null_checks.null_customer_id == 0 and 
                null_checks.null_email == 0 and 
                null_checks.null_created_at == 0 and
                invalid_emails == 0)
        
    except Exception as e:
        print(f"Error validating bronze customers: {str(e)}")
        return False

def validate_orders_bronze(spark, catalog: str, schema: str) -> bool:
    """Validate bronze orders table"""
    table_name = f"{catalog}.{schema}.bronze_orders"
    
    try:
        df = spark.read.table(table_name)
        
        row_count = df.count()
        print(f"Bronze Orders row count: {row_count}")
        
        if row_count == 0:
            print("WARNING: Bronze orders table is empty")
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
        
        # Business logic checks
        negative_amounts = df.filter(col("total_amount") <= 0).count()
        negative_quantities = df.filter(col("quantity") <= 0).count()
        
        print(f"Negative amounts: {negative_amounts}")
        print(f"Negative quantities: {negative_quantities}")
        
        return (null_checks.null_order_id == 0 and 
                null_checks.null_customer_id == 0 and 
                null_checks.null_total_amount == 0 and
                negative_amounts == 0 and
                negative_quantities == 0)
        
    except Exception as e:
        print(f"Error validating bronze orders: {str(e)}")
        return False

def main():
    """Main validation function"""
    # Get parameters from Databricks job
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    
    print(f"Validating bronze layer for {catalog}.{schema}")
    
    # Run all validations
    results = []
    results.append(validate_events_bronze(spark, catalog, schema))
    results.append(validate_customers_bronze(spark, catalog, schema))
    results.append(validate_orders_bronze(spark, catalog, schema))
    
    # Overall result
    all_passed = all(results)
    
    if all_passed:
        print("✅ All bronze layer validations passed!")
    else:
        print("❌ Some bronze layer validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
