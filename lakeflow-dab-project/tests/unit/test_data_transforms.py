"""
Unit tests for data transformation utilities
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from utils.data_transforms import DataTransforms, EventTransforms

@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing"""
    spark = SparkSession.builder \
        .appName("test_data_transforms") \
        .master("local[2]") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .getOrCreate()
    
    yield spark
    
    spark.stop()

@pytest.fixture
def sample_customer_data(spark):
    """Create sample customer data for testing"""
    data = [
        (1, "john.doe@example.com", "John", "Doe", "555-123-4567", "123 Main St", "Anytown", "CA", "USA", "12345", datetime(2023, 1, 15)),
        (2, "jane.smith@test.com", "Jane", "Smith", "555-987-6543", "456 Oak Ave", "Somecity", "NY", "USA", "67890", datetime(2023, 2, 20)),
        (3, "invalid-email", "Bob", "Johnson", "555-555-5555", "789 Pine Rd", "Anothercity", "TX", "USA", "11223", datetime(2023, 3, 10)),
        (4, "   alice.wonderland@magic.com   ", "  Alice  ", "  Wonderland  ", "(555) 999-8888", "101 Fantasy Blvd", "Dreamland", "CA", "USA", "33445", datetime(2023, 4, 5))
    ]
    
    schema = StructType([
        StructField("customer_id", IntegerType(), True),
        StructField("email", StringType(), True),
        StructField("first_name", StringType(), True),
        StructField("last_name", StringType(), True),
        StructField("phone", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("state", StringType(), True),
        StructField("country", StringType(), True),
        StructField("postal_code", StringType(), True),
        StructField("created_at", TimestampType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

@pytest.fixture
def sample_order_data(spark):
    """Create sample order data for testing"""
    data = [
        (1, 1, 101, 2, 29.99, 59.98, "pending", datetime(2023, 5, 1)),
        (2, 2, 102, 1, 49.99, 49.99, "shipped", datetime(2023, 5, 2)),
        (3, 1, 103, 3, 19.99, 59.97, "delivered", datetime(2023, 5, 3)),
        (4, 3, 104, 1, 99.99, 99.99, "cancelled", datetime(2023, 5, 4)),
        (5, 2, 105, 2, 15.99, 31.98, "pending", datetime(2023, 5, 5))
    ]
    
    schema = StructType([
        StructField("order_id", IntegerType(), True),
        StructField("customer_id", IntegerType(), True),
        StructField("product_id", IntegerType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("total_amount", DoubleType(), True),
        StructField("order_status", StringType(), True),
        StructField("order_date", TimestampType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

@pytest.fixture
def sample_event_data(spark):
    """Create sample event data for testing"""
    data = [
        (1, 1, "page_view", datetime(2023, 5, 1, 10, 30), {"page": "/home", "referrer": "google"}),
        (2, 1, "add_to_cart", datetime(2023, 5, 1, 10, 35), {"product_id": "101", "quantity": 1}),
        (3, 2, "search", datetime(2023, 5, 1, 11, 0), {"query": "laptop", "results": 25}),
        (4, 1, "purchase", datetime(2023, 5, 1, 11, 15), {"order_id": "123", "amount": 59.98}),
        (5, 3, "page_view", datetime(2023, 5, 1, 12, 0), {"page": "/products", "referrer": "direct"})
    ]
    
    schema = StructType([
        StructField("event_id", IntegerType(), True),
        StructField("customer_id", IntegerType(), True),
        StructField("event_type", StringType(), True),
        StructField("timestamp", TimestampType(), True),
        StructField("properties", StringType(), True)
    ])
    
    return spark.createDataFrame(data, schema)

class TestDataTransforms:
    """Test DataTransforms class"""
    
    def test_clean_email(self, spark, sample_customer_data):
        """Test email cleaning"""
        result = DataTransforms.clean_email(sample_customer_data)
        
        # Check that emails are uppercase and trimmed
        emails = result.select("email").collect()
        assert emails[0].email == "JOHN.DOE@EXAMPLE.COM"
        assert emails[3].email == "ALICE.WONDERLAND@MAGIC.COM"
    
    def test_clean_names(self, spark, sample_customer_data):
        """Test name cleaning"""
        result = DataTransforms.clean_names(sample_customer_data)
        
        # Check that names are uppercase and trimmed
        first_names = result.select("first_name").collect()
        last_names = result.select("last_name").collect()
        
        assert first_names[0].first_name == "JOHN"
        assert last_names[0].last_name == "DOE"
        assert first_names[3].first_name == "ALICE"
        assert last_names[3].last_name == "WONDERLAND"
    
    def test_validate_email_format(self, spark, sample_customer_data):
        """Test email validation"""
        result = DataTransforms.validate_email_format(sample_customer_data)
        
        validation_flags = result.select("is_valid_email").collect()
        assert validation_flags[0].is_valid_email == True  # john.doe@example.com
        assert validation_flags[1].is_valid_email == True  # jane.smith@test.com
        assert validation_flags[2].is_valid_email == False  # invalid-email
        assert validation_flags[3].is_valid_email == True  # alice.wonderland@magic.com
    
    def test_add_date_dimensions(self, spark, sample_event_data):
        """Test date dimension addition"""
        result = DataTransforms.add_date_dimensions(sample_event_data, "timestamp")
        
        # Check that new columns exist
        assert "year" in result.columns
        assert "month" in result.columns
        assert "day_of_week" in result.columns
        assert "hour" in result.columns
        assert "date_only" in result.columns
        
        # Check values
        row = result.filter(col("event_id") == 1).collect()[0]
        assert row.year == 2023
        assert row.month == 5
        assert row.hour == 10
    
    def test_calculate_customer_age(self, spark, sample_customer_data):
        """Test customer age calculation"""
        result = DataTransforms.calculate_customer_age(sample_customer_data)
        
        # Check that days_since_signup column exists and is positive
        assert "days_since_signup" in result.columns
        ages = result.select("days_since_signup").collect()
        for age in ages:
            assert age.days_since_signup >= 0
    
    def test_validate_order_amounts(self, spark, sample_order_data):
        """Test order amount validation"""
        result = DataTransforms.validate_order_amounts(sample_order_data)
        
        # Check that validation columns exist
        assert "calculated_total" in result.columns
        assert "is_valid_total" in result.columns
        
        # Check validation results
        validation_flags = result.select("is_valid_total").collect()
        for flag in validation_flags:
            assert flag.is_valid_total == True
    
    def test_add_order_metrics(self, spark, sample_order_data):
        """Test order metrics addition"""
        result = DataTransforms.add_order_metrics(sample_order_data)
        
        # Check that revenue_per_item column exists
        assert "revenue_per_item" in result.columns
        
        # Check calculated values
        row = result.filter(col("order_id") == 1).collect()[0]
        assert row.revenue_per_item == 29.99  # 59.98 / 2
    
    def test_segment_customers(self, spark):
        """Test customer segmentation"""
        # Create test data with different recency values
        data = [(1, 10), (2, 45), (3, 100)]
        schema = StructType([
            StructField("customer_id", IntegerType(), True),
            StructField("days_since_last_activity", IntegerType(), True)
        ])
        df = spark.createDataFrame(data, schema)
        
        result = DataTransforms.segment_customers(df)
        
        segments = result.select("customer_segment").collect()
        assert segments[0].customer_segment == "Active"  # 10 days
        assert segments[1].customer_segment == "At Risk"  # 45 days
        assert segments[2].customer_segment == "Inactive"  # 100 days
    
    def test_deduplicate_by_key(self, spark):
        """Test deduplication"""
        # Create test data with duplicates
        data = [
            (1, "value1", datetime(2023, 1, 1)),
            (1, "value2", datetime(2023, 1, 2)),  # Duplicate with newer date
            (2, "value3", datetime(2023, 1, 1))
        ]
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("value", StringType(), True),
            StructField("updated_at", TimestampType(), True)
        ])
        df = spark.createDataFrame(data, schema)
        
        result = DataTransforms.deduplicate_by_key(df, ["id"], ["updated_at"])
        
        # Should keep only the newer record for id=1
        assert result.count() == 2
        records = result.filter(col("id") == 1).collect()
        assert len(records) == 1
        assert records[0].value == "value2"

class TestEventTransforms:
    """Test EventTransforms class"""
    
    def test_categorize_events(self, spark, sample_event_data):
        """Test event categorization"""
        result = EventTransforms.categorize_events(sample_event_data)
        
        # Check that event_category column exists
        assert "event_category" in result.columns
        
        # Check categorization
        categories = result.select("event_category").collect()
        assert categories[0].event_category == "Engagement"  # page_view
        assert categories[1].event_category == "Consideration"  # add_to_cart
        assert categories[2].event_category == "Discovery"  # search
        assert categories[3].event_category == "Conversion"  # purchase
    
    def test_add_session_metrics(self, spark, sample_event_data):
        """Test session metrics calculation"""
        result = EventTransforms.add_session_metrics(sample_event_data)
        
        # Check that session columns exist
        session_columns = ["session_id", "session_event_count", "session_start_time", 
                          "session_end_time", "session_duration_minutes"]
        for col_name in session_columns:
            assert col_name in result.columns
        
        # Check that session IDs are generated
        session_ids = result.select("session_id").distinct().collect()
        assert len(session_ids) > 0

if __name__ == "__main__":
    pytest.main([__file__])
