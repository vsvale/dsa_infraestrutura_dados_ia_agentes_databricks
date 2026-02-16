# Lakeflow Medallion Pipeline with Databricks Asset Bundles

A complete Lakeflow Spark Declarative Pipeline implementation using Databricks Asset Bundles (DABs) for the Medallion Architecture (Bronze → Silver → Gold layers).

## 🏗️ Architecture Overview

This project implements a robust data pipeline with the following components:

- **Bronze Layer**: Raw data ingestion with Auto Loader and data quality expectations
- **Silver Layer**: Cleaned and processed data with business logic validation
- **Gold Layer**: Business aggregates and KPIs for analytics and reporting
- **Data Quality**: Comprehensive validation across all layers
- **CI/CD**: Automated testing and deployment with GitHub Actions

## 📁 Project Structure

```
lakeflow-dab-project/
├── databricks.yml                 # Main DAB configuration
├── resources/                     # Resource definitions
│   ├── pipelines.yml             # Lakeflow pipeline configuration
│   ├── jobs.yml                  # Databricks jobs (refresh, validation)
│   └── permissions.yml           # Access control and permissions
├── src/                          # Source code
│   ├── pipelines/
│   │   └── medallion_pipeline.sql # Main pipeline logic
│   ├── validation/               # Data quality validation
│   │   ├── validate_bronze_data.py
│   │   ├── validate_silver_data.py
│   │   └── validate_gold_data.py
│   └── utils/                    # Utility modules
│       ├── __init__.py
│       ├── data_transforms.py    # Reusable transformations
│       └── pipeline_helpers.py   # Pipeline management utilities
├── tests/                        # Test suite
│   ├── unit/
│   │   └── test_data_transforms.py
│   └── conftest.py
├── .github/workflows/            # CI/CD pipelines
│   └── ci-cd.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Databricks CLI v0.218.0 or later
- Python 3.9+
- Databricks workspace with Unity Catalog enabled
- Appropriate permissions for creating catalogs, schemas, and pipelines

### 1. Configure Environment

Update the workspace URLs in `databricks.yml`:

```yaml
targets:
  dev:
    workspace:
      host: https://your-dev-workspace.cloud.databricks.com
  staging:
    workspace:
      host: https://your-staging-workspace.cloud.databricks.com
  prod:
    workspace:
      host: https://your-prod-workspace.cloud.databricks.com
```

### 2. Set Up Authentication

```bash
# Configure Databricks CLI
databricks configure --token

# Or use environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"
```

### 3. Deploy to Development

```bash
# Validate configuration
databricks bundle validate -t dev

# Deploy to development
databricks bundle deploy -t dev

# Run the pipeline
databricks bundle run pipeline_refresh_job -t dev
```

### 4. Run Data Quality Validation

```bash
databricks bundle run data_quality_validation -t dev
```

## 📊 Data Model

### Bronze Layer (Raw Data)

- **bronze_events**: Raw event data from web/mobile applications
- **bronze_customers**: Raw customer data from CRM systems
- **bronze_orders**: Raw order data from transaction systems

### Silver Layer (Cleaned Data)

- **silver_events**: Validated and standardized events
- **silver_customers**: Cleaned customer data with standardized formats
- **silver_orders**: Validated order data with business logic checks

### Gold Layer (Business Aggregates)

- **gold_customer_analytics**: Customer-level metrics and segmentation
- **gold_daily_sales_metrics**: Daily sales performance KPIs
- **gold_product_performance**: Product-level analytics

## 🔧 Configuration

### Environment Variables

The pipeline supports the following configuration variables:

```yaml
variables:
  base_catalog: "main"           # Target catalog
  bronze_schema: "bronze"        # Bronze layer schema
  silver_schema: "silver"        # Silver layer schema
  gold_schema: "gold"           # Gold layer schema
  pipeline_name: "lakeflow_medallion_pipeline"
```

### Data Quality Expectations

Each bronze table includes data quality expectations:

```sql
ALTER TABLE bronze_events 
SET TBLPROPERTIES (
  'delta.expectations.valid_event_id' = 'event_id IS NOT NULL',
  'delta.expectations.valid_customer_id' = 'customer_id IS NOT NULL',
  'delta.expectations.valid_timestamp' = 'timestamp IS NOT NULL AND timestamp > "2020-01-01"'
);
```

## 🧪 Testing

### Unit Tests

Run unit tests locally:

```bash
pip install pytest pyspark
pytest tests/unit/ -v
```

### Integration Tests

Integration tests run in the Databricks workspace:

```bash
databricks bundle run data_quality_validation -t staging
```

## 🔄 CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline:

1. **Validation**: Bundle configuration validation
2. **Unit Tests**: Local testing with pytest
3. **Security Scan**: Vulnerability scanning with Trivy
4. **Deploy to Dev**: Automatic on develop branch
5. **Deploy to Staging**: On PR to main
6. **Deploy to Production**: On merge to main

### GitHub Actions Setup

1. Add required secrets to your GitHub repository:
   - `DATABRICKS_HOST`: Databricks workspace URL
   - `DATABRICKS_TOKEN`: Databricks personal access token
   - `SLACK_WEBHOOK_URL`: Optional Slack notifications

## 📈 Monitoring

### Pipeline Health

Monitor pipeline health using the built-in validation jobs:

```bash
# Check pipeline status
databricks pipelines get <pipeline-id>

# View pipeline logs
databricks pipelines logs <pipeline-id>
```

### Data Quality Metrics

Data quality validation results are logged and can be monitored:

- Row counts per table
- Null value checks
- Business rule validation
- Data freshness checks

## 🛠️ Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feature/new-data-source

# Make changes to pipeline logic
# Update tests

# Run local tests
pytest tests/unit/ -v

# Validate bundle
databricks bundle validate -t dev
```

### 2. Testing

```bash
# Deploy to dev for testing
databricks bundle deploy -t dev

# Run validation
databricks bundle run data_quality_validation -t dev

# Test manually in Databricks workspace
```

### 3. Deployment

```bash
# Merge to develop for dev deployment
# Create PR to main for staging deployment
# Merge to main for production deployment
```

## 📚 Best Practices

### Data Quality

- Always validate data at each layer transition
- Use expectations for automated quality checks
- Monitor data freshness and completeness

### Performance

- Use Liquid Clustering for better query performance
- Enable Predictive Optimization for automatic maintenance
- Monitor job performance and optimize as needed

### Security

- Follow principle of least privilege for permissions
- Use service principals for production deployments
- Regularly audit access and permissions

### Cost Management

- Use appropriate cluster sizes for each environment
- Enable auto-termination for development clusters
- Monitor DBU consumption and optimize jobs

## 🔍 Troubleshooting

### Common Issues

1. **Pipeline Fails to Start**
   - Check workspace connectivity
   - Verify service principal permissions
   - Review pipeline configuration

2. **Data Quality Validation Fails**
   - Check source data quality
   - Review validation logic
   - Examine error logs

3. **Deployment Issues**
   - Validate bundle configuration
   - Check target workspace permissions
   - Review CI/CD logs

### Getting Help

- Check Databricks documentation for Lakeflow SDP
- Review pipeline logs in the Databricks workspace
- Monitor job runs and error messages

## 📄 License

This project is provided as an example implementation. Adapt to your specific requirements and organizational standards.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Note**: This is a template project. Customize the data models, transformations, and configurations to match your specific business requirements and data sources.
