# How to Install GitHub CLI

## Option 1: Using Winget (Recommended)

In your terminal, the installation is waiting for approval. Type `Y` and press Enter to continue.

```powershell
winget install --id GitHub.cli
# When prompted, type: Y
```

---

## Option 2: Download Installer (If Winget Fails)

1. Go to: https://cli.github.com/
2. Click **Download for Windows**
3. Run the downloaded `.msi` installer
4. Follow the installation wizard
5. Restart your terminal

---

## Option 3: Using Chocolatey

If you have Chocolatey installed:

```powershell
choco install gh
```

---

## Option 4: Using Scoop

If you have Scoop installed:

```powershell
scoop install gh
```

---

## Verify Installation

After installation, verify it works:

```powershell
gh --version
```

You should see something like:
```
gh version 2.40.0 (2024-01-15)
```

---

## Authenticate with GitHub

After installation, authenticate:

```powershell
gh auth login
```

Follow the prompts:
1. Choose: **GitHub.com**
2. Choose: **HTTPS**
3. Choose: **Login with a web browser**
4. Copy the one-time code
5. Press Enter to open browser
6. Paste the code and authorize

---

## Quick Commands

### Create Repository:
```powershell
gh repo create txr1 --private --source=. --remote=origin --push
```

### View Repository:
```powershell
gh repo view --web
```

### Create Pull Request:
```powershell
gh pr create --title "My changes" --body "Description"
```

---

## Alternative: Use Git Without GitHub CLI

You don't actually need GitHub CLI. You can use regular Git:

```powershell
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit"

# Add remote (create repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/txr1.git

# Push
git push -u origin main
```

---

## Troubleshooting

### Issue: "winget not found"

**Solution:** Update Windows or install App Installer from Microsoft Store

### Issue: "gh not recognized"

**Solution:** Restart your terminal after installation

### Issue: "Authentication failed"

**Solution:** Run `gh auth login` again

---

## Do You Need GitHub CLI?

**No, it's optional!** You can:

1. **Use regular Git** (already installed)
2. **Create repo on GitHub website** manually
3. **Push using Git commands**

GitHub CLI just makes it faster, but it's not required for the deployment pipeline to work.
