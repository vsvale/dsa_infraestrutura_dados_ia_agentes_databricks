CREATE OR REFRESH MATERIALIZED VIEW report_pk_dsa_silver_tb_clients(
  CONSTRAINT unique_pk EXPECT (num_entries = 1)
)
AS SELECT id_cliente, count(*) as num_entries
  FROM dsa.silver.tb_clientes
  GROUP BY id_cliente;

CREATE OR REFRESH MATERIALIZED VIEW report_pk_dsa_silver_tb_tipos_clientes(
  CONSTRAINT unique_pk EXPECT (num_entries = 1)
)
AS SELECT codigo_tipo, count(*) as num_entries
  FROM dsa.silver.tb_tipos_clientes
  GROUP BY codigo_tipo;

CREATE OR REFRESH MATERIALIZED VIEW report_fk_dsa_silver_tb_clientes(
  CONSTRAINT unique_pk EXPECT (num_entries = 0) ON VIOLATION FAIL UPDATE
)
select count(*) as num_entries from (
SELECT distinct tipo_cliente from dsa.silver.tb_clientes WHERE tipo_cliente not in (select distinct codigo_tipo from dsa.silver.tb_tipos_clientes));

CREATE OR REFRESH MATERIALIZED VIEW count_verification_tb_clientes(
  CONSTRAINT no_rows_dropped EXPECT (a_count == b_count)
) AS SELECT * FROM
  (SELECT COUNT(*) AS a_count FROM dsa.silver.tb_tipos_clientes),
  (SELECT COUNT(*) AS b_count FROM dsa.bronze.tb_tipos_clientes);