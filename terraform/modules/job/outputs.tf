output "job_id" {
  description = "Job ID"
  value       = databricks_job.this.id
}

output "job_name" {
  description = "Job name"
  value       = databricks_job.this.name
}

output "job_url" {
  description = "Job URL (requires host variable)"
  value       = databricks_job.this.url
}
