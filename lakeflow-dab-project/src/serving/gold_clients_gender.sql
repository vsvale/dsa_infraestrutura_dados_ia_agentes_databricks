CREATE MATERIALIZED VIEW dsa.gold.tb_clients_statistics_gender
COMMENT "This materialized view contains the statistics of the clients by gender"
TBLPROPERTIES(
    'delta.enableDeletionVectors' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.enableRowTracking' = 'true',
    'delta.logRetentionDuration' = '30 day',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'pipelines.channel' = 'preview',
    'quality' = 'gold'
)
 AS
SELECT
    genero,
    count(id_cliente) AS total_clientes,
    ROUND(AVG(idade),2) AS media_idade,
    COUNT(DISTINCT genero) AS count_genero_distinct,
    MIN(idade) AS menor_idade,
    MAX(idade) AS maior_idade
FROM dsa.silver.tb_clientes_join_tipos
GROUP BY genero