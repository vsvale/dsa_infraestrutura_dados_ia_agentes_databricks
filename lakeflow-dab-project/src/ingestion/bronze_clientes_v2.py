from pyspark import pipelines as dp 
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType 
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, lit

source_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("country", StringType(), True),
    StructField("customer_type", StringType(), True),
    StructField("registration_date", StringType(), True),
    StructField("age", IntegerType(), True),
    StructField("gender", StringType(), True),
    StructField("total_purchases", DoubleType(), True)
])

@dp.table( 
    name="dsa.bronze.tb_clientes_v2", 
    comment="Tabela bronze de clientes" 
) 
def bronze_clientes_v2(): 
    df = (spark.readStream 
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("delimiter", ",") 
        .option("header", True) 
        .schema(source_schema) 
        .load("/Volumes/dsa/raw/dsa_files/cli_tran_prod/cliente/")
    )

    return (df
        .withColumn("file_name_raw", col("_metadata.file_path")) 
        .withColumn("ts_load_bronze", current_timestamp()) 
        .withColumn( 
            "record_hash", 
            sha2( 
                concat_ws( 
                    "|", 
                    coalesce(col("customer_id"), lit("")),
                    coalesce(col("name"), lit("")),
                    coalesce(col("email"), lit("")),
                    coalesce(col("country"), lit("")),
                    coalesce(col("customer_type"), lit("")),
                    coalesce(col("registration_date"), lit("")),
                    coalesce(col("age").cast("string"), lit("")),
                    coalesce(col("gender"), lit("")),
                    coalesce(col("total_purchases").cast("string"), lit(""))
                ), 
                256 
            ) 
        ) 
    )