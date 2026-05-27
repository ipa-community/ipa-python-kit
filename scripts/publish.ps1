Remove-Item -Recurse -Force dist, build, *.egg-info, src/*.egg-info -ErrorAction SilentlyContinue
uv run python -m build; if ($?) { uv run python -m twine upload --config-file .pypirc --repository pypi dist/* }
