output "warehouse_id" {
  description = "SQL Warehouse ID"
  value       = databricks_sql_warehouse.this.id
}

output "warehouse_name" {
  description = "SQL Warehouse name"
  value       = databricks_sql_warehouse.this.name
}

output "endpoint_id" {
  description = "SQL Warehouse endpoint ID"
  value       = databricks_sql_warehouse.this.endpoint_id
}
