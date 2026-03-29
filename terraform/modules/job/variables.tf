variable "job_name" {
  description = "Job name"
  type        = string
}

variable "sql_warehouse_id" {
  description = "SQL Warehouse ID for serverless compute"
  type        = string
}

variable "tags" {
  description = "Job tags"
  type        = map(string)
  default     = {}
}

variable "max_concurrent_runs" {
  description = "Maximum concurrent runs"
  type        = number
  default     = 1
}
