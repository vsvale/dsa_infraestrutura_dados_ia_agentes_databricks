CREATE OR REFRESH STREAMING TABLE dsa.silver.tb_clientes_join_tipos
COMMENT 'Tabela silver join de clientes com tipo clientes'
TBLPROPERTIES(
    'delta.enableDeletionVectors' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.enableRowTracking' = 'true',
    'delta.logRetentionDuration' = '30 day',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'pipelines.channel' = 'preview',
    'quality' = 'silver'
)
AS SELECT 
c.id_cliente,
c.nome,
c.idade,
c.genero,
c.endereco,
c.numero_contato,
c.data_cadastro,
tc.desc_tipo,
current_timestamp() as ts_processed_silver
FROM STREAM dsa.silver.tb_clientes c
LEFT JOIN dsa.silver.tb_tipos_clientes tc
ON c.tipo_cliente = tc.codigo_tipo