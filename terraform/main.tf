# Get current user information
data "databricks_current_user" "me" {}

# Use existing catalog from data sources
data "databricks_catalog" "dsa" {
  name = "dsa"
}

# Use existing schemas
data "databricks_schema" "bronze" {
  name = "dsa.bronze"
}

data "databricks_schema" "silver" {
  name = "dsa.silver"
}

data "databricks_schema" "gold" {
  name = "dsa.gold"
}

# Use existing SQL Warehouse (Free Edition limitation)
# Only one warehouse allowed, limited to 2X-Small
data "databricks_sql_warehouse" "existing" {
  id = var.existing_warehouse_id
}

# Create SQL notebooks
module "sql_notebooks" {
  source = "./modules/notebooks"
  
  notebook_base_path = "/Shared/${var.project_name}/${var.environment}"
  notebooks = {
    "create_departamentos" = {
      content = <<-EOT
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
      EOT
      language = "PYTHON"
    }
    
    "create_funcionarios" = {
      content = <<-EOT
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
      EOT
      language = "PYTHON"
    }
  }
  
  catalog_name = data.databricks_catalog.dsa.name
  schema_names = {
    bronze = data.databricks_schema.bronze.name
    silver = data.databricks_schema.silver.name
    gold   = data.databricks_schema.gold.name
  }
}

# Create SQL execution job (uses warehouse, runs queries in order)
module "sql_execution_job" {
  source = "./modules/job"
  
  job_name = "${var.project_name}-sql-execution-${var.environment}"
  
  sql_warehouse_id = data.databricks_sql_warehouse.existing.id
  notebooks = module.sql_notebooks.notebook_paths
  
  tags = merge(var.tags, {
    "Environment" = var.environment
    "Purpose"     = "SQLExecution"
  })
  
  depends_on = [
    data.databricks_sql_warehouse.existing,
    module.sql_notebooks
  ]
}
