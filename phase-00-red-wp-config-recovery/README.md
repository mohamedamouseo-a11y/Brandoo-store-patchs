# RED Recovery — wp-config.php

Emergency-only recovery for a missing or truncated `wp-config.php` on the Brando WordPress host.

## Safety model

- This patch contains **no database credentials, passwords, tokens, or salts**.
- Secrets are supplied only at runtime through environment variables on the server.
- The recovery tool validates the database connection before writing anything.
- The WordPress table prefix is validated against a real `*_options` table; if exactly one valid prefix can be detected it is selected automatically. Otherwise the tool stops and requires `BRANDO_TABLE_PREFIX`.
- Existing valid `wp-config.php` files are never overwritten unless `BRANDO_FORCE=1` is explicitly supplied.
- Any existing non-valid config is backed up before replacement.
- The new config is written to a temporary file, linted, then atomically renamed into place.
- Fresh WordPress auth salts are generated locally. This may log existing sessions out but does not modify site/database content.

## Required runtime variables

- `BRANDO_DB_NAME`
- `BRANDO_DB_USER`
- `BRANDO_DB_PASSWORD`
- `BRANDO_DB_HOST`

Optional:

- `BRANDO_TABLE_PREFIX`
- `BRANDO_FORCE=1`

## Run

```bash
php recover-wp-config.php /absolute/path/to/public_html
```

Do not commit, log, print, or copy the runtime secret values into the public patch repository.
