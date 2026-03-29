output "databricks_host" {
  description = "Databricks workspace URL"
  value       = var.databricks_host
  sensitive   = true
}

output "current_user" {
  description = "Current Databricks user"
  value       = data.databricks_current_user.me.user_name
}

output "catalog_name" {
  description = "Main catalog name"
  value       = data.databricks_catalog.dsa.name
}

output "schema_names" {
  description = "Schema names"
  value = {
    bronze = data.databricks_schema.bronze.name
    silver = data.databricks_schema.silver.name
    gold   = data.databricks_schema.gold.name
  }
}

output "sql_warehouse_id" {
  description = "SQL Warehouse ID"
  value       = data.databricks_sql_warehouse.existing.id
}

output "job_id" {
  description = "SQL execution job ID"
  value       = module.sql_execution_job.job_id
}

output "job_url" {
  description = "SQL execution job URL"
  value       = "https://${var.databricks_host}/#job/${module.sql_execution_job.job_id}"
  sensitive   = true
}

output "workspace_urls" {
  description = "Useful workspace URLs"
  value = {
    workspace    = "https://${var.databricks_host}"
    sql_warehouse = "https://${var.databricks_host}/#sql/warehouses/${data.databricks_sql_warehouse.existing.id}"
    jobs         = "https://${var.databricks_host}/#job/${module.sql_execution_job.job_id}"
    git_repo     = "https://${var.databricks_host}/#repos/viniciusdvale/dsa_infraestrutura_dados_ia_agentes_databricks"
  }
  sensitive   = true
}
