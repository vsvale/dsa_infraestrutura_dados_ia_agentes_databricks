resource "databricks_sql_warehouse" "this" {
  name         = var.warehouse_name
  cluster_size = var.cluster_size
  
  auto_stop_mins = var.auto_stop_minutes
  
  tags = merge(var.tags, {
    "CreatedBy" = "Terraform"
  })
  
  enable_photon          = var.enable_photon
  spot_instance_policy   = var.spot_instance_policy
}
