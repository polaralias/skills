# Publish Safety Checklist

Use this reference when doing the bounded publish-safety sweep.

## 1. Secrets and credentials

Scan for:

- API keys
- tokens
- passwords
- private keys
- OAuth credential files
- cloud credential files
- `.env` files

Typical search terms:

- `token`
- `secret`
- `api_key`
- `password`
- `BEGIN PRIVATE KEY`
- `.env`
- `oauth`
- `credentials`

## 2. Local and machine-specific traces

Scan for:

- absolute file paths
- usernames
- workstation names
- home-directory paths
- `AppData`, `.codex`, `.agents`, OneDrive, or similar machine-local references
- localhost-only notes that were meant for development rather than publication

Typical search terms:

- `C:\Users\`
- `/Users/`
- `/home/`
- `AppData`
- `OneDrive`
- `.codex`
- `.agents`
- `localhost`
- `127.0.0.1`

## 3. PII

Scan for:

- personal email addresses
- phone numbers
- identifiers accidentally pasted from logs or exports
- names that should not be public

Distinguish:

- intended public maintainer identity
- accidental private identity leakage

## 4. Generated clutter

Remove or ignore:

- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`
- editor swap files
- local scratch notes
- build outputs not meant for source control
- empty directories left behind after file deletion or moves

If the repo lacks a proper `.gitignore`, add one.
Keep an empty directory only when the repository intentionally documents that convention or tooling depends on it.

## 5. Image and binary metadata

Check images or assets for:

- author fields
- local export paths
- embedded software metadata
- timestamps if the repo wants ultra-clean packaged assets

Do not spend time stripping harmless metadata unless the user wants maximum tidiness or the metadata contains sensitive traces.

## 6. Archives and completed docs

Delete archive surfaces when they:

- duplicate current canonical docs
- contain stale "remaining work" language
- are no longer needed as historical evidence

Keep them only when they provide real, non-misleading historical value.

## 7. Empty directory sweep

After cleanup work:

- scan for directories that no longer contain tracked files or intentional placeholder content
- remove empty directories that exist only because earlier file deletion left them behind
- keep directories that are intentionally preserved by convention, documented setup, or required placeholder files
