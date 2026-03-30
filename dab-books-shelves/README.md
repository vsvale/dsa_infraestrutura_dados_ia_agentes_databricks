# Books and Shelves Databricks Asset Bundle (DAB)

This Databricks Asset Bundle manages the creation and population of books and shelves tables in a library management system. It's the DAB equivalent of the Terraform setup for managing database tables.

## Project Structure

```
dab-books-shelves/
├── databricks.yml              # Main DAB configuration
├── resources/
│   └── books_shelves_job.yml  # Job definitions
├── notebooks/
│   ├── 01_create_books.ipynb  # Books table creation and data
│   └── 02_create_shelves.ipynb # Shelves table creation and data
├── jobs/                       # Additional job files (if needed)
├── tests/                      # Test files
└── README.md                   # This documentation
```

## Tables

### Books Table
- **Purpose**: Stores book information with shelf relationships
- **Schema**:
  - `id` (INT, PRIMARY KEY): Unique book identifier
  - `title` (STRING): Book title
  - `author` (STRING): Book author
  - `isbn` (STRING): ISBN number
  - `publication_year` (INT): Year published
  - `shelf_id` (INT): Foreign key to shelves table
  - `created_at` (TIMESTAMP): Record creation timestamp

### Shelves Table
- **Purpose**: Stores shelf/location information
- **Schema**:
  - `id` (INT, PRIMARY KEY): Unique shelf identifier
  - `location` (STRING): Physical location description
  - `capacity` (INT): Maximum number of books
  - `category` (STRING): Shelf category (Fiction, Non-Fiction, etc.)
  - `floor_level` (INT): Floor level in library
  - `created_at` (TIMESTAMP): Record creation timestamp

## Environments

The DAB supports three environments with different configurations:

### Development (dev)
- **Mode**: development
- **Workspace**: User workspace (`/Workspace/Users/{user}/.bundle/dev/books-shelves-dab`)
- **Catalog**: `dsa`
- **Schema**: `bronze`
- **Features**: User-scoped resources, schedules paused

### Staging (staging)
- **Mode**: development
- **Workspace**: Shared workspace (`/Shared/.bundle/staging/books-shelves-dab`)
- **Catalog**: `dsa`
- **Schema**: `silver`
- **Features**: Name prefix "stg_", shared resources

### Production (prod)
- **Mode**: production
- **Workspace**: Shared workspace (`/Shared/.bundle/prod/books-shelves-dab`)
- **Catalog**: `dsa`
- **Schema**: `gold`
- **Features**: Production deployment, service principal execution

## Usage

### Prerequisites
- Databricks CLI installed and configured
- Appropriate workspace permissions
- Existing SQL Warehouse (ID: `29c4dccd4d8d7e90`)
- Unity Catalog with existing schemas

### Deployment Commands

```bash
# Validate the bundle configuration
databricks bundle validate -t dev

# Deploy to development environment
databricks bundle deploy -t dev

# Run the setup job
databricks bundle run -t dev books_shelves_setup_job

# Deploy to staging
databricks bundle deploy -t staging

# Deploy to production
databricks bundle deploy -t prod

# Destroy resources (cleanup)
databricks bundle destroy -t dev
```

### Job Execution

The bundle creates a job named `Books and Shelves Tables Setup - {environment}` that:

1. **Creates Shelves Table**: Creates the shelves table and inserts sample data
2. **Creates Books Table**: Creates the books table (depends on shelves) and inserts sample data

The job uses:
- **Compute**: New cluster with auto-scaling (1-2 workers)
- **Warehouse**: SQL Warehouse for SQL execution
- **Dependencies**: Books task depends on shelves completion
- **Parameters**: Catalog and schema passed as job parameters

## Sample Data

The bundle includes sample data for:
- **10 shelves** across different categories and floor levels
- **10 books** with various authors, publication years, and shelf assignments

## Monitoring and Validation

After deployment, validate the setup:

```sql
-- Check shelves table
SELECT * FROM dsa.bronze.shelves ORDER BY id;

-- Check books table  
SELECT * FROM dsa.bronze.books ORDER BY id;

-- Verify relationships
SELECT b.title, b.author, s.location, s.category
FROM dsa.bronze.books b
JOIN dsa.bronze.shelves s ON b.shelf_id = s.id;
```

## Configuration Variables

The DAB uses these configurable variables:
- `catalog_name`: Target catalog (default: "dsa")
- `schema_name`: Target schema (bronze/silver/gold based on environment)
- `warehouse_id`: SQL Warehouse ID for execution

## Integration with Terraform

This DAB complements the existing Terraform setup by:
- Using the same workspace and warehouse configurations
- Following similar naming conventions
- Providing a code-native alternative to infrastructure management
- Supporting the same multi-environment deployment patterns

## Best Practices

- Always validate before deployment: `databricks bundle validate -t {env}`
- Test in dev environment before staging/production
- Monitor job runs in the Databricks workspace
- Use version control for all configuration changes
- Review job logs for troubleshooting

## Troubleshooting

### Common Issues
1. **Validation Errors**: Check YAML syntax and variable references
2. **Permission Errors**: Verify workspace and catalog permissions
3. **Job Failures**: Check notebook paths and parameter passing
4. **Warehouse Issues**: Confirm warehouse is running and accessible

### Debug Commands
```bash
# Validate with debug output
databricks bundle validate -t dev --debug

# Check deployment status
databricks bundle summary -t dev

# View job run details
databricks jobs get-run --run-id {run-id}
```

## Next Steps

- Add data validation notebooks
- Implement scheduled refresh jobs
- Create analytical dashboards
- Add data quality monitoring
- Extend with additional library management features
