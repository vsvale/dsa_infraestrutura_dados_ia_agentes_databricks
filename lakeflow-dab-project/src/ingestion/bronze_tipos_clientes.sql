CREATE OR REFRESH STREAMING TABLE dsa.bronze.tb_tipos_clientes (
  codigo_tipo STRING NOT NULL COMMENT 'Código do tipo de cliente'
  ,desc_tipo STRING NOT NULL COMMENT 'Descrição do tipo de cliente'
  ,file_name_raw STRING NOT NULL COMMENT 'Nome do arquivo de origem'
  ,ts_load_bronze TIMESTAMP NOT NULL COMMENT 'Timestamp de carga na bronze'
  ,record_hash STRING GENERATED ALWAYS AS (sha2(concat_ws('|', coalesce(codigo_tipo, ''), coalesce(desc_tipo, '')), 256)) COMMENT 'Hash do registro para controle de integridade'
)
COMMENT 'Tabela bronze de tipos de clientes'
TBLPROPERTIES(
    'delta.enableDeletionVectors' = 'true',
    'delta.enableChangeDataFeed' = 'true',
    'delta.enableRowTracking' = 'true',
    'delta.logRetentionDuration' = '30 day',
    'delta.autoOptimize.optimizeWrite' = 'true',
    'pipelines.channel' = 'preview',
    'quality' = 'bronze'
)
  AS SELECT 
  codigo_tipo,
desc_tipo,
_metadata.file_path as file_name_raw,
current_timestamp() as ts_load_bronze
   FROM STREAM READ_FILES(
    '/Volumes/dsa/raw/dsa_files/clientes/tipos_clientes/'
    ,format => "csv"
    ,delimiter => ","
    ,header => true
    ,includeExistingFiles => true
    ,`cloudFiles.inferColumnTypes` => true
    ,`cloudFiles.schemaEvolutionMode` => 'addNewColumns'
);