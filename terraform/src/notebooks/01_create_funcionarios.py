# Databricks Notebook: Create Funcionarios Table
# MAGIC %sql
# MAGIC -- Criar tabela de funcionários
# MAGIC CREATE OR REPLACE TABLE funcionarios (
# MAGIC   id INT PRIMARY KEY,
# MAGIC   nome STRING
# MAGIC );
# MAGIC 
# MAGIC -- Inserir dados de funcionários
# MAGIC INSERT INTO funcionarios (id, nome)
# MAGIC VALUES 
# MAGIC   (1, 'Bob'),
# MAGIC   (2, 'Ana'),
# MAGIC   (3, 'Flavio'),
# MAGIC   (4, 'Marcelo'),
# MAGIC   (5, 'Tatiana'),
# MAGIC   (6, 'Leandro'),
# MAGIC   (7, 'Tulio'),
# MAGIC   (8, 'Edson'),
# MAGIC   (9, 'Francisco'),
# MAGIC   (10, 'Helio');
# MAGIC 
# MAGIC -- Consultar todos os funcionários
# MAGIC SELECT * FROM funcionarios;
