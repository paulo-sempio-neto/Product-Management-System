# Database evolution

## Storage boundary

The API and CLI continue to call the same service functions. The service now uses
`ProductRepository` and neutral product/error definitions from `persistence.py`.
`repositories.py` is the composition boundary and selects `SQLiteProductRepository`.
The adapter delegates to the existing SQLite functions so connection handling,
parameter binding, rollback, closure, and compatibility imports remain intact.

Every service persistence entry point accepts `repository=` as a keyword argument.
Passing both a database path and a repository is rejected rather than silently
selecting one. Service tests inject a non-SQLite repository; SQL and driver exception
classification never enter business rules. The existing `db_name` argument remains
a compatibility path for API, CLI, tests, and callers.

Repository writes each own a transaction. Multiple service calls are still not one
transaction: preflight duplicate/existence checks do not provide optimistic locking.
Database uniqueness remains authoritative if a concurrent insert wins a race.

## Migration strategy

This project has one table and no ORM. A small explicit SQLite runner is sufficient
for the first controlled schema transition without adding SQLAlchemy/Alembic merely
to recreate the existing adapter. `PRAGMA user_version` is owned by this application
and records revision 1. Revision-1 DDL and its upgrade must stay immutable; future
changes require another ordered revision and tests from each supported predecessor.
If ORM-backed PostgreSQL support is implemented later, adopt a backend-aware migration
tool such as Alembic as part of that implementation, not as a second concurrent
schema owner.

Fresh empty databases initialize to revision 1 during startup. An existing database
is inspected first: the known pre-Phase-5 schema is `legacy`; a matching revision-1
schema is `current`. Unexpected versions, altered tables, and legacy custom indexes,
triggers, views, or additional tables require manual review. This deliberately
conservative adoption policy may reject an equivalent manually authored schema.
It never stamps an unknown schema merely because a table named `products` exists.

`status` uses a read-only connection, validates legacy data, and never creates a
missing file. `upgrade` also requires an existing file and uses one transaction
for inspection, replacement-table creation, row copying, old-table removal, rename,
sequence restoration, and the revision stamp. Failure rolls everything back.
No names, prices, IDs, or deleted-ID sequence history are rewritten. Invalid legacy
rows stop the upgrade; the operator must decide how to repair them.

The table replacement follows SQLite's documented
[generalized ALTER TABLE procedure](https://sqlite.org/lang_altertable.html#otheralter).
Customized dependencies are refused instead of being silently discarded or recreated.
Run upgrades offline with all writers stopped. A lock timeout aborts the transaction;
do not run migrations from multiple app replicas. Health requires the supported
revision and a readable products table; it remains non-writing and cannot certify
that storage is writable.

## Local upgrade and rollback

1. Stop API, CLI, and any other database writers cleanly. Verify `DB_NAME` and the
   actual absolute file path. Production settings still require `DB_NAME`.
2. Inspect the database without mutation:

   ```powershell
   python -m migrations status --database produtos.db
   ```

3. Make a distinct backup while storage is offline. Use a new backup name; retain
   backups outside the container and outside the source repository:

   ```powershell
   Copy-Item -LiteralPath produtos.db -Destination produtos-before-v1.db
   ```

   This project uses SQLite's default rollback journal. If journal mode has been
   changed to WAL or shutdown was not clean, use SQLite's online backup API or a
   verified consistent snapshot; copying only the main file may omit committed data.
4. Rehearse the upgrade on a copy first, then upgrade the selected original:

   ```powershell
   python -m migrations upgrade --database produtos.db
   python -m migrations status --database produtos.db
   ```

5. Start the app, verify `/health`, and verify product counts and representative
   values against the backup. Keep the backup until application verification passes.

There is no automatic downgrade. To roll back, stop all writers, preserve the failed
database separately, restore the verified pre-upgrade backup, and run the matching
previous application version. Revision-1 startup refuses a restored legacy file.
Restoring a backup discards subsequent writes, so decide recovery explicitly.

## Container upgrade

Use the existing named volume; do not remove it. With the existing API container
present, stop all writers and copy its database to a new backup destination:

```powershell
docker compose stop api
docker compose cp api:/data/products.db .\products-before-v1.db
docker compose build api
docker compose run --rm --no-deps api python -m migrations status --database /data/products.db
docker compose run --rm --no-deps api python -m migrations upgrade --database /data/products.db
docker compose up -d api
```

The one-off service uses the same volume and unprivileged user as the API.
For an empty/new deployment, normal startup initializes revision 1; no upgrade
command is needed. These container commands require Docker and were not executed
in the development workspace where Docker is unavailable.

## Modeling decisions

| Concern | Revision 1 decision |
|---|---|
| Table/columns | Keep `products`, `id`, `name`, `price`; no API renaming. |
| IDs | Preserve signed 64-bit SQLite integer IDs and autoincrement history. |
| Name equality | Preserve exact, case-sensitive, accent-sensitive uniqueness. `Rice` and `rice` are distinct. |
| Name normalization | The service applies Python Unicode `strip()`. Storage additionally rejects non-text and empty/ASCII-space-only names; SQL `trim()` is not a replacement for Unicode normalization. |
| Search | Preserve the existing Python case/accent normalization and substring search. |
| Price | Keep positive finite binary64 floats, including existing fractional precision. Database checks reject invalid numeric values and nonnumeric stored text. |
| Indexes | The primary key and name-unique index already cover ID and exact-name lookups. Another name index would duplicate work. No ordinary index accelerates the current Python substring scan. |

An exact decimal price would be preferable if this becomes a monetary accounting
domain, but no currency, scale, rounding mode, or allowed range is specified.
Silently changing to integer cents or `NUMERIC(12,2)` would round existing values
and reject currently valid small/large prices. A later decimal migration needs an
explicit API contract, data audit, and separately versioned conversion.
PostgreSQL distinguishes approximate floating point from exact numeric types in its
[numeric type documentation](https://www.postgresql.org/docs/current/datatype-numeric.html).

## PostgreSQL preparation and acceptance criteria

PostgreSQL is not a configured backend yet. There is no `DATABASE_URL` switch,
driver dependency, or untested claim that SQLite SQL runs on PostgreSQL. A future
adapter can implement `ProductRepository` without changing product business rules.

| SQLite behavior | PostgreSQL adapter requirement |
|---|---|
| Integer autoincrement | `BIGINT GENERATED BY DEFAULT AS IDENTITY`; preserve imported IDs and advance the sequence beyond imported/deleted-ID history. |
| `TEXT ... UNIQUE` with binary comparison | Text with deterministic case/accent-sensitive collation, e.g. `COLLATE "C"`; retain named unique constraint `uq_products_name`. |
| SQLite `REAL` (binary64) | `DOUBLE PRECISION` while the float API remains; preserve finite-positive checks including rejecting NaN/infinity. PostgreSQL `REAL` is not the equivalent precision. |
| `?` placeholders, lastrowid | Driver parameter binding and `INSERT ... RETURNING id`; no interpolated values. |
| SQLite error codes | Translate only the name unique-constraint violation to `DatabaseDuplicateError`; other integrity/driver failures use the neutral error hierarchy. |
| Missing update/delete | Return False from affected-row checks; never report a missing write as success. |
| Out-of-range ID lookup | Return no product for integers outside the backend ID range. |
| Read-only health | Verify expected schema revision and table readability without creating storage. |

Before enabling PostgreSQL, run the same repository/API behavior suite against a
real PostgreSQL CI service, test driver failures and transactions, and test import
row counts, names, prices, and sequence behavior. Audit string compatibility
(including embedded NUL, unsupported in PostgreSQL text) rather than silently
changing names. Provision credentials/pooling and backend-specific migrations in
the composition layer. Cross-database data transfer is a separate explicit operation.
