"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing"""
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder \
        .appName("lakeflow_tests") \
        .master("local[2]") \
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
        .config("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation", "true") \
        .getOrCreate()
    
    yield spark
    
    spark.stop()

@pytest.fixture
def sample_bronze_data(spark):
    """Create sample bronze layer data for testing"""
    data = [
        (1, 1, "page_view", "2023-05-01 10:30:00", '{"page": "/home"}'),
        (2, 1, "add_to_cart", "2023-05-01 10:35:00", '{"product_id": "101"}'),
        (3, 2, "search", "2023-05-01 11:00:00", '{"query": "laptop"}'),
        (4, 1, "purchase", "2023-05-01 11:15:00", '{"order_id": "123"}')
    ]
    
    schema = ["event_id", "customer_id", "event_type", "timestamp", "properties"]
    return spark.createDataFrame(data, schema)

@pytest.fixture
def sample_silver_data(spark):
    """Create sample silver layer data for testing"""
    data = [
        (1, 1, "PAGE_VIEW", "2023-05-01 10:30:00", '{"page": "/home"}', "2023-05-01"),
        (2, 1, "ADD_TO_CART", "2023-05-01 10:35:00", '{"product_id": "101"}', "2023-05-01"),
        (3, 2, "SEARCH", "2023-05-01 11:00:00", '{"query": "laptop"}', "2023-05-01"),
        (4, 1, "PURCHASE", "2023-05-01 11:15:00", '{"order_id": "123"}', "2023-05-01")
    ]
    
    schema = ["event_id", "customer_id", "event_type", "timestamp", "properties", "event_date"]
    return spark.createDataFrame(data, schema)
