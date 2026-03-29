locals {
  # Common naming convention
  prefix = "${var.project_name}-${var.environment}"
  
  # Common tags
  common_tags = merge(var.tags, {
    "Environment" = var.environment
    "Project"     = var.project_name
    "CreatedBy"   = "Terraform"
    "CreatedAt"   = timestamp()
  })
  
  # Workspace paths
  workspace_paths = {
    notebooks    = "/Shared/${var.project_name}"
    jobs         = "/Shared/${var.project_name}/jobs"
    libraries    = "/Shared/${var.project_name}/libraries"
    init_scripts = "/Shared/${var.project_name}/init_scripts"
  }
  
  # Unity Catalog full names
  catalog_name = "${var.project_name}_catalog"
  
  schemas = {
    bronze = "${local.catalog_name}.bronze"
    silver = "${local.catalog_name}.silver"
    gold   = "${local.catalog_name}.gold"
  }
}
