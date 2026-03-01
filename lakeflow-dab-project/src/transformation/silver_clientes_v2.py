from pyspark import pipelines as dp 
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, expr, lit 

@dp.table( 
    name="dsa.silver.tb_clientes_v2", 
    comment="Tabela silver de clientes processada incrementalmente",
    cluster_by_auto=True
) 
@dp.expect("valid_customer_id", "customer_id IS NOT NULL") 
@dp.expect("valid_email", "email IS NOT NULL") 
@dp.expect("positive_purchases", "total_purchases > 0") 
def tb_clientes_silver(): 
    df = spark.readStream.table("dsa.bronze.tb_clientes_v2") 
    
    df = (df
        .withColumn("name", expr("CASE WHEN name IS NOT NULL THEN initcap(trim(name)) ELSE 'Unknown' END")) 
        .withColumn("email", expr("CASE WHEN email IS NOT NULL THEN lower(trim(email)) ELSE NULL END")) 
        .withColumn("country", expr("CASE WHEN country IS NOT NULL THEN trim(country) ELSE 'Unknown' END")) 
        .withColumn("customer_type", expr("CASE WHEN customer_type IN ('Regular','Premium','VIP') THEN customer_type ELSE 'Unknown' END")) 
        .withColumn("age", expr("CASE WHEN age BETWEEN 18 AND 100 THEN age ELSE NULL END")) 
        .withColumn("gender", expr("CASE WHEN gender IN ('Male','Female','Other') THEN gender ELSE NULL END")) 
        .withColumn("total_purchases", expr("CASE WHEN total_purchases > 0 THEN total_purchases ELSE 0 END")) 
        .withColumn("last_updated_at", current_timestamp()) 
    )


    return (df.withColumn("record_hash", sha2(concat_ws("|", 
        coalesce(col("customer_id").cast("string"), lit("")),
        coalesce(col("name"), lit("")), 
        coalesce(col("email"), lit("")), 
        coalesce(col("country"), lit("")), 
        coalesce(col("customer_type"), lit("")), 
        coalesce(col("age").cast("string"), lit("")),
        coalesce(col("gender"), lit("")), 
        coalesce(col("total_purchases").cast("string"), lit("")),
        coalesce(col("last_updated_at").cast("string"), lit(""))
    ), 256)))