variable "warehouse_name" {
  description = "SQL Warehouse name"
  type        = string
}

variable "cluster_size" {
  description = "Cluster size (Small, Medium, Large, etc.)"
  type        = string
  default     = "Small"
}

variable "auto_stop_minutes" {
  description = "Auto-stop time in minutes"
  type        = number
  default     = 10
}

variable "tags" {
  description = "Tags for the warehouse"
  type        = map(string)
  default     = {}
}

variable "enable_photon" {
  description = "Enable Photon acceleration"
  type        = bool
  default     = true
}

variable "spot_instance_policy" {
  description = "Spot instance policy"
  type        = string
  default     = "COST_OPTIMIZED"
}
