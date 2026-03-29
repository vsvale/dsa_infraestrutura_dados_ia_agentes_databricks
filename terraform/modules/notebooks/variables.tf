variable "notebook_base_path" {
  description = "Base path for notebooks"
  type        = string
}

variable "notebooks" {
  description = "Notebook configurations"
  type = map(object({
    content = string
    language = string
  }))
}

variable "catalog_name" {
  description = "Catalog name"
  type        = string
}

variable "schema_names" {
  description = "Schema names"
  type        = map(string)
}
