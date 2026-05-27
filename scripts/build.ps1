Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
uv run pyinstaller main.spec
