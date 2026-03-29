resource "databricks_notebook" "this" {
  for_each = var.notebooks
  
  path    = "${var.notebook_base_path}/${each.key}"
  content_base64 = base64encode(each.value.content)
  language = each.value.language
  
  depends_on = [var.catalog_name, var.schema_names]
}
