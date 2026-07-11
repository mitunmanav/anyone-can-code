param(
    [Parameter(Mandatory = $true)]
    [string]$Base,

    [Parameter(Mandatory = $true)]
    [string]$Candidate,

    [Parameter(Mandatory = $true)]
    [ValidateSet("reliability", "development-system", "docs-only", "plugin-product")]
    [string]$Policy
)

$ErrorActionPreference = "Stop"

function Get-AllowedPatterns {
    param([string]$Name)

    switch ($Name) {
        "reliability" {
            return @(
                '^\.flow/specs/fn-2-harden-acc-development-system\.(json|md)$',
                '^\.flow/tasks/fn-2-harden-acc-development-system\.[0-9]+\.(json|md)$',
                '^\.flow/usage\.md$',
                '^AGENTS\.md$',
                '^DEVELOPMENT-WORKFLOW\.md$'
            )
        }
        "docs-only" {
            return @(
                '^AGENTS\.md$',
                '^DEVELOPMENT-WORKFLOW\.md$',
                '^README\.md$',
                '^CONTRIBUTING\.md$',
                '^CHANGELOG\.md$',
                '^SECURITY\.md$',
                '^SUPPORT\.md$',
                '^\.flow/usage\.md$',
                '^\.flow/(specs|tasks)/.*\.(md|json)$'
            )
        }
        "development-system" {
            return @(
                '^AGENTS\.md$',
                '^DEVELOPMENT-WORKFLOW\.md$',
                '^scripts/check-promotion-scope\.ps1$',
                '^tests/test_check_promotion_scope\.py$',
                '^\.flow/(specs|tasks)/fn-3-automate-safe-local-promotion(\.[0-9]+)?\.(md|json)$'
            )
        }
        "plugin-product" {
            return @(
                '^plugins/anyone-can-code/',
                '^AGENTS\.md$',
                '^DEVELOPMENT-WORKFLOW\.md$',
                '^README\.md$',
                '^\.flow/(specs|tasks)/.*\.(md|json)$'
            )
        }
    }
}

function Test-AllowedPath {
    param(
        [string]$Path,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if ($Path -match $pattern) {
            return $true
        }
    }
    return $false
}

git rev-parse --verify $Base *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Output "FAIL invalid base ref: $Base"
    exit 1
}

git rev-parse --verify $Candidate *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Output "FAIL invalid candidate ref: $Candidate"
    exit 1
}

$changed = @(git diff --name-only $Base $Candidate | ForEach-Object { $_.Replace('\', '/') } | Where-Object { $_ })
$patterns = Get-AllowedPatterns -Name $Policy
$forbidden = @($changed | Where-Object { -not (Test-AllowedPath -Path $_ -Patterns $patterns) })

if ($forbidden.Count -gt 0) {
    Write-Output "FAIL policy=$Policy"
    Write-Output "Forbidden files:"
    $forbidden | ForEach-Object { Write-Output $_ }
    exit 1
}

Write-Output "PASS policy=$Policy changed=$($changed.Count)"
exit 0
