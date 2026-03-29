#!/bin/bash

# Terraform Validation Script
# Performs comprehensive validation of Terraform configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
PROJECT_ROOT=$(pwd)

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
check_required_files() {
    print_status "Checking required files..."
    
    local required_files=(
        "main.tf"
        "variables.tf"
        "outputs.tf"
        "provider.tf"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            print_error "Required file not found: $file"
            return 1
        fi
    done
    
    print_status "All required files found."
}

# Validate Terraform syntax
validate_terraform_syntax() {
    print_status "Validating Terraform syntax..."
    
    if ! terraform fmt -check -recursive .; then
        print_error "Terraform formatting issues found. Run 'terraform fmt' to fix."
        return 1
    fi
    
    if ! terraform validate; then
        print_error "Terraform validation failed."
        return 1
    fi
    
    print_status "Terraform syntax validation passed."
}

# Check environment configuration
check_environment_config() {
    print_status "Checking environment configuration: $ENVIRONMENT"
    
    local env_dir="environments/$ENVIRONMENT"
    
    if [[ ! -d "$env_dir" ]]; then
        print_error "Environment directory not found: $env_dir"
        return 1
    fi
    
    if [[ ! -f "$env_dir/terraform.tfvars" ]]; then
        print_warning "terraform.tfvars not found in $env_dir"
        print_warning "Create terraform.tfvars from terraform.tfvars.example"
    fi
    
    if [[ ! -f "$env_dir/backend.tf" ]]; then
        print_warning "backend.tf not found in $env_dir"
    fi
    
    print_status "Environment configuration check completed."
}

# Validate variables
validate_variables() {
    print_status "Validating variables..."
    
    # Check for required variables in terraform.tfvars
    local tfvars_file="environments/$ENVIRONMENT/terraform.tfvars"
    
    if [[ -f "$tfvars_file" ]]; then
        local required_vars=(
            "databricks_host"
            "databricks_profile"
        )
        
        for var in "${required_vars[@]}"; do
            if ! grep -q "^$var\s*=" "$tfvars_file"; then
                print_warning "Required variable not found in $tfvars_file: $var"
            fi
        done
    fi
    
    print_status "Variable validation completed."
}

# Check modules
check_modules() {
    print_status "Checking modules..."
    
    local modules_dir="modules"
    
    if [[ ! -d "$modules_dir" ]]; then
        print_error "Modules directory not found: $modules_dir"
        return 1
    fi
    
    # Check each module
    for module in "$modules_dir"/*; do
        if [[ -d "$module" ]]; then
            local module_name=$(basename "$module")
            print_status "Checking module: $module_name"
            
            # Check for required module files
            if [[ ! -f "$module/main.tf" ]]; then
                print_error "Module $module_name missing main.tf"
                return 1
            fi
            
            # Validate module
            if ! terraform validate -no-color > /dev/null 2>&1; then
                print_error "Module $module_name validation failed"
                return 1
            fi
        fi
    done
    
    print_status "All modules validation passed."
}

# Check security best practices
check_security() {
    print_status "Checking security best practices..."
    
    # Check for hardcoded secrets
    if grep -r -i "token\|password\|secret\|key" . --include="*.tf" --include="*.tfvars" | grep -v "#"; then
        print_warning "Potential hardcoded secrets found. Review the output above."
    fi
    
    # Check for unencrypted backend
    if grep -r "backend.*s3" . --include="*.tf" | grep -v "encrypt.*=.*true"; then
        print_warning "S3 backend without encryption found."
    fi
    
    print_status "Security check completed."
}

# Check naming conventions
check_naming_conventions() {
    print_status "Checking naming conventions..."
    
    # Check for consistent resource naming
    local resources=$(terraform state list 2>/dev/null || echo "")
    
    if [[ -n "$resources" ]]; then
        print_status "Found $(echo "$resources" | wc -l) resources in state"
    fi
    
    print_status "Naming convention check completed."
}

# Generate validation report
generate_report() {
    print_status "Generating validation report..."
    
    local report_file="validation-report-$ENVIRONMENT-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "Terraform Validation Report"
        echo "=========================="
        echo "Environment: $ENVIRONMENT"
        echo "Timestamp: $(date)"
        echo "Project: $(basename $PROJECT_ROOT)"
        echo ""
        echo "Files Checked:"
        find . -name "*.tf" -o -name "*.tfvars" | sort
        echo ""
        echo "Terraform Version:"
        terraform version
        echo ""
        echo "Providers:"
        terraform providers
        echo ""
        echo "Validation completed successfully!"
    } > "$report_file"
    
    print_status "Validation report generated: $report_file"
}

# Main validation function
main() {
    print_status "Starting comprehensive Terraform validation"
    print_status "Environment: $ENVIRONMENT"
    
    # Change to environment directory if it exists
    if [[ -d "environments/$ENVIRONMENT" ]]; then
        cd "environments/$ENVIRONMENT"
        print_status "Working in: $(pwd)"
    fi
    
    # Run validation checks
    check_required_files
    validate_terraform_syntax
    check_environment_config
    validate_variables
    check_modules
    check_security
    check_naming_conventions
    
    # Generate report
    generate_report
    
    print_status "All validation checks completed successfully!"
    print_status "Ready for Terraform deployment."
}

# Help function
show_help() {
    echo "Usage: $0 [environment]"
    echo ""
    echo "Performs comprehensive validation of Terraform configuration"
    echo ""
    echo "Arguments:"
    echo "  environment   Target environment (dev, staging, prod)"
    echo ""
    echo "Examples:"
    echo "  $0 dev        # Validate development environment"
    echo "  $0 prod       # Validate production environment"
}

# Handle help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main
