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

# Create SQL execution job (uses warehouse, runs queries in order)
module "sql_execution_job" {
  source = "./modules/job"
  
  job_name = "${var.project_name}-sql-execution-${var.environment}"
  
  sql_warehouse_id = data.databricks_sql_warehouse.existing.id
  
  tags = merge(var.tags, {
    "Environment" = var.environment
    "Purpose"     = "SQLExecution"
  })
  
  depends_on = [
    data.databricks_sql_warehouse.existing
  ]
}
