resource "databricks_job" "this" {
  name = var.job_name
  
  task {
    task_key = "create_departamentos"
    
    notebook_task {
      notebook_path = var.notebooks["create_departamentos"]
    }
  }
  
  task {
    task_key = "create_funcionarios"
    
    notebook_task {
      notebook_path = var.notebooks["create_funcionarios"]
    }
    
    depends_on {
      task_key = "create_departamentos"
    }
  }
  
  tags = merge(var.tags, {
    "CreatedBy" = "Terraform"
  })
}

# Trigger job run immediately after creation
resource "null_resource" "job_trigger" {
  depends_on = [databricks_job.this]
  
  provisioner "local-exec" {
    command = "databricks jobs run-now ${databricks_job.this.id}"
  }
}
