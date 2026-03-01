CREATE OR REFRESH MATERIALIZED VIEW dsa.silver.tb_tipos_clientes (
  codigo_tipo STRING NOT NULL COMMENT 'Código do tipo de cliente'
  ,desc_tipo STRING NOT NULL COMMENT 'Descrição do tipo de cliente'
  ,file_name_raw STRING NOT NULL COMMENT 'Nome do arquivo de origem'
  ,ts_load_bronze TIMESTAMP NOT NULL COMMENT 'Timestamp de carga na bronze'
  ,ts_load_silver TIMESTAMP NOT  NULL COMMENT 'Timestamp de carga na silver'
  ,record_hash STRING GENERATED ALWAYS AS (sha2(concat_ws('|', coalesce(codigo_tipo, ''), coalesce(desc_tipo, '')), 256)) COMMENT 'Hash do registro para controle de integridade'
  ,CONSTRAINT valid_codigo_tipo  EXPECT (codigo_tipo IS NOT NULL AND length(codigo_tipo) > 0)  ON VIOLATION DROP ROW
  ,CONSTRAINT valid_desc_tipo  EXPECT (desc_tipo IS NOT NULL AND length(desc_tipo) > 0)  ON VIOLATION DROP ROW
  ,CONSTRAINT pk_tb_tipos_clientes PRIMARY KEY (codigo_tipo)
)
COMMENT 'Tabela silver de tipos de clientes'
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
  *, current_timestamp() as ts_load_silver
   FROM dsa.bronze.tb_tipos_clientes;