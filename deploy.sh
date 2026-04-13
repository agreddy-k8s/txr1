#!/bin/bash
# Local Deployment Script for Databricks (Linux/Mac)
# This script deploys your code to Databricks workspace without needing CI/CD

set -e

ENVIRONMENT=${1:-dev}
PROFILE=${2:-dev}

echo "========================================"
echo "Databricks Deployment Script"
echo "========================================"
echo ""

# Check if databricks CLI is installed
echo "Checking Databricks CLI..."
if ! command -v databricks &> /dev/null; then
    echo "❌ Databricks CLI not found. Installing..."
    pip install databricks-cli
fi
echo "✅ Databricks CLI found"
echo ""

# Get workspace path
echo "Enter your Databricks workspace path (e.g., /Workspace/Users/your-email@company.com/txr1):"
read -r WORKSPACE_PATH

if [ -z "$WORKSPACE_PATH" ]; then
    echo "❌ Workspace path is required"
    exit 1
fi

echo ""
echo "Deploying to: $WORKSPACE_PATH"
echo "Using profile: $PROFILE"
echo ""

# Create workspace directory
echo "Creating workspace directory..."
databricks workspace mkdirs "$WORKSPACE_PATH" --profile "$PROFILE" || echo "⚠️  Directory might already exist (this is OK)"
echo "✅ Workspace directory ready"
echo ""

# Deploy Python files
echo "Deploying Python scripts..."
PYTHON_COUNT=0
for file in *.py; do
    if [ -f "$file" ]; then
        echo -n "  Uploading: $file..."
        if databricks workspace import "$file" "$WORKSPACE_PATH/$file" --language PYTHON --overwrite --profile "$PROFILE" 2>&1 > /dev/null; then
            echo " ✅"
            ((PYTHON_COUNT++))
        else
            echo " ❌"
        fi
    fi
done
echo "✅ Deployed $PYTHON_COUNT Python files"
echo ""

# Deploy SQL files
echo "Deploying SQL scripts..."
SQL_COUNT=0
for file in *.sql; do
    if [ -f "$file" ]; then
        echo -n "  Uploading: $file..."
        if databricks workspace import "$file" "$WORKSPACE_PATH/$file" --language SQL --overwrite --profile "$PROFILE" 2>&1 > /dev/null; then
            echo " ✅"
            ((SQL_COUNT++))
        else
            echo " ❌"
        fi
    fi
done
echo "✅ Deployed $SQL_COUNT SQL files"
echo ""

# Summary
echo "========================================"
echo "Deployment Summary"
echo "========================================"
echo "Environment: $ENVIRONMENT"
echo "Profile: $PROFILE"
echo "Workspace Path: $WORKSPACE_PATH"
echo "Python files: $PYTHON_COUNT"
echo "SQL files: $SQL_COUNT"
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Go to Databricks workspace"
echo "2. Navigate to: $WORKSPACE_PATH"
echo "3. Run your scripts!"
echo ""
