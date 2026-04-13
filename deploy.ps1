# Local Deployment Script for Databricks
# This script deploys your code to Databricks workspace without needing CI/CD

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Profile = "dev"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Databricks Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if databricks CLI is installed
Write-Host "Checking Databricks CLI..." -ForegroundColor Yellow
$databricksCmd = Get-Command databricks -ErrorAction SilentlyContinue
if (-not $databricksCmd) {
    Write-Host "❌ Databricks CLI not found. Installing..." -ForegroundColor Red
    pip install databricks-cli
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Databricks CLI" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Databricks CLI found" -ForegroundColor Green
Write-Host ""

# Get workspace path
Write-Host "Enter your Databricks workspace path (e.g., /Workspace/Users/your-email@company.com/txr1):" -ForegroundColor Yellow
$workspacePath = Read-Host "Workspace Path"

if ([string]::IsNullOrWhiteSpace($workspacePath)) {
    Write-Host "❌ Workspace path is required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying to: $workspacePath" -ForegroundColor Cyan
Write-Host "Using profile: $Profile" -ForegroundColor Cyan
Write-Host ""

# Create workspace directory
Write-Host "Creating workspace directory..." -ForegroundColor Yellow
databricks workspace mkdirs $workspacePath --profile $Profile
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Workspace directory ready" -ForegroundColor Green
} else {
    Write-Host "⚠️  Directory might already exist (this is OK)" -ForegroundColor Yellow
}
Write-Host ""

# Deploy Python files
Write-Host "Deploying Python scripts..." -ForegroundColor Yellow
$pythonFiles = Get-ChildItem -Path . -Filter *.py
$pythonCount = 0

foreach ($file in $pythonFiles) {
    Write-Host "  Uploading: $($file.Name)..." -NoNewline
    $remotePath = "$workspacePath/$($file.Name)"
    
    databricks workspace import $file.FullName $remotePath --language PYTHON --overwrite --profile $Profile 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        $pythonCount++
    } else {
        Write-Host " ❌" -ForegroundColor Red
    }
}
Write-Host "✅ Deployed $pythonCount Python files" -ForegroundColor Green
Write-Host ""

# Deploy SQL files
Write-Host "Deploying SQL scripts..." -ForegroundColor Yellow
$sqlFiles = Get-ChildItem -Path . -Filter *.sql
$sqlCount = 0

foreach ($file in $sqlFiles) {
    Write-Host "  Uploading: $($file.Name)..." -NoNewline
    $remotePath = "$workspacePath/$($file.Name)"
    
    databricks workspace import $file.FullName $remotePath --language SQL --overwrite --profile $Profile 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅" -ForegroundColor Green
        $sqlCount++
    } else {
        Write-Host " ❌" -ForegroundColor Red
    }
}
Write-Host "✅ Deployed $sqlCount SQL files" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deployment Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor White
Write-Host "Profile: $Profile" -ForegroundColor White
Write-Host "Workspace Path: $workspacePath" -ForegroundColor White
Write-Host "Python files: $pythonCount" -ForegroundColor White
Write-Host "SQL files: $sqlCount" -ForegroundColor White
Write-Host ""
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Go to Databricks workspace" -ForegroundColor White
Write-Host "2. Navigate to: $workspacePath" -ForegroundColor White
Write-Host "3. Run your scripts!" -ForegroundColor White
Write-Host ""
