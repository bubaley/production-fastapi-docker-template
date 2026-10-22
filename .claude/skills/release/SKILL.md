---
name: release
description: How versions, changelog and releases work in this template (conventional commits + git-cliff in CI). Use when the user asks to release, bump the version, tag, write the changelog, choose a commit message type, or asks why something did or did not release.
---

# Release

Rules: [deployment.md → Releases](../../../docs/deployment.md) and [cliff.toml](../../../cliff.toml). Releases are automatic; agents never tag or bump by hand.

1. **Commit types decide the version.** `feat` → minor; `fix`, `perf`, `revert`, `build`, `chore(deps)` → patch; `!` or a `BREAKING CHANGE:` footer → major. `docs`, `refactor`, `test`, `chore`, `ci`, `style` do not release.
2. Write conventional commits (`type(scope): summary`, imperative, English). PR titles must be conventional — they become the squash commit on `main`.
3. Never edit `version.json`, the `version` in `backend/pyproject.toml` / `frontend/package.json`, or `CHANGELOG.md`; never create `v*` tags. The CI `release` job does it after the gate passes on `main`: `chore(release): vX.Y.Z [skip ci]`, tag, GitHub Release, image publish, deploy.
4. To preview the next version locally: `uvx --from git-cliff git-cliff --bumped-version` (needs the tags fetched).
5. Nothing released? Check that the commits since the last tag have a releasable type and that the CI gate passed on `main`.
6. Rollback is a workflow (`.github/workflows/rollback.yaml`), not a revert-and-retag — see deployment.md.
