# Check if git is available
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Git is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com/downloads and try again."
    exit 1
}

# Initialize repository if not already initialized
if (-not (Test-Path .git)) {
    git init
}

# Configure remote
git remote remove origin 2>$null
git remote add origin https://github.com/varma1225/Gen-AI.git

# Add files (respecting .gitignore which excludes Data/ and frontend/)
git add .

# Commit
git commit -m "Initial commit of backend logic"

# Rename branch to main
git branch -M main

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main
