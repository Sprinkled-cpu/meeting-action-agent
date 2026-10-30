# Script to push local repository to GitHub
param (
    [string]$RepoUrl
)

if (-not $RepoUrl) {
    $RepoUrl = Read-Host "Enter your GitHub repository HTTPS URL (e.g., https://github.com/your-username/meeting-action-agent.git)"
}

if (-not $RepoUrl) {
    Write-Error "Repository URL cannot be empty."
    exit 1
}

Write-Host "Configuring remote origin: $RepoUrl" -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $RepoUrl

Write-Host "Pushing main branch to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS! Your code is now live on GitHub at:" -ForegroundColor Green
    Write-Host $RepoUrl.Replace('.git', '') -ForegroundColor Yellow
} else {
    Write-Host "`nPush failed. Please ensure the repository is created on GitHub and your credentials are valid." -ForegroundColor Red
}
