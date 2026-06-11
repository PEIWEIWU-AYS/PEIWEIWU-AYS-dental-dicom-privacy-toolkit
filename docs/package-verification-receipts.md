# Package Verification Receipts | 分享包验证收据

`ddpt verify` can write JSON and HTML receipts when checking an encrypted sharing
package.

`ddpt verify` 在验证加密分享包时可以输出 JSON 和 HTML 收据。

The receipt records package integrity evidence for the receiver side of a
synthetic dental DICOM sharing workflow. It confirms that the package can be
opened, the manifest can be read, expected files are present, and SHA-256
checksums match.

这份收据用于合成牙科 DICOM 分享流程的接收方验证：确认分享包可以打开、manifest 可以读取、
文件存在且 SHA-256 校验一致。

## Command

```bash
ddpt verify demo-run/share/package.ddpt \
  --key demo-run/share/package.key \
  --receipt demo-run/reports/package-receipt.json \
  --html demo-run/reports/package-receipt.html
```

The command exits with status `0` when verification passes and non-zero when the
package cannot be decrypted, the manifest is missing, a file is missing, a
checksum does not match, or the ZIP contains an unsafe path.

## Receipt Contents

The receipt includes:

- package path
- whether a key was provided
- pass/fail status
- package SHA-256
- manifest package name
- encrypted flag from the manifest
- manifest entries with path, size, and SHA-256
- total entry bytes
- errors, if verification failed
- generated timestamp

## Why This Matters

Many tools can create or modify DICOM files, but sharing workflows also need
receiver-side evidence. A receipt gives reviewers a simple artifact they can
archive, screenshot, or include in method documentation.

## Safety Notes

Do not commit generated packages, keys, or receipts from real clinical material.
This repository is synthetic-data-only. A passing receipt proves package
integrity for the checked artifact, not clinical safety, legal compliance, or
complete de-identification.
