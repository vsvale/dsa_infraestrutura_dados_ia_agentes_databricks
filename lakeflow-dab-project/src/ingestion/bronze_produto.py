from pyspark import pipelines as dp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, BooleanType, LongType 
# Added lit to imports for literal handling
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, lit 

# 1. Define the schema ONLY for the source data
source_schema = StructType([ 
    StructField("brand", StringType(), True), 
    StructField("category", StringType(), True), 
    StructField("is_active", BooleanType(), True), 
    StructField("name", StringType(), True), 
    StructField("price", DoubleType(), True), 
    StructField("product_id", LongType(), True), 
    StructField("rating", DoubleType(), True), 
    StructField("stock_quantity", StringType(), True)
])

@dp.table( 
    name="dsa.bronze.tb_produtos", 
    comment="Tabela bronze de produtos"
)
def bronze_produtos():
    checkpoint_path = "/Volumes/dsa/raw/dsa_files/checkpoints/bronze/tb_produtos"
    df = (spark.readStream 
        .format("cloudFiles") 
        .option("cloudFiles.format", "json")
        .option("cloudFiles.rescuedDataColumn", "_rescued_data")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
        .load("/Volumes/dsa/raw/dsa_files/cli_tran_prod/produto/") 
    ) 
    
    return (df 
        .withColumn("file_name_raw", col("_metadata.file_path")) 
        .withColumn("ts_load_bronze", current_timestamp()) 
        .withColumn( 
            "record_hash", 
            sha2( 
                concat_ws( 
                    "|", 
                    coalesce(col("brand"), lit("")), 
                    coalesce(col("category"), lit("")), 
                    coalesce(col("is_active").cast("string"), lit("")),
                    coalesce(col("name"), lit("")), 
                    coalesce(col("price").cast("string"), lit("")),     
                    coalesce(col("product_id").cast("string"), lit("")),
                    coalesce(col("rating").cast("string"), lit("")),
                    coalesce(col("stock_quantity"), lit("")) 
                ), 
                256 
            ) 
        ) 
    )