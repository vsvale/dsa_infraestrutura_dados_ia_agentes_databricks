from pyspark import pipelines as dp 
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, expr, lit 

@dp.table( 
    name="dsa.silver.tb_produtos", 
    comment="Tabela silver de produtos processada incrementalmente com limpeza e hashing",
    cluster_by_auto=True
) 
@dp.expect_or_drop("valid_product_id", "product_id IS NOT NULL") 
@dp.expect_or_drop("valid_category", "category IS NOT NULL") 
def tb_produtos_silver(): 
    df = spark.readStream.table("dsa.bronze.tb_produtos") 
    
    df = (df
        .withColumn("brand", expr("CASE WHEN brand IS NOT NULL THEN lower(trim(brand)) ELSE 'Unknown' END")) 
        .withColumn("category", expr("CASE WHEN category IS NOT NULL THEN initcap(trim(category)) ELSE 'Unknown' END")) 
        .withColumn("name", expr("CASE WHEN name IS NOT NULL THEN initcap(trim(name)) ELSE 'Unknown' END"))
        .withColumn("price", expr("CASE WHEN price < 0 THEN 0 ELSE price END"))
        .withColumn("rating", expr("CASE WHEN rating < 0 THEN 0 WHEN rating > 5 THEN 5 ELSE rating END"))
        .withColumn("stock_quantity", expr("CASE WHEN stock_quantity > 0 OR stock_quantity IS NULL THEN coalesce(stock_quantity, 0) ELSE 0 END"))
        .withColumn("last_updated_at", current_timestamp()) 
    )

    return (df.withColumn("record_hash", sha2(concat_ws("|", 
        coalesce(col("brand"), lit("")),
        coalesce(col("category"), lit("")), 
        coalesce(col("is_active").cast("string"), lit("")),
        coalesce(col("name"), lit("")), 
        coalesce(col("price").cast("string"), lit("")),
        coalesce(col("product_id").cast("string"), lit("")),
        coalesce(col("rating").cast("string"), lit("")),
        coalesce(col("stock_quantity").cast("string"), lit("")),
        coalesce(col("last_updated_at").cast("string"), lit(""))
    ), 256)))
