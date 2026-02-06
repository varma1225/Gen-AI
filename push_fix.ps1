$env:Path = "C:\Program Files\Git\cmd;" + $env:Path

Write-Host "Attempting to pull remote changes..."
git pull origin main --allow-unrelated-histories --no-edit

if ($LASTEXITCODE -ne 0) {
    Write-Host "Pull failed or conflict. Attempting force push (overwriting remote)..." -ForegroundColor Yellow
    git push -u origin main --force
}
else {
    Write-Host "Pull successful. Pushing changes..."
    git push -u origin main
}
