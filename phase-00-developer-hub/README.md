# Phase 00 — Brando Developer Hub

This phase must be applied before the storefront/theme phases.

The WordPress plugin is modeled directly on the current TCRM `DeveloperHubTab.tsx` + `server/routes/developerHub.ts` workflow: local repository status, encrypted GitHub connection, repository/branch selection, Push Control (`off` / `review` / `auto`), preview-before-write Push/Pull/Sync, AI context generation, MCP toggle, secure AI context endpoint, and source-code ZIP export.

## Access policy

Brando intentionally tightens TCRM access: the Hub is **Super Admin only**.

- Multisite: WordPress `is_super_admin()` is required.
- Single-site: only the designated Developer Hub owner IDs may enter; activation seeds the activating administrator (or the first administrator when activated by WP-CLI).
- The menu is hidden from everyone else.
- Direct admin-page and REST mutation access are also denied server-side.

## Security baseline

- GitHub token encrypted at rest with AES-256-GCM.
- Token is never returned to the browser after storage and is redacted from errors/logs.
- Git writes require a fresh preview fingerprint.
- Concurrent Git writes are locked.
- Shell interpolation is not used; Git is invoked with an argument array and an allowlisted subcommand set.
- Source/context exports exclude `.git`, uploads/cache, `wp-config.php`, `.env`, and secret/credential-like files.
- V1 blocks automatic execution when local and remote changes both exist; this is fail-safe until advanced conflict/recovery parity is added.

## Bootstrap compatibility hotfix — v0.1.1

The plugin registers its WordPress hooks immediately when the active plugin file is loaded instead of deferring bootstrap to `plugins_loaded`.

## Production alignment — v0.1.2

- Canonical health endpoint: `/wp-json/brando-developer-hub/v1/health`.
- WordPress core checksum/integrity verification is required after core repair incidents.

## Reviewed first repository setup — v0.1.3

Added reviewed initialization for an empty remote repository and safe WordPress baseline fingerprinting.

## Manual first push workflow — v0.1.4

- Repository Initialize prepares Git only on the real WordPress server.
- It creates local `main`, safe `.gitignore`, `origin`, and the initial local baseline commit.
- Initialize does **not** push remotely.
- The user performs the first actual remote push manually from Developer Hub.

## Mixed-deployment protection — v0.1.5

A production fatal exposed a mixed/stale deployment: the server was executing legacy namespaced classes such as `BrandoDeveloperHub\\Core` / `BrandoDeveloperHub\\RepositoryInit`, while the canonical patch uses `BDH_Core` / `BDH_Repository_Init`.

v0.1.5 therefore:

- adds build ID `20260904-v015-canonical`;
- checks that all required plugin files exist before loading them;
- checks that all canonical `BDH_*` classes were actually loaded;
- fails soft and disables the Hub safely if a partial/mixed deployment is detected, instead of taking down WordPress;
- requires byte-for-byte deployment verification using `DEPLOYMENT_MANIFEST.v0.1.5.json`;
- requires every plugin file to be overwritten from the public patch repo during this recovery; old PHP files must not be preserved.

## Files

Copy `files/` into the existing WordPress root, preserving paths. For v0.1.5 recovery, follow `OPENHANDS_PROMPT.txt` and `DEPLOYMENT_MANIFEST.v0.1.5.json` exactly.
