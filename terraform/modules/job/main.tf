resource "databricks_job" "this" {
  name = var.job_name
  
  git_source {
    url      = "https://github.com/vsvale/dsa_infraestrutura_dados_ia_agentes_databricks.git"
    provider  = "github"
    branch   = "main"
  }
  
  task {
    task_key = "create_departamentos"
    
    notebook_task {
      notebook_path = "terraform/src/notebooks/02_create_departamentos"
      source = "GIT"
    }
  }
  
  task {
    task_key = "create_funcionarios"
    
    notebook_task {
      notebook_path = "terraform/src/notebooks/01_create_funcionarios"
      source = "GIT"
    }
    
    depends_on {
      task_key = "create_departamentos"
    }
  }
  
  tags = merge(var.tags, {
    "CreatedBy" = "Terraform"
  })
  
  queue {
    enabled = false
  }
  
  run_as {
    user_name = "viniciusdvale@gmail.com"
  }
  
  performance_target = "PERFORMANCE_OPTIMIZED"
}

# Trigger job run immediately after creation
resource "null_resource" "job_trigger" {
  depends_on = [databricks_job.this]
  
  provisioner "local-exec" {
    command = "databricks jobs run-now ${databricks_job.this.id}"
  }
}
