# Publication Extension

Use only when public-release hardening is explicitly in scope. Establish the active truth surface, verify real implementation and packaging paths, and remove stale public surfaces deliberately. Run `rke publication scan`; it reports redacted path/kind/line findings for tracked secrets, credential assignments, local paths, environment files, PII candidates, and caches, and adds Git-history scanning when `gitleaks` is already installed. Tool absence is reported rather than triggering installation. Review all candidates, because pattern and scanner findings can be false positives.

Add release automation only when the repository publication model requires it. Re-run implementation validation and the scan after cleanup. Resolving `publication-safety` establishes readiness evidence; it does not authorise repository-setting changes, publication, release creation, deployment, or external communication.
