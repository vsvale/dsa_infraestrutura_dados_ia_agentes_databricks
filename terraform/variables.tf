# Required
variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
  sensitive   = true
}

variable "databricks_profile" {
  description = "Databricks configuration profile from ~/.databrickscfg"
  type        = string
  default     = "DEFAULT"
}

# Optional
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "databricks-terraform"
}

# Use existing warehouse (Free Edition limitation)
variable "existing_warehouse_id" {
  description = "Existing SQL Warehouse ID (Free Edition limitation)"
  type        = string
  default     = "29c4dccd4d8d7e90"
}

# Custom Tags
variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    "Source"     = "Terraform"
    "ManagedBy"  = "Infrastructure"
  }
}
