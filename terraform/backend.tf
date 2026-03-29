# Local Backend Configuration (Free Edition limitation)
# No AWS access for remote backend
terraform {
  backend "local" {
    path = "./terraform.tfstate"
  }
}
