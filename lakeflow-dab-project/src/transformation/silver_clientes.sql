CREATE OR REFRESH STREAMING TABLE dsa.silver.tb_clientes (
  id_cliente STRING NOT NULL COMMENT 'Identificador único do cliente',
  nome STRING NOT NULL COMMENT 'Nome do cliente',
  idade INT NOT NULL COMMENT 'Idade do cliente',
  genero STRING COMMENT 'Gênero do cliente',
  endereco STRING COMMENT 'Endereço do cliente',
  numero_contato STRING COMMENT 'Número de contato do cliente',
  data_cadastro DATE COMMENT 'Data de cadastro do cliente',
  tipo_cliente STRING COMMENT 'Tipo de cliente',
  file_name_raw STRING NOT NULL COMMENT 'Nome do arquivo de origem',
  ts_load_bronze TIMESTAMP NOT NULL COMMENT 'Timestamp de carga na bronze',
  ts_load_silver TIMESTAMP NOT NULL COMMENT 'Timestamp de carga na silver',
  record_hash STRING GENERATED ALWAYS AS (sha2(concat_ws('|', coalesce(id_cliente, ''), coalesce(nome, ''), coalesce(idade, ''), coalesce(genero, ''), coalesce(endereco, ''), coalesce(numero_contato, ''), coalesce(data_cadastro, ''), coalesce(tipo_cliente, '')), 256)) COMMENT 'Hash do registro para controle de integridade'
  ,CONSTRAINT valid_id_cliente EXPECT (id_cliente IS NOT NULL AND length(id_cliente) > 0) ON VIOLATION DROP ROW
  ,CONSTRAINT valid_nome EXPECT (nome IS NOT NULL AND length(nome) > 0) ON VIOLATION DROP ROW
  ,CONSTRAINT valid_idade EXPECT (idade > 0 AND idade <= 120) ON VIOLATION DROP ROW
  ,CONSTRAINT valid_genero EXPECT (genero IS NULL OR upper(genero) IN ('M','F'))
  ,CONSTRAINT valid_data_cadastro EXPECT (data_cadastro IS NULL OR (data_cadastro >= DATE '1900-01-01' AND data_cadastro <= current_date())) ON VIOLATION DROP ROW
  ,CONSTRAINT pk_tb_clientes PRIMARY KEY (id_cliente)
  ,CONSTRAINT fk_clientes_tipo FOREIGN KEY (tipo_cliente) REFERENCES dsa.silver.tb_tipos_clientes(codigo_tipo)
)
COMMENT 'Tabela silver de clientes'
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
trim(id_cliente) as id_cliente,
trim(nome) as nome,
CAST(idade AS INT) as idade,
trim(genero) as genero,
trim(endereco) as endereco,
trim(numero_contato) as numero_contato,
CAST(data_cadastro AS DATE) as data_cadastro,
trim(tipo_cliente) as tipo_cliente,
file_name_raw,
ts_load_bronze,
current_timestamp() as ts_load_silver
FROM STREAM dsa.bronze.tb_clientes;