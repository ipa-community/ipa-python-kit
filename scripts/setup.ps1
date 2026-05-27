uv sync --all-extras --index-strategy unsafe-best-match
if ($?) {
    if (-not (Test-Path .git/hooks/pre-commit)) { pre-commit install }
    if (-not (Test-Path .git/hooks/commit-msg)) { pre-commit install --hook-type commit-msg }
}
