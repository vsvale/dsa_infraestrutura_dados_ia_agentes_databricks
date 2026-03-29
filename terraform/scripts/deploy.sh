#!/bin/bash

# Databricks Terraform Deployment Script
# Usage: ./scripts/deploy.sh [environment] [action]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-dev}
ACTION=${2:-plan}
BACKEND_CONFIG=""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        print_error "Invalid environment: $ENVIRONMENT. Must be one of: dev, staging, prod"
        exit 1
    fi
    
    if [[ ! -d "environments/$ENVIRONMENT" ]]; then
        print_error "Environment directory not found: environments/$ENVIRONMENT"
        exit 1
    fi
}

# Validate action
validate_action() {
    if [[ ! "$ACTION" =~ ^(plan|apply|destroy|init|validate)$ ]]; then
        print_error "Invalid action: $ACTION. Must be one of: plan, apply, destroy, init, validate"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform CLI not found. Please install Terraform."
        exit 1
    fi
    
    # Check Databricks CLI
    if ! command -v databricks &> /dev/null; then
        print_warning "Databricks CLI not found. Some features may not work."
    fi
    
    # Check AWS CLI (for backend)
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI not found. Backend configuration may fail."
    fi
    
    print_status "Prerequisites check completed."
}

# Setup workspace
setup_workspace() {
    print_status "Setting up workspace for environment: $ENVIRONMENT"
    
    # Create workspace if it doesn't exist
    if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
        print_status "Creating new workspace: $ENVIRONMENT"
        terraform workspace new "$ENVIRONMENT"
    fi
    
    # Switch to workspace
    print_status "Switching to workspace: $ENVIRONMENT"
    terraform workspace select "$ENVIRONMENT"
}

# Initialize Terraform
init_terraform() {
    print_status "Initializing Terraform..."
    
    cd "environments/$ENVIRONMENT"
    
    # Initialize with backend configuration
    terraform init -upgrade
    
    cd ../..
}

# Validate configuration
validate_config() {
    print_status "Validating Terraform configuration..."
    
    cd "environments/$ENVIRONMENT"
    
    terraform validate
    
    cd ../..
    
    print_status "Configuration validation passed."
}

# Plan changes
plan_changes() {
    print_status "Planning Terraform changes for environment: $ENVIRONMENT"
    
    cd "environments/$ENVIRONMENT"
    
    terraform plan -var-file=terraform.tfvars -out="tfplan"
    
    cd ../..
    
    print_status "Plan created successfully."
}

# Apply changes
apply_changes() {
    print_status "Applying Terraform changes for environment: $ENVIRONMENT"
    
    cd "environments/$ENVIRONMENT"
    
    terraform apply "tfplan"
    
    cd ../..
    
    print_status "Changes applied successfully."
}

# Destroy resources
destroy_resources() {
    print_warning "Destroying all resources in environment: $ENVIRONMENT"
    print_warning "This action is irreversible!"
    
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        print_status "Destroy operation cancelled."
        exit 0
    fi
    
    cd "environments/$ENVIRONMENT"
    
    terraform destroy -var-file=terraform.tfvars
    
    cd ../..
    
    print_status "Resources destroyed successfully."
}

# Show outputs
show_outputs() {
    print_status "Terraform outputs for environment: $ENVIRONMENT"
    
    cd "environments/$ENVIRONMENT"
    
    terraform output
    
    cd ../..
}

# Main execution
main() {
    print_status "Starting Databricks Terraform deployment"
    print_status "Environment: $ENVIRONMENT"
    print_status "Action: $ACTION"
    
    # Validate inputs
    validate_environment
    validate_action
    
    # Check prerequisites
    check_prerequisites
    
    # Setup workspace
    setup_workspace
    
    # Initialize if needed
    if [[ "$ACTION" == "init" ]]; then
        init_terraform
        exit 0
    fi
    
    # Initialize Terraform
    init_terraform
    
    # Validate configuration
    validate_config
    
    # Execute action
    case $ACTION in
        "plan")
            plan_changes
            ;;
        "apply")
            plan_changes
            apply_changes
            show_outputs
            ;;
        "destroy")
            destroy_resources
            ;;
        "validate")
            print_status "Configuration already validated."
            ;;
        *)
            print_error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
    
    print_status "Deployment completed successfully!"
}

# Help function
show_help() {
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  dev       Development environment"
    echo "  staging   Staging environment"
    echo "  prod      Production environment"
    echo ""
    echo "Actions:"
    echo "  plan      Show execution plan (default)"
    echo "  apply     Apply the configuration"
    echo "  destroy   Destroy all resources"
    echo "  init      Initialize Terraform"
    echo "  validate  Validate configuration"
    echo ""
    echo "Examples:"
    echo "  $0 dev plan     # Plan changes for dev environment"
    echo "  $0 prod apply   # Apply changes to production"
    echo "  $0 staging destroy # Destroy staging resources"
}

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main
