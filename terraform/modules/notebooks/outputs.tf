output "notebook_paths" {
  description = "Notebook paths"
  value = {
    for key, notebook in databricks_notebook.this : key => notebook.path
  }
}
