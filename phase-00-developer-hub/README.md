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

The plugin registers its WordPress hooks immediately when the active plugin file is loaded instead of deferring bootstrap to `plugins_loaded`. This prevents managed-hosting or temporary MU-activation flows from loading the plugin after `plugins_loaded` has already fired and silently missing `rest_api_init` registration.

Any temporary MU activation helper used only to activate the plugin must be removed after `brando-developer-hub` is confirmed active. The production plugin must load through WordPress' normal active-plugin mechanism.

## Files

Copy `files/` into the existing WordPress root, preserving paths, then activate `brando-developer-hub`.
