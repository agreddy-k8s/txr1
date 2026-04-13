# Azure DevOps CI/CD Setup Guide

This guide explains how to set up Azure DevOps pipelines to automatically deploy your Databricks code.

## Architecture

```
Git Push → Azure DevOps Pipeline → Validate Code → Deploy to Databricks Workspace
```

- **develop branch** → Deploys to Dev environment
- **main branch** → Deploys to Production environment

---

## Prerequisites

1. Azure DevOps organization and project
2. Databricks workspace (Dev and/or Prod)
3. Databricks personal access tokens
4. Anthropic API key (for PDF extraction)

---

## Step 1: Create Azure DevOps Project

1. Go to https://dev.azure.com
2. Create a new project (e.g., "txr1-databricks")
3. Initialize a Git repository

---

## Step 2: Push Code to Azure DevOps

### Option A: Using Git Command Line

```bash
cd c:\Users\gopal.allam\txr1

# Initialize git (if not already done)
git init

# Add Azure DevOps remote
git remote add origin https://dev.azure.com/YOUR_ORG/YOUR_PROJECT/_git/txr1

# Add all files
git add .

# Commit
git commit -m "Initial commit - RRC pipeline"

# Push to main branch
git branch -M main
git push -u origin main

# Create develop branch
git checkout -b develop
git push -u origin develop
```

### Option B: Using Visual Studio Code

1. Open Source Control panel (Ctrl+Shift+G)
2. Click "Initialize Repository"
3. Stage all changes (+ icon)
4. Commit with message
5. Click "Publish Branch" and select Azure DevOps

---

## Step 3: Create Variable Group in Azure DevOps

1. In Azure DevOps, go to **Pipelines** → **Library**
2. Click **+ Variable group**
3. Name it: `databricks-secrets`
4. Add the following variables:

### For Dev Environment:
| Variable Name | Value | Secret? |
|--------------|-------|---------|
| `DATABRICKS_HOST` | `https://your-workspace.cloud.databricks.com` | No |
| `DATABRICKS_TOKEN` | Your Databricks personal access token | **Yes** ✓ |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | **Yes** ✓ |

### For Production Environment (if separate):
| Variable Name | Value | Secret? |
|--------------|-------|---------|
| `DATABRICKS_HOST_PROD` | `https://your-prod-workspace.cloud.databricks.com` | No |
| `DATABRICKS_TOKEN_PROD` | Your Databricks prod access token | **Yes** ✓ |

5. Click **Save**

### How to Get Databricks Token:
1. In Databricks, click your profile icon (top right)
2. Go to **Settings** → **Developer**
3. Click **Manage** next to Access tokens
4. Click **Generate new token**
5. Give it a name (e.g., "Azure DevOps Pipeline")
6. Set expiration (or leave blank for no expiration)
7. Click **Generate**
8. **Copy the token immediately** (you won't see it again!)

---

## Step 4: Create Pipeline in Azure DevOps

1. In Azure DevOps, go to **Pipelines** → **Pipelines**
2. Click **New pipeline**
3. Select **Azure Repos Git**
4. Select your repository
5. Choose **Existing Azure Pipelines YAML file**
6. Select `/azure-pipelines.yml`
7. Click **Continue**
8. Review the pipeline
9. Click **Run** to test it

---

## Step 5: Create Environments

### Create Dev Environment:
1. Go to **Pipelines** → **Environments**
2. Click **New environment**
3. Name: `databricks-dev`
4. Description: "Databricks Development Environment"
5. Click **Create**

### Create Prod Environment:
1. Click **New environment**
2. Name: `databricks-prod`
3. Description: "Databricks Production Environment"
4. Click **Create**
5. Click on the environment
6. Click **⋮** (three dots) → **Approvals and checks**
7. Add **Approvals** (require manual approval before prod deployment)
8. Add approvers (e.g., your email)

---

## Step 6: Configure Pipeline Permissions

1. Go to **Pipelines** → **Pipelines**
2. Click on your pipeline
3. Click **Edit**
4. Click **⋮** (three dots) → **Triggers**
5. Enable **Continuous integration** (CI)
6. Add branch filters:
   - Include: `main`, `develop`
7. Add path filters:
   - Include: `*.sql`, `*.py`, `databricks.yml`

---

## Step 7: Test the Pipeline

### Test Dev Deployment:
```bash
# Make a change to any Python or SQL file
git checkout develop
# Edit a file
git add .
git commit -m "Test dev deployment"
git push origin develop
```

The pipeline will:
1. ✅ Validate Python syntax
2. ✅ Validate SQL syntax
3. ✅ Deploy to Databricks Dev workspace
4. ✅ Scripts available at `/Workspace/Users/your-email/txr1/`

### Test Prod Deployment:
```bash
# Merge develop to main
git checkout main
git merge develop
git push origin main
```

The pipeline will:
1. ✅ Validate code
2. ⏸️ Wait for approval (if configured)
3. ✅ Deploy to Databricks Prod workspace

---

## Pipeline Stages Explained

### Stage 1: Build and Validate
- Validates Python syntax (py_compile)
- Validates SQL syntax (sqlparse)
- Publishes artifacts for deployment

### Stage 2: Deploy to Dev
- **Trigger:** Push to `develop` branch
- Installs Databricks CLI
- Configures authentication
- Creates workspace directory
- Uploads Python scripts (`.py` files)
- Uploads SQL scripts (`.sql` files)

### Stage 3: Deploy to Prod
- **Trigger:** Push to `main` branch
- Requires manual approval (if configured)
- Same steps as Dev but to production workspace

---

## Workspace Structure After Deployment

After successful deployment, your files will be in Databricks at:

```
/Workspace/Users/your-email@company.com/txr1/
├── 01_create_schemas_and_tables.sql
├── 02_extract_pdfs_to_bronze.py
├── 03_transform_bronze_to_silver.sql
├── upload_to_volume.py
└── rrc_scraper.py
```

---

## Running the Pipeline in Databricks

After deployment, you can run the scripts:

### Option 1: Run Manually in Databricks
1. Go to Databricks Workspace
2. Navigate to `/Workspace/Users/your-email/txr1/`
3. Open `01_create_schemas_and_tables.sql`
4. Click **Run All**
5. Open `02_extract_pdfs_to_bronze.py` as a notebook
6. Set environment variables in notebook:
   ```python
   import os
   os.environ["ANTHROPIC_API_KEY"] = dbutils.secrets.get("scope", "anthropic-key")
   os.environ["DATABRICKS_WAREHOUSE_ID"] = "your-warehouse-id"
   ```
7. Run the notebook
8. Open `03_transform_bronze_to_silver.sql`
9. Click **Run All**

### Option 2: Create Databricks Job (Recommended)
1. In Databricks, go to **Workflows** → **Jobs**
2. Click **Create Job**
3. Name: "RRC PDF Extraction Pipeline"
4. Add tasks:
   - **Task 1:** SQL - `01_create_schemas_and_tables.sql`
   - **Task 2:** Python - `02_extract_pdfs_to_bronze.py` (depends on Task 1)
   - **Task 3:** SQL - `03_transform_bronze_to_silver.sql` (depends on Task 2)
5. Configure schedule (e.g., daily at 2 AM)
6. Save and run

---

## Troubleshooting

### Issue: "Variable group not found"
**Solution:** Make sure you created the variable group named exactly `databricks-secrets`

### Issue: "Authentication failed"
**Solution:** 
- Verify `DATABRICKS_HOST` is correct (include `https://`)
- Verify `DATABRICKS_TOKEN` is valid and not expired
- Check token has workspace access permissions

### Issue: "Permission denied to create workspace directory"
**Solution:** 
- Verify the token has workspace write permissions
- Try using a different workspace path

### Issue: "Pipeline fails on validation"
**Solution:**
- Check Python syntax errors in your `.py` files
- Check SQL syntax errors in your `.sql` files
- Review pipeline logs for specific error messages

### Issue: "Files not appearing in Databricks"
**Solution:**
- Check the workspace path in pipeline logs
- Verify you're looking in the correct user directory
- Refresh the Databricks workspace browser

---

## Best Practices

1. **Use Separate Environments:** Keep Dev and Prod separate
2. **Require Approvals for Prod:** Always require manual approval for production deployments
3. **Use Secrets:** Store all sensitive values (tokens, API keys) as secret variables
4. **Test in Dev First:** Always test changes in develop branch before merging to main
5. **Use Pull Requests:** Require PR reviews before merging to main
6. **Monitor Pipeline Runs:** Set up email notifications for pipeline failures
7. **Version Control:** Tag releases in Git for production deployments

---

## Advanced: Using Databricks Asset Bundles

For more advanced deployments, you can use Databricks Asset Bundles (DABs):

```bash
# Install Databricks CLI
pip install databricks-cli

# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy -t dev

# Deploy to prod
databricks bundle deploy -t prod
```

The `databricks-bundle.yml` file is already configured for this approach.

---

## Next Steps

1. ✅ Set up Azure DevOps project
2. ✅ Create variable group with secrets
3. ✅ Create environments (dev/prod)
4. ✅ Push code to Azure DevOps
5. ✅ Run pipeline
6. ✅ Verify deployment in Databricks
7. ✅ Create Databricks job for scheduled runs
8. ✅ Set up monitoring and alerts

---

## Support

For issues or questions:
- Check Azure DevOps pipeline logs
- Review Databricks workspace for deployed files
- Verify all environment variables are set correctly
- Check Databricks job run history for errors
