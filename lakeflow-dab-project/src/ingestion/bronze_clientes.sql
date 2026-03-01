CREATE OR REFRESH STREAMING TABLE dsa.bronze.tb_clientes (
  id_cliente STRING COMMENT 'Identificador único do cliente',
  nome STRING COMMENT 'Nome do cliente',
  idade INTEGER COMMENT 'Idade do cliente',
  genero STRING COMMENT 'Gênero do cliente',
  endereco STRING COMMENT 'Endereço do cliente',
  numero_contato STRING COMMENT 'Número de contato do cliente',
  data_cadastro DATE COMMENT 'Data de cadastro do cliente',
  tipo_cliente STRING COMMENT 'Tipo de cliente',
  file_name_raw STRING COMMENT 'Nome do arquivo de origem',
  ts_load_bronze TIMESTAMP COMMENT 'Timestamp de carga na bronze',
  record_hash STRING GENERATED ALWAYS AS (sha2(concat_ws('|', coalesce(id_cliente, ''), coalesce(nome, ''), coalesce(idade, ''), coalesce(genero, ''), coalesce(endereco, ''), coalesce(numero_contato, ''), coalesce(data_cadastro, ''), coalesce(tipo_cliente, '')), 256)) COMMENT 'Hash do registro para controle de integridade'
)
COMMENT 'Tabela bronze de clientes'
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
id_cliente,
nome,
idade,
genero,
endereco,
numero_contato,
data_cadastro,
tipo_cliente,
_metadata.file_path as file_name_raw,
current_timestamp() as ts_load_bronze
FROM STREAM READ_FILES(
    '/Volumes/dsa/raw/dsa_files/clientes/clientes/',
    format => "csv",
    delimiter => ",",
    header => true,
    includeExistingFiles => true,
    `cloudFiles.inferColumnTypes` => true,
    `cloudFiles.schemaEvolutionMode` => 'addNewColumns'
);