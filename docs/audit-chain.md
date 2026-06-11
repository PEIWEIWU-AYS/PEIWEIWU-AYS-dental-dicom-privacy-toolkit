# Audit Chain | 可验证审计链

Dental DICOM Privacy Toolkit can create a tamper-evident hash chain for generated artifacts.

This helps demonstrate that reports, anonymized files, redaction audits, manifests, and encrypted packages have not changed since the chain was created.

## Commands

```bash
ddpt audit chain demo-run --out demo-run/reports/audit-chain.json
ddpt audit verify demo-run/reports/audit-chain.json
```

The one-command demo automatically creates:

```text
demo-run/reports/audit-chain.json
demo-run/reports/audit-chain-verify.json
```

## How It Works

For each artifact, the chain records:

- relative path
- file size
- SHA-256 hash
- previous chain hash
- current chain hash

Files are processed in deterministic path order. The final `root_hash` summarizes the chain.

## Default Exclusions

By default, `.key` files are excluded from the audit chain because encryption keys should not be treated as public demo assets.

Use `--include-keys` only for controlled local testing:

```bash
ddpt audit chain demo-run --out demo-run/reports/audit-chain.json --include-keys
```

## Tamper Check

If any chained artifact changes after the chain is generated, verification fails:

```bash
ddpt audit verify demo-run/reports/audit-chain.json
```

This is not a blockchain and not a legal certification. It is a simple, transparent, reproducible integrity check for local demo and research artifacts.
