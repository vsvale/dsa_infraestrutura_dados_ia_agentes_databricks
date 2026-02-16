"""
Data transformation utilities for Lakeflow pipeline
Reusable functions for data cleaning, validation, and enrichment
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    col, upper, trim, regexp_replace, when, 
    datediff, current_date, lit, coalesce,
    year, month, dayofweek, hour
)
from pyspark.sql.types import StringType, IntegerType, FloatType, DateType
import re

class DataTransforms:
    """Collection of reusable data transformation functions"""
    
    @staticmethod
    def clean_email(df: DataFrame, email_col: str = "email") -> DataFrame:
        """Clean and standardize email addresses"""
        return df.withColumn(
            email_col,
            upper(trim(regexp_replace(col(email_col), r'\s+', '')))
        )
    
    @staticmethod
    def clean_names(df: DataFrame, first_name_col: str = "first_name", 
                   last_name_col: str = "last_name") -> DataFrame:
        """Clean and standardize names"""
        return df.withColumn(
            first_name_col,
            upper(trim(regexp_replace(col(first_name_col), r'[^a-zA-Z\s]', '')))
        ).withColumn(
            last_name_col,
            upper(trim(regexp_replace(col(last_name_col), r'[^a-zA-Z\s]', '')))
        )
    
    @staticmethod
    def validate_email_format(df: DataFrame, email_col: str = "email") -> DataFrame:
        """Add email validation flag"""
        email_pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return df.withColumn(
            "is_valid_email",
            when(col(email_col).rlike(email_pattern), lit(True)).otherwise(lit(False))
        )
    
    @staticmethod
    def add_date_dimensions(df: DataFrame, date_col: str = "timestamp") -> DataFrame:
        """Add date dimension columns for analytics"""
        return df.withColumn("year", year(col(date_col))) \
                .withColumn("month", month(col(date_col))) \
                .withColumn("day_of_week", dayofweek(col(date_col))) \
                .withColumn("hour", hour(col(date_col))) \
                .withColumn("date_only", col(date_col).cast("date"))
    
    @staticmethod
    def calculate_customer_age(df: DataFrame, created_at_col: str = "created_at") -> DataFrame:
        """Calculate customer age in days"""
        return df.withColumn(
            "days_since_signup",
            datediff(current_date(), col(created_at_col).cast("date"))
        )
    
    @staticmethod
    def calculate_recency(df: DataFrame, last_date_col: str = "last_order_date") -> DataFrame:
        """Calculate recency in days since last activity"""
        return df.withColumn(
            "days_since_last_activity",
            when(col(last_date_col).isNotNull(), 
                 datediff(current_date(), col(last_date_col).cast("date")))
            .otherwise(lit(None))
        )
    
    @staticmethod
    def segment_customers(df: DataFrame, recency_col: str = "days_since_last_activity") -> DataFrame:
        """Segment customers based on recency"""
        return df.withColumn(
            "customer_segment",
            when(col(recency_col) <= 30, lit("Active"))
            .when(col(recency_col) <= 90, lit("At Risk"))
            .otherwise(lit("Inactive"))
        )
    
    @staticmethod
    def validate_order_amounts(df: DataFrame, quantity_col: str = "quantity",
                              unit_price_col: str = "unit_price",
                              total_amount_col: str = "total_amount") -> DataFrame:
        """Validate order amount calculations"""
        return df.withColumn(
            "calculated_total",
            col(quantity_col) * col(unit_price_col)
        ).withColumn(
            "is_valid_total",
            when(col(total_amount_col) == col("calculated_total"), lit(True))
            .otherwise(lit(False))
        )
    
    @staticmethod
    def add_order_metrics(df: DataFrame, total_amount_col: str = "total_amount",
                         quantity_col: str = "quantity") -> DataFrame:
        """Add order-level metrics"""
        return df.withColumn(
            "revenue_per_item",
            when(col(quantity_col) > 0, col(total_amount_col) / col(quantity_col))
            .otherwise(lit(0))
        )
    
    @staticmethod
    def clean_phone_numbers(df: DataFrame, phone_col: str = "phone") -> DataFrame:
        """Clean and standardize phone numbers"""
        return df.withColumn(
            phone_col,
            regexp_replace(regexp_replace(col(phone_col), r'[^\d]', ''), r'^(\d{3})(\d{3})(\d{4})$', r'(\1) \2-\3')
        )
    
    @staticmethod
    def standardize_addresses(df: DataFrame, address_cols: list = None) -> DataFrame:
        """Standardize address fields"""
        if address_cols is None:
            address_cols = ["address", "city", "state", "country"]
        
        result_df = df
        for col_name in address_cols:
            if col_name in df.columns:
                result_df = result_df.withColumn(
                    col_name,
                    upper(trim(regexp_replace(col(col_name), r'\s+', ' ')))
                )
        return result_df
    
    @staticmethod
    def add_data_quality_flags(df: DataFrame, rules: dict = None) -> DataFrame:
        """Add data quality flags based on provided rules"""
        if rules is None:
            rules = {
                "null_check": ["customer_id", "email", "created_at"],
                "positive_check": ["total_amount", "quantity"],
                "date_check": ["created_at", "updated_at"]
            }
        
        result_df = df
        
        # Null checks
        if "null_check" in rules:
            for col_name in rules["null_check"]:
                if col_name in df.columns:
                    result_df = result_df.withColumn(
                        f"is_null_{col_name}",
                        col(col_name).isNull()
                    )
        
        # Positive value checks
        if "positive_check" in rules:
            for col_name in rules["positive_check"]:
                if col_name in df.columns:
                    result_df = result_df.withColumn(
                        f"is_negative_{col_name}",
                        col(col_name) < 0
                    )
        
        # Date validity checks
        if "date_check" in rules:
            for col_name in rules["date_check"]:
                if col_name in df.columns:
                    result_df = result_df.withColumn(
                        f"is_invalid_date_{col_name}",
                        when(col(col_name).cast("date").isNull(), lit(True))
                        .otherwise(lit(False))
                    )
        
        return result_df
    
    @staticmethod
    def deduplicate_by_key(df: DataFrame, key_cols: list, 
                         order_cols: list = None) -> DataFrame:
        """Remove duplicates keeping the latest record based on order columns"""
        from pyspark.sql.window import Window
        from pyspark.sql.functions import row_number
        
        if order_cols is None:
            order_cols = ["updated_at", "created_at"]
        
        # Filter to only existing columns
        valid_order_cols = [col for col in order_cols if col in df.columns]
        
        window_spec = Window.partitionBy(*key_cols).orderBy(*valid_order_cols)
        
        return df.withColumn("rn", row_number().over(window_spec)) \
                .filter(col("rn") == 1) \
                .drop("rn")
    
    @staticmethod
    def calculate_running_totals(df: DataFrame, group_cols: list, 
                               value_col: str, order_col: str) -> DataFrame:
        """Calculate running totals within groups"""
        from pyspark.sql.window import Window
        from pyspark.sql.functions import sum as _sum
        
        window_spec = Window.partitionBy(*group_cols).orderBy(order_col) \
                           .rowsBetween(Window.unboundedPreceding, Window.currentRow)
        
        return df.withColumn(
            f"running_total_{value_col}",
            _sum(col(value_col)).over(window_spec)
        )
    
    @staticmethod
    def add_percentile_ranks(df: DataFrame, group_cols: list, 
                           value_col: str) -> DataFrame:
        """Add percentile ranks within groups"""
        from pyspark.sql.window import Window
        from pyspark.sql.functions import percent_rank
        
        window_spec = Window.partitionBy(*group_cols).orderBy(col(value_col).desc())
        
        return df.withColumn(
            f"percentile_rank_{value_col}",
            percent_rank().over(window_spec)
        )

class EventTransforms:
    """Specialized transforms for event data"""
    
    @staticmethod
    def categorize_events(df: DataFrame, event_type_col: str = "event_type") -> DataFrame:
        """Categorize events into broader groups"""
        return df.withColumn(
            "event_category",
            when(col(event_type_col).isin(["page_view"]), lit("Engagement"))
            .when(col(event_type_col).isin(["add_to_cart"]), lit("Consideration"))
            .when(col(event_type_col).isin(["purchase"]), lit("Conversion"))
            .when(col(event_type_col).isin(["search"]), lit("Discovery"))
            .otherwise(lit("Other"))
        )
    
    @staticmethod
    def add_session_metrics(df: DataFrame, session_window_minutes: int = 30) -> DataFrame:
        """Add session-level metrics from event data"""
        from pyspark.sql.window import Window
        from pyspark.sql.functions import lag, unix_timestamp, min as _min, max as _max
        
        # Sort by customer and timestamp
        df_sorted = df.orderBy("customer_id", "timestamp")
        
        # Calculate time difference from previous event
        window_spec = Window.partitionBy("customer_id").orderBy("timestamp")
        
        df_with_session = df_sorted.withColumn(
            "prev_timestamp",
            lag("timestamp").over(window_spec)
        ).withColumn(
            "time_diff_minutes",
            when(col("prev_timestamp").isNotNull(),
                 (unix_timestamp("timestamp") - unix_timestamp("prev_timestamp")) / 60)
            .otherwise(lit(0))
        ).withColumn(
            "session_id",
            when(col("time_diff_minutes") > session_window_minutes, 
                 col("customer_id").cast("string") + "_" + unix_timestamp("timestamp").cast("string"))
            .otherwise(lag("session_id", 1, 
                          col("customer_id").cast("string") + "_" + unix_timestamp("timestamp").cast("string"))
                      .over(window_spec))
        )
        
        # Add session metrics
        session_window = Window.partitionBy("session_id")
        
        return df_with_session.withColumn(
            "session_event_count",
            count("*").over(session_window)
        ).withColumn(
            "session_start_time",
            _min("timestamp").over(session_window)
        ).withColumn(
            "session_end_time",
            _max("timestamp").over(session_window)
        ).withColumn(
            "session_duration_minutes",
            (unix_timestamp("session_end_time") - unix_timestamp("session_start_time")) / 60
        )
