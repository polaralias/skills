# Test prompts

## 1. Happy path repo finalisation
Prompt: "Use $repo-publish-finaliser to close out this repository for public release."
Expected:
- Read the repository entrypoints before making cleanup decisions.
- Run a bounded verification pass and a publish-safety scan.
- Update active docs and remove or retire stale surfaces when justified.

## 2. Gitleaks path
Prompt: "Use $repo-publish-finaliser and make sure secret scanning is part of the final pass."
Expected:
- Check whether `gitleaks` is installed.
- Install or explain the installation step if it is missing.
- Run `gitleaks` and report whether findings are real leaks or likely false positives.

## 3. Archive cleanup boundary
Prompt: "Use $repo-publish-finaliser to decide whether completed-plan docs should stay in this repo."
Expected:
- Classify archive files as active, historical evidence, or redundant clutter.
- Prefer deletion when archive material is stale and no longer useful.

## 4. Publish-safety scan
Prompt: "Use $repo-publish-finaliser to check this repo for PII, local paths, and env or OAuth artifacts."
Expected:
- Search for secrets, `.env` files, local machine traces, and obvious PII.
- Distinguish acceptable public maintainer identity from accidental leakage.

## 5. Knowledge-surface closure
Prompt: "Use $repo-publish-finaliser to close the debt tracker and align the canonical docs."
Expected:
- Update README, glossary or architecture surfaces when needed.
- Remove pseudo-debt wording if the remaining constraints are intentional.
