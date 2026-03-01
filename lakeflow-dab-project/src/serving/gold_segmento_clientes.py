from pyspark import pipelines as dp
from pyspark.sql.functions import col, round, sum, current_timestamp

@dp.materialized_view(
    name="dsa.gold.tb_segmentos_clientes",
    comment="Tabela gold processada em PySpark com agregação de receita por segmento",
    table_properties={"quality": "gold"}
)
def gold_segmentos_clientes():
    """
    Agregação Gold utilizando Materialized View para joins e cálculos de receita.
    As dependências entre tabelas são gerenciadas automaticamente pelo Lakeflow SDP.
    """
    
    df_transacoes = spark.read.table("dsa.silver.tb_transacao")
    df_clientes = spark.read.table("dsa.silver.tb_clientes_v2")
    
    df_gold = (df_transacoes.alias("o")
        .join(df_clientes.alias("c"), col("o.customer_id") == col("c.customer_id"), "inner")
        .groupBy(
            col("c.customer_type"),
            col("c.country"),
            col("o.payment_method")
        )
        .agg(
            round(sum(col("o.total_amount")), 2).alias("total_revenue")
        )
        .withColumn("last_processed_at", current_timestamp())
    )
    
    return df_gold