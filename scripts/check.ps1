[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$failureCount = 0

function Report-Check {
    param([bool]$Passed, [string]$Message)
    if ($Passed) {
        Write-Host "[OK] $Message"
    } else {
        Write-Host "[FAIL] $Message"
        $script:failureCount++
    }
}

Push-Location -LiteralPath $projectRoot
try {
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    Report-Check ($null -ne $gitCommand) 'Git is available'
    if ($null -eq $gitCommand) { exit 1 }

    $insideRepo = git rev-parse --is-inside-work-tree 2>$null
    Report-Check ($LASTEXITCODE -eq 0 -and $insideRepo -eq 'true') 'Workspace is a Git repository'
    if ($LASTEXITCODE -ne 0) { exit 1 }

    foreach ($requiredFile in @('README.md', '.gitignore', '.env.example', 'docs/PROJECT_BRIEF.md')) {
        Report-Check (Test-Path -LiteralPath $requiredFile -PathType Leaf) "$requiredFile exists"
    }

    git diff --check
    Report-Check ($LASTEXITCODE -eq 0) 'Unstaged changes have no whitespace errors'
    git diff --cached --check
    Report-Check ($LASTEXITCODE -eq 0) 'Staged changes have no whitespace errors'
    git show --format= --check HEAD
    Report-Check ($LASTEXITCODE -eq 0) 'Latest commit has no whitespace errors'

    $ignoredTrackedFiles = @(git ls-files --cached --ignored --exclude-standard)
    Report-Check ($ignoredTrackedFiles.Count -eq 0) 'No tracked files match .gitignore'
    if ($ignoredTrackedFiles.Count -gt 0) {
        $ignoredTrackedFiles | ForEach-Object { Write-Host "  $_" }
    }

    $originUrl = git config --get remote.origin.url
    if ($LASTEXITCODE -eq 0) {
        Write-Host '[INFO] Git origin is configured'
    } else {
        Write-Host '[INFO] Git origin is not configured yet'
    }

    $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
    if ($null -ne $nodeCommand) {
        Write-Host "[INFO] Node.js $(node --version)"
    }
    Write-Host '[INFO] Application build/tests are pending stack selection'
    if ($failureCount -gt 0) { exit 1 }
    Write-Host 'Repository checks passed.'
} finally {
    Pop-Location
}
