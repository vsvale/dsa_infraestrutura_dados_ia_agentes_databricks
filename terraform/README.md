# Databricks Terraform Project (Free Edition)

This project provides a complete Infrastructure as Code (IaC) solution for managing Databricks workspaces using Terraform, specifically configured for **Databricks Free Edition** with its actual limitations.

## ⚠️ Free Edition Limitations (Based on Official Documentation)

This project is configured to work within these verified constraints:

### Compute Limitations
- **Serverless compute only** - No custom compute configurations
- **SQL Warehouses**: One warehouse, limited to 2X-Small cluster size
- **Jobs**: Max of 5 concurrent job tasks per account
- **Clusters**: Limited to small cluster sizes

### Unsupported Features
- R and Scala languages
- Custom workspace storage locations
- Online tables
- Clean rooms
- Agent Bricks
- Legacy Databricks features
- Lakebase database instances

### Administrative Limitations
- **One workspace and one metastore per account**
- **No access to account console or account-level APIs**
- **No compliance enforcement, security customization, or private networking**
- **Authentication limited to email OTP, Google, Microsoft** (no SSO/SCIM)

### Additional Limitations
- No AWS access for backend storage
- No Databricks support policy or SLA
- Non-commercial use only
- Cannot become Databricks Marketplace providers

*Source: [Databricks Free Edition Limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)*

## 🏗️ Project Structure

```
terraform/
├── main.tf                    # Main resource configuration
├── variables.tf              # Input variables
├── outputs.tf                # Output values
├── provider.tf               # Provider and backend configuration
├── data.tf                   # Data sources
├── locals.tf                 # Local values and naming conventions
├── backend.tf                # Local backend configuration
├── terraform.tfvars.example  # Example variables file
├── .gitignore                # Git ignore file
├── README.md                 # This documentation
├── FREE_EDITION_NOTES.md     # Detailed limitations guide
├── modules/                  # Reusable modules
│   ├── cluster/             # Databricks cluster module
│   ├── sql_warehouse/       # SQL Warehouse module
│   ├── notebooks/           # Notebook management module
│   ├── job/                 # Job orchestration module
│   └── unity_catalog/       # Unity Catalog module
├── environments/             # Environment-specific configurations
│   ├── dev/                 # Development environment
│   ├── staging/             # Staging environment
│   └── prod/                # Production environment
└── scripts/                  # Utility scripts
    ├── deploy.sh            # Deployment script
    └── validate.sh          # Validation script
```

## 🚀 Quick Start (Free Edition)

### Prerequisites

1. **Terraform CLI** (v1.0+)
2. **Databricks CLI** and configured profile
3. **Databricks workspace** (Free Edition)
4. **Existing SQL Warehouse** ID

### Installation

1. Clone repository:
```bash
git clone <repository-url>
cd terraform
```

2. Copy and configure variables:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

3. Configure Databricks profile:
```bash
# Add to ~/.databrickscfg
[DEFAULT]
host = https://dbc-285062b2-ce3e.cloud.databricks.com
token = your-pat-token
```

4. Initialize Terraform:
```bash
terraform init
```

5. Plan and apply:
```bash
terraform plan
terraform apply
```

## 🌍 Multi-Environment Support

### Development Environment
```bash
cd environments/dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### Staging Environment
```bash
cd environments/staging
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

### Production Environment
```bash
cd environments/prod
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## 📦 Modules

### Cluster Module
Creates and manages Databricks clusters with Free Edition constraints.

**Usage:**
```hcl
module "shared_cluster" {
  source = "./modules/cluster"
  
  cluster_name            = "my-cluster"
  spark_version           = "14.3.x-scala2.12"
  node_type_id            = "i3.xlarge"
  autotermination_minutes = 20
  min_workers             = 1
  max_workers             = 2  # Free Edition limitation
}
```

### SQL Warehouse Module
References existing SQL Warehouses (cannot create new ones in Free Edition).

**Usage:**
```hcl
data "databricks_sql_warehouse" "existing" {
  id = var.existing_warehouse_id
}
```

### Notebooks Module
Creates and manages Databricks notebooks.

**Usage:**
```hcl
module "notebooks" {
  source = "./modules/notebooks"
  
  notebook_base_path = "/Shared/my-project"
  notebooks = {
    "data_processing" = {
      language = "PYTHON"
      content = <<-EOT
        print("Hello from Terraform!")
      EOT
    }
  }
}
```

### Job Module
Orchestrates automated workflows with Free Edition constraints.

**Usage:**
```hcl
module "data_pipeline" {
  source = "./modules/job"
  
  job_name = "my-data-pipeline"
  tasks = {
    "ingest" = {
      notebook_path = module.notebooks.notebook_paths["ingest"]
      cluster_key   = "job_cluster"
    }
  }
}
```

## 🔧 Configuration

### Required Variables

| Variable | Description | Type |
|----------|-------------|------|
| `databricks_host` | Databricks workspace URL | `string` |
| `databricks_profile` | Databricks CLI profile name | `string` |
| `existing_warehouse_id` | Existing SQL Warehouse ID | `string` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name | `dev` |
| `project_name` | Project name for tagging | `databricks-terraform` |
| `cluster_spark_version` | Spark version | `14.3.x-scala2.12` |
| `cluster_node_type` | Cluster node type | `i3.xlarge` |

## 🔐 Security Best Practices

1. **Never hardcode tokens** - Use environment variables or Databricks CLI profiles
2. **Use local backend** - No AWS access in Free Edition
3. **Implement least privilege** - Grant minimum necessary permissions
4. **Use Service Principals** - For CI/CD automation (when available)

### Authentication Methods

**Environment Variables:**
```bash
export DATABRICKS_HOST="https://dbc-285062b2-ce3e.cloud.databricks.com"
export DATABRICKS_TOKEN="your-pat-token"
```

**Databricks CLI Profile:**
```hcl
provider "databricks" {
  host    = var.databricks_host
  profile = var.databricks_profile
}
```

## 📊 Resources Created

This project creates the following resources (Free Edition compatible):

### Unity Catalog (Available)
- Uses existing metastore (one per account limit)
- Main catalog
- Bronze, Silver, and Gold schemas

### Compute Resources
- Shared interactive cluster (limited to small sizes)
- Job cluster for automated workloads
- **Uses existing SQL Warehouse** (2X-Small limit)

### Data Engineering Assets
- Bronze layer ingestion notebook
- Silver layer transformation notebook
- Gold layer aggregation notebook
- Automated data pipeline job (max 5 concurrent tasks)

### Workspace Organization
- Structured notebook paths
- Consistent tagging strategy
- Environment-specific configurations

## 🔄 Workflow Examples

### Data Pipeline Architecture
```
Source → Bronze → Silver → Gold
   ↓        ↓        ↓      ↓
 Ingest   Clean    Transform Aggregate
```

### Typical Workflow
1. **Bronze Layer**: Raw data ingestion with minimal transformation
2. **Silver Layer**: Data cleaning, validation, and standardization
3. **Gold Layer**: Business-ready aggregates and metrics

## 🛠️ Operations

### Common Commands

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy

# Import existing resources
terraform import databricks_cluster.this <cluster-id>

# Format code
terraform fmt

# Validate configuration
terraform validate
```

### State Management

```bash
# List workspaces
terraform workspace list

# Create new workspace
terraform workspace new dev

# Switch workspace
terraform workspace select dev

# Show state
terraform state show databricks_cluster.this
```

## 📈 Monitoring and Observability

### Resource Monitoring
- Cluster utilization metrics
- Job execution status
- SQL Warehouse performance (2X-Small limit)

### Cost Optimization
- Auto-termination settings
- Serverless compute usage
- Cluster sizing per environment

## 🧪 Testing

### Terraform Test
```hcl
# Filename: cluster_test.tftest.hcl
run "cluster_validation" {
  command = apply
  
  assert {
    condition     = databricks_cluster.this.cluster_name == var.cluster_name
    error_message = "Cluster name mismatch"
  }
}
```

### Validation Commands
```bash
# Run tests
terraform test

# Validate configuration
terraform validate
```

## 🤝 Contributing

1. Follow Terraform best practices
2. Use consistent naming conventions
3. Add appropriate tags to all resources
4. Update documentation for changes
5. Test in non-production environments first
6. Respect Free Edition limitations

## 📚 References

- [Databricks Terraform Provider](https://registry.terraform.io/providers/databricks/databricks/latest/docs)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Free Edition Limitations](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations)
- [Databricks Best Practices](https://docs.databricks.com/getting-started/index.html)

## 📞 Support

For issues and questions:
1. Check the [FREE_EDITION_NOTES.md](FREE_EDITION_NOTES.md) guide
2. Review [common issues](docs/common-issues.md)
3. Contact the data platform team

---

**Note**: Always review Terraform plans carefully before applying, especially in production environments. This project is specifically designed for Databricks Free Edition limitations.
