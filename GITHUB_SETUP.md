# GitHub Actions Setup Guide (FREE)

Complete guide to set up FREE automated deployments using GitHub Actions.

---

## Why GitHub Actions?

- ✅ **100% FREE** for public repos
- ✅ **FREE** for private repos (2,000 minutes/month)
- ✅ Automatic deployment on git push
- ✅ Code validation before deployment
- ✅ No credit card required
- ✅ Industry standard

---

## Step 1: Create GitHub Account (if needed)

1. Go to https://github.com
2. Click **Sign up**
3. Follow the registration process
4. Verify your email

**Cost: FREE** ✅

---

## Step 2: Create GitHub Repository

### Option A: Using GitHub Website

1. Go to https://github.com/new
2. Repository name: `txr1`
3. Description: "RRC Refinery Reports Data Pipeline"
4. Choose **Private** (still FREE with 2,000 minutes/month)
5. **Do NOT** initialize with README (we already have files)
6. Click **Create repository**

### Option B: Using GitHub CLI

```bash
gh repo create txr1 --private --source=. --remote=origin --push
```

---

## Step 3: Push Your Code to GitHub

Open PowerShell in your project directory:

```powershell
cd c:\Users\gopal.allam\txr1

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - RRC pipeline with GitHub Actions"

# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/txr1.git

# Push to main branch
git branch -M main
git push -u origin main

# Create and push develop branch
git checkout -b develop
git push -u origin develop
git checkout main
```

---

## Step 4: Add Secrets to GitHub

Secrets are encrypted environment variables that store sensitive information.

### Get Your Databricks Information:

#### A. Databricks Host:
- Your workspace URL (e.g., `https://adb-1234567890123456.7.azuredatabricks.net`)

#### B. Databricks Token:
1. In Databricks, click your profile icon (top right)
2. Go to **Settings** → **Developer**
3. Click **Manage** next to "Access tokens"
4. Click **Generate new token**
5. Name: "GitHub Actions"
6. Lifetime: Leave blank (no expiration) or set to 90 days
7. Click **Generate**
8. **Copy the token immediately** (you won't see it again!)

#### C. Your Databricks Email:
- The email you use to log into Databricks

### Add Secrets in GitHub:

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

Add these 3 secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `DATABRICKS_HOST` | Your workspace URL | `https://adb-123.7.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Your personal access token | `dapi1234567890abcdef...` |
| `DATABRICKS_USER` | Your email | `your.email@company.com` |

**For Production (optional):**

If you have a separate production workspace:

| Secret Name | Value |
|------------|-------|
| `DATABRICKS_HOST_PROD` | Production workspace URL |
| `DATABRICKS_TOKEN_PROD` | Production access token |

---

## Step 5: Create Environments (Optional but Recommended)

Environments allow you to require approvals before deploying to production.

### Create Dev Environment:

1. In your repository, go to **Settings** → **Environments**
2. Click **New environment**
3. Name: `databricks-dev`
4. Click **Configure environment**
5. (No additional settings needed for dev)
6. Click **Save protection rules**

### Create Prod Environment:

1. Click **New environment**
2. Name: `databricks-prod`
3. Click **Configure environment**
4. Check **Required reviewers**
5. Add yourself (or team members) as reviewers
6. Click **Save protection rules**

Now production deployments will require manual approval! ✅

---

## Step 6: Test the Deployment

### Test Dev Deployment:

```powershell
# Make a small change
git checkout develop
echo "# Test" >> README_PIPELINE.md
git add .
git commit -m "Test dev deployment"
git push origin develop
```

**What happens:**
1. GitHub Actions automatically starts
2. Validates Python and SQL code
3. Deploys to Databricks Dev workspace
4. You get a notification when complete

**View the deployment:**
1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click on the running workflow
4. Watch the deployment in real-time!

### Test Prod Deployment:

```powershell
# Merge develop to main
git checkout main
git merge develop
git push origin main
```

**What happens:**
1. GitHub Actions starts
2. Validates code
3. **Waits for your approval** (if you set up environment protection)
4. After approval, deploys to production

---

## Step 7: Verify Deployment in Databricks

1. Go to your Databricks workspace
2. Navigate to **Workspace** → **Users** → **your-email@company.com** → **txr1**
3. You should see all your files:
   - `01_create_schemas_and_tables.sql`
   - `02_extract_pdfs_to_bronze.py`
   - `03_transform_bronze_to_silver.sql`
   - `upload_to_volume.py`
   - `rrc_scraper.py`

---

## How It Works

### Workflow Triggers:

- **Push to `develop` branch** → Deploys to Dev
- **Push to `main` branch** → Deploys to Prod (with approval)
- **Manual trigger** → Can run anytime from Actions tab

### Workflow Steps:

1. **Validate** (runs on every push)
   - Checks Python syntax
   - Checks SQL syntax
   - Fails if any errors found

2. **Deploy to Dev** (only on develop branch)
   - Installs Databricks CLI
   - Uploads all `.py` files
   - Uploads all `.sql` files
   - Shows deployment summary

3. **Deploy to Prod** (only on main branch)
   - Waits for approval (if configured)
   - Same as dev deployment
   - Deploys to production workspace

---

## Daily Workflow

### Making Changes:

```powershell
# 1. Create a feature branch
git checkout develop
git pull origin develop
git checkout -b feature/my-changes

# 2. Make your changes
# Edit files...

# 3. Commit and push
git add .
git commit -m "Description of changes"
git push origin feature/my-changes

# 4. Create Pull Request on GitHub
# Go to GitHub → Pull Requests → New Pull Request

# 5. After review, merge to develop
# This automatically deploys to Dev

# 6. When ready for production, merge develop to main
git checkout main
git merge develop
git push origin main
# This deploys to Prod (after approval)
```

---

## Monitoring Deployments

### View Deployment Status:

1. Go to repository on GitHub
2. Click **Actions** tab
3. See all workflow runs
4. Click on any run to see details

### Get Notifications:

1. Go to repository **Settings** → **Notifications**
2. Configure email notifications for:
   - Workflow failures
   - Workflow successes
   - Approval requests

---

## Troubleshooting

### Issue: "Workflow doesn't start"

**Check:**
- Did you push to `main` or `develop` branch?
- Did you modify `.py` or `.sql` files?
- Go to **Actions** tab → Check if workflow is disabled

**Solution:**
```powershell
# Enable workflows
# Go to Actions tab → Click "I understand, enable them"
```

### Issue: "Authentication failed"

**Check:**
- Is `DATABRICKS_HOST` correct? (include `https://`)
- Is `DATABRICKS_TOKEN` valid?
- Did you copy the full token?

**Solution:**
- Regenerate token in Databricks
- Update secret in GitHub

### Issue: "Files not appearing in Databricks"

**Check:**
- Is `DATABRICKS_USER` your correct email?
- Check the workspace path in deployment logs

**Solution:**
- Update `DATABRICKS_USER` secret
- Check Databricks workspace under your user folder

### Issue: "Workflow fails on validation"

**Check:**
- Python syntax errors
- SQL syntax errors
- Review the error in Actions logs

**Solution:**
- Fix the syntax errors locally
- Test with: `python -m py_compile your_file.py`
- Commit and push again

---

## Cost Tracking

### Check Your Usage:

1. Go to GitHub **Settings** (your profile, not repo)
2. Click **Billing and plans**
3. Click **Plans and usage**
4. See **Actions** usage

### Free Tier Limits:

- **Public repos:** Unlimited ✅
- **Private repos:** 2,000 minutes/month ✅
- Each deployment: ~2-3 minutes
- **You can do ~600-1000 deployments/month FREE**

### If You Exceed Free Tier:

- **Cost:** $0.008/minute
- **Example:** 1,000 extra minutes = $8
- Still much cheaper than Azure DevOps!

---

## Best Practices

1. **Use Branch Protection:**
   - Require pull request reviews
   - Require status checks to pass
   - Settings → Branches → Add rule

2. **Use Environments:**
   - Require approvals for production
   - Separate dev and prod secrets

3. **Monitor Workflows:**
   - Check Actions tab regularly
   - Set up email notifications

4. **Keep Secrets Updated:**
   - Rotate tokens every 90 days
   - Update secrets in GitHub

5. **Use Descriptive Commit Messages:**
   - Helps track what was deployed
   - Shows in deployment history

---

## Advanced: Manual Deployment

You can manually trigger a deployment:

1. Go to **Actions** tab
2. Click on "Deploy to Databricks" workflow
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow**

---

## Summary

✅ **Step 1:** Create GitHub account (FREE)  
✅ **Step 2:** Create repository (FREE)  
✅ **Step 3:** Push code to GitHub  
✅ **Step 4:** Add 3 secrets (DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_USER)  
✅ **Step 5:** Create environments (optional)  
✅ **Step 6:** Push to develop or main  
✅ **Step 7:** Automatic deployment! 🎉

**Total Cost: $0/month** (for typical usage)

---

## Next Steps

After setup:
1. ✅ Make changes locally
2. ✅ Commit and push to develop
3. ✅ Automatic deployment to dev
4. ✅ Merge to main for production
5. ✅ Approve and deploy to prod

**You now have a professional CI/CD pipeline for FREE!** 🚀
