# Release process

Use this checklist when publishing a new `smsflow` version.

## Before release

1. Update `pyproject.toml` version.
2. Update `CHANGELOG.md`.
3. Run `python -m unittest discover -s tests`.
4. Run `python -m build`.
5. Confirm no credentials, customer data, logs, or private URLs are present.

## Publish

1. Merge to `main` after CI passes.
2. Create a GitHub release named `vX.Y.Z`.
3. The publish workflow publishes `smsflow` to PyPI through Trusted Publishing.
4. The package smoke workflow installs the published package from PyPI.

## Trusted Publishing

PyPI publishing uses a GitHub Trusted Publisher for:

- Owner: `SMSFlow-ZA`
- Repository: `smsflow-python`
- Workflow: `publish.yml`
- Environment: blank

No long-lived PyPI API token is required.

