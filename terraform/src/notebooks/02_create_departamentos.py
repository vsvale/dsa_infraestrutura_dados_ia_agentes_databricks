# Databricks Notebook: Create Departamentos Table
# MAGIC %sql
# MAGIC -- Criar tabela de departamentos
# MAGIC CREATE OR REPLACE TABLE departamentos (
# MAGIC   id INT PRIMARY KEY,
# MAGIC   departamento STRING
# MAGIC );
# MAGIC 
# MAGIC -- Inserir dados de departamentos
# MAGIC INSERT INTO departamentos (id, departamento)
# MAGIC VALUES 
# MAGIC   (1, 'Engenharia'),
# MAGIC   (2, 'Marketing'),
# MAGIC   (3, 'Vendas'),
# MAGIC   (4, 'Recursos Humanos'),
# MAGIC   (5, 'Financeiro'),
# MAGIC   (6, 'TI'),
# MAGIC   (7, 'Operações'),
# MAGIC   (8, 'Suporte Técnico'),
# MAGIC   (9, 'Logística'),
# MAGIC   (10, 'Pesquisa & Desenvolvimento');
# MAGIC 
# MAGIC -- Consultar todos os departamentos
# MAGIC SELECT * FROM departamentos;
