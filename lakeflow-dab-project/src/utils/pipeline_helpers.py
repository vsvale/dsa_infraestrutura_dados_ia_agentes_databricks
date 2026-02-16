"""
Pipeline helper functions for Lakeflow operations
Common utilities for pipeline management, monitoring, and error handling
"""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, sum, avg, max as _max, min as _min

class PipelineHelpers:
    """Helper utilities for pipeline operations"""
    
    @staticmethod
    def get_pipeline_config(spark: SparkSession, config_path: str = None) -> Dict[str, Any]:
        """Load pipeline configuration"""
        if config_path is None:
            config_path = "/dbfs/FileStore/pipeline_config.json"
        
        try:
            # Try to read from DBFS
            if spark.conf.get("spark.databricks.clusterUsageTags.clusterAllTags", "").find("job") != -1:
                config_df = spark.read.text(config_path)
                config_str = config_df.collect()[0][0]
                return json.loads(config_str)
            else:
                # Fallback to environment variables
                return {
                    "catalog": os.getenv("DATABRICKS_CATALOG", "main"),
                    "bronze_schema": os.getenv("BRONZE_SCHEMA", "bronze"),
                    "silver_schema": os.getenv("SILVER_SCHEMA", "silver"),
                    "gold_schema": os.getenv("GOLD_SCHEMA", "gold")
                }
        except Exception as e:
            print(f"Warning: Could not load pipeline config: {e}")
            return {}
    
    @staticmethod
    def create_table_if_not_exists(spark: SparkSession, table_name: str, 
                                  df: DataFrame, partition_cols: List[str] = None) -> None:
        """Create table if it doesn't exist"""
        try:
            spark.sql(f"DESCRIBE TABLE {table_name}")
            print(f"Table {table_name} already exists")
        except:
            print(f"Creating table {table_name}")
            writer = df.write.mode("overwrite")
            if partition_cols:
                writer = writer.partitionBy(*partition_cols)
            writer.saveAsTable(table_name)
    
    @staticmethod
    def get_table_stats(spark: SparkSession, table_name: str) -> Dict[str, Any]:
        """Get basic table statistics"""
        try:
            df = spark.read.table(table_name)
            
            stats = {
                "row_count": df.count(),
                "column_count": len(df.columns),
                "columns": df.columns
            }
            
            # Get table size info
            try:
                table_info = spark.sql(f"DESCRIBE EXTENDED {table_name}")
                size_info = [row for row in table_info.collect() 
                           if row.col_name == "Size"]
                if size_info:
                    stats["size"] = size_info[0].data_type
            except:
                pass
            
            return stats
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def monitor_pipeline_health(spark: SparkSession, catalog: str, 
                              schemas: List[str]) -> Dict[str, Any]:
        """Monitor pipeline health across schemas"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "schemas": {},
            "overall_status": "healthy"
        }
        
        for schema in schemas:
            schema_health = {
                "tables": {},
                "status": "healthy"
            }
            
            try:
                tables = spark.sql(f"SHOW TABLES IN {catalog}.{schema}")
                
                for table_row in tables.collect():
                    table_name = f"{catalog}.{schema}.{table_row.tableName}"
                    stats = PipelineHelpers.get_table_stats(spark, table_name)
                    
                    # Check for issues
                    if "error" in stats:
                        schema_health["status"] = "error"
                        schema_health["tables"][table_row.tableName] = {
                            "status": "error",
                            "error": stats["error"]
                        }
                    elif stats["row_count"] == 0:
                        schema_health["status"] = "warning"
                        schema_health["tables"][table_row.tableName] = {
                            "status": "warning",
                            "message": "Empty table"
                        }
                    else:
                        schema_health["tables"][table_row.tableName] = {
                            "status": "healthy",
                            "row_count": stats["row_count"],
                            "column_count": stats["column_count"]
                        }
                
            except Exception as e:
                schema_health["status"] = "error"
                schema_health["error"] = str(e)
            
            health_report["schemas"][schema] = schema_health
            
            # Update overall status
            if schema_health["status"] == "error":
                health_report["overall_status"] = "error"
            elif schema_health["status"] == "warning" and health_report["overall_status"] != "error":
                health_report["overall_status"] = "warning"
        
        return health_report
    
    @staticmethod
    def validate_data_freshness(spark: SparkSession, table_name: str, 
                               date_column: str, max_age_days: int = 2) -> Dict[str, Any]:
        """Check if table data is fresh"""
        try:
            df = spark.read.table(table_name)
            
            # Get latest date
            latest_date = df.agg({date_column: "max"}).collect()[0][0]
            
            if latest_date is None:
                return {"status": "error", "message": f"No data in {date_column}"}
            
            days_old = (datetime.now().date() - latest_date.date()).days
            
            return {
                "status": "pass" if days_old <= max_age_days else "fail",
                "latest_date": latest_date.isoformat(),
                "days_old": days_old,
                "max_age_days": max_age_days
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def log_pipeline_metrics(spark: SparkSession, metrics: Dict[str, Any], 
                           log_table: str = "pipeline_logs.pipeline_metrics") -> None:
        """Log pipeline metrics to a monitoring table"""
        try:
            # Create DataFrame from metrics
            metrics_data = [{
                "timestamp": datetime.now(),
                "pipeline_name": metrics.get("pipeline_name", "unknown"),
                "stage": metrics.get("stage", "unknown"),
                "status": metrics.get("status", "unknown"),
                "row_count": metrics.get("row_count", 0),
                "processing_time_seconds": metrics.get("processing_time_seconds", 0),
                "error_message": metrics.get("error_message", None),
                "metadata": json.dumps(metrics.get("metadata", {}))
            }]
            
            metrics_df = spark.createDataFrame(metrics_data)
            
            # Append to log table
            metrics_df.write.mode("append").saveAsTable(log_table)
            
        except Exception as e:
            print(f"Warning: Could not log pipeline metrics: {e}")

class ErrorHandlers:
    """Error handling utilities"""
    
    @staticmethod
    def handle_spark_exception(func):
        """Decorator to handle Spark exceptions"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                print(error_msg)
                # Log to monitoring system
                raise Exception(error_msg)
        return wrapper
    
    @staticmethod
    def retry_on_failure(max_retries: int = 3, delay_seconds: int = 60):
        """Decorator to retry function on failure"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay_seconds} seconds...")
                        time.sleep(delay_seconds)
            return wrapper
        return decorator

class DataQuality:
    """Data quality utilities"""
    
    @staticmethod
    def check_nulls(df: DataFrame, columns: List[str] = None) -> Dict[str, int]:
        """Check null counts in specified columns"""
        if columns is None:
            columns = df.columns
        
        null_counts = {}
        for col_name in columns:
            if col_name in df.columns:
                null_count = df.filter(col(col_name).isNull()).count()
                null_counts[col_name] = null_count
        
        return null_counts
    
    @staticmethod
    def check_duplicates(df: DataFrame, key_columns: List[str]) -> int:
        """Check for duplicate records based on key columns"""
        total_count = df.count()
        distinct_count = df.select(*key_columns).distinct().count()
        return total_count - distinct_count
    
    @staticmethod
    def check_data_ranges(df: DataFrame, column_checks: Dict[str, Dict]) -> Dict[str, Any]:
        """Check if data falls within expected ranges"""
        results = {}
        
        for col_name, check_config in column_checks.items():
            if col_name not in df.columns:
                results[col_name] = {"status": "error", "message": "Column not found"}
                continue
            
            col_df = df.select(col_name)
            
            # Min/max checks
            if "min" in check_config:
                min_val = col_df.agg({col_name: "min"}).collect()[0][0]
                if min_val < check_config["min"]:
                    results[col_name] = {"status": "fail", "message": f"Min value {min_val} < expected {check_config['min']}"}
                    continue
            
            if "max" in check_config:
                max_val = col_df.agg({col_name: "max"}).collect()[0][0]
                if max_val > check_config["max"]:
                    results[col_name] = {"status": "fail", "message": f"Max value {max_val} > expected {check_config['max']}"}
                    continue
            
            # Value set checks
            if "values" in check_config:
                invalid_count = df.filter(~col(col_name).isin(check_config["values"])).count()
                if invalid_count > 0:
                    results[col_name] = {"status": "fail", "message": f"{invalid_count} invalid values"}
                    continue
            
            results[col_name] = {"status": "pass"}
        
        return results

class PerformanceOptimizers:
    """Performance optimization utilities"""
    
    @staticmethod
    def optimize_delta_table(spark: SparkSession, table_name: str, 
                           z_order_cols: List[str] = None) -> None:
        """Optimize Delta table with Z-ordering"""
        try:
            print(f"Optimizing table: {table_name}")
            
            # Run OPTIMIZE
            spark.sql(f"OPTIMIZE {table_name}")
            
            # Run Z-order if columns specified
            if z_order_cols:
                z_order_clause = ", ".join(z_order_cols)
                spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({z_order_clause}")
            
            print(f"Table {table_name} optimized successfully")
            
        except Exception as e:
            print(f"Error optimizing table {table_name}: {e}")
    
    @staticmethod
    def vacuum_delta_table(spark: SparkSession, table_name: str, 
                          retention_hours: int = 168) -> None:
        """Vacuum Delta table to remove old files"""
        try:
            print(f"Vacuuming table: {table_name} with retention {retention_hours} hours")
            spark.sql(f"VACUUM {table_name} RETAIN {retention_hours} HOURS")
            print(f"Table {table_name} vacuumed successfully")
            
        except Exception as e:
            print(f"Error vacuuming table {table_name}: {e}")
    
    @staticmethod
    def cache_table(spark: SparkSession, table_name: str) -> None:
        """Cache table in memory"""
        try:
            df = spark.read.table(table_name)
            df.cache()
            df.count()  # Trigger caching
            print(f"Table {table_name} cached successfully")
            
        except Exception as e:
            print(f"Error caching table {table_name}: {e}")
