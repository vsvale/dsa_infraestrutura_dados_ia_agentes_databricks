from pyspark import pipelines as dp 
from pyspark.sql.functions import sha2, concat_ws, coalesce, current_timestamp, col, expr, lit, when, to_date, trim, initcap

@dp.table( 
    name="dsa.silver.tb_transacao", 
    comment="Tabela silver de transações processada incrementalmente com limpeza e validação", 
    cluster_by_auto=True 
) 
@dp.expect_or_drop("valid_transaction_id", "transaction_id IS NOT NULL") 
@dp.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL") 
@dp.expect_or_drop("valid_product_id", "product_id IS NOT NULL") 
@dp.expect_or_drop("not_future_date", "to_date(transaction_date, 'yyyy-MM-dd') <= current_date()")
def tb_transacoes_silver(): 
    # Leitura incremental da tabela bronze (O SDP gerencia checkpoints automaticamente)
    df = spark.readStream.table("dsa.bronze.tb_transacao") 
    
    # Transformações de limpeza e padronização baseadas no transcript
    df = (df 
        .withColumn("quantity", when(col("quantity") < 0, 0).otherwise(col("quantity")))
        .withColumn("total_amount", when(col("total_amount") < 0, 0).otherwise(col("total_amount")))
        .withColumn("transaction_date", to_date(col("transaction_date"), 'yyyy-MM-dd'))
        .withColumn("order_status", when((col("total_amount") == 0) | (col("quantity") == 0), "Cancelled").otherwise("Completed"))
        .withColumn("payment_method", coalesce(trim(col("payment_method")), lit("Unknown")))
        .withColumn("store_type", coalesce(initcap(trim(col("store_type"))), lit("Unknown")))
        .withColumn("last_updated_at", current_timestamp()) 
    ) 
 
    # Geração de hash determinístico para detecção de mudanças e integridade
    return (df.withColumn("record_hash", sha2(concat_ws("|", 
        coalesce(col("transaction_id").cast("string"), lit("")), 
        coalesce(col("customer_id").cast("string"), lit("")), 
        coalesce(col("product_id").cast("string"), lit("")), 
        coalesce(col("quantity").cast("string"), lit("")), 
        coalesce(col("total_amount").cast("string"), lit("")), 
        coalesce(col("order_status"), lit("")), 
        coalesce(col("transaction_date").cast("string"), lit("")), 
        coalesce(col("payment_method"), lit("")), 
        coalesce(col("store_type"), lit("")), 
        coalesce(col("last_updated_at").cast("string"), lit("")) 
    ), 256)))
