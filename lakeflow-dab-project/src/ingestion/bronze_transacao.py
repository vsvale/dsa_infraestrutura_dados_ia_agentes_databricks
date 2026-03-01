from pyspark import pipelines as dp 
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType 
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, to_timestamp, lit 

source_schema = StructType([ 
    StructField("transaction_id", StringType(), True), 
    StructField("customer_id", IntegerType(), True), 
    StructField("product_id", IntegerType(), True), 
    StructField("quantity", IntegerType(), True), 
    StructField("total_amount", DoubleType(), True), 
    StructField("transaction_date", StringType(), True), 
    StructField("payment_method", StringType(), True), 
    StructField("store_type", StringType(), True)
]) 

@dp.table( 
    name="dsa.bronze.tb_transacao", 
    comment="Tabela bronze de transações" 
) 
def bronze_transacao(): 
    df = (spark.readStream 
        .format("cloudFiles") 
        .option("cloudFiles.format", "parquet") 
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .option("cloudFiles.rescuedDataColumn", "_rescued_data")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load("/Volumes/dsa/raw/dsa_files/cli_tran_prod/transacao/") 
    ) 
    
    return (df 
        .withColumn("file_name_raw", col("_metadata.file_path")) 
        .withColumn("ts_load_bronze", current_timestamp()) 
        .withColumn( 
            "transaction_date", 
            to_timestamp(col("transaction_date"), "yyyy-MM-dd HH:mm:ss") 
        ) 
        .withColumn( 
            "record_hash", 
            sha2( 
                concat_ws( 
                    "|", 
                    coalesce(col("transaction_id"), lit("")), 
                    coalesce(col("customer_id").cast("string"), lit("")), 
                    coalesce(col("product_id").cast("string"), lit("")), 
                    coalesce(col("quantity").cast("string"), lit("")), 
                    coalesce(col("total_amount").cast("string"), lit("")), 
                    coalesce(col("transaction_date").cast("string"), lit("")), 
                    coalesce(col("payment_method"), lit("")), 
                    coalesce(col("store_type"), lit("")) 
                ), 
                256 
            ) 
        ) 
    )