# DICOM Tag Operations | DICOM 标签精确操作

`ddpt tag` provides low-level DICOM metadata operations inspired by tools such as DCMTK `dcmodify`. It is meant for expert review, synthetic demos, debugging anonymization profiles, and documenting exact tag changes.

`ddpt tag` 提供类似 DCMTK `dcmodify` 的底层 DICOM metadata 操作能力，适合专家检查、合成数据演示、调试脱敏 profile，以及记录精确 tag 变更。

## Dump Tags

```bash
ddpt tag dump demo-run/input/sample.synthetic.dcm \
  --json demo-run/reports/tag-dump.json
```

Pixel data is excluded by default.

## Set or Insert a Tag

```bash
ddpt tag set demo-run/input/sample.synthetic.dcm PatientName ANON^TEST \
  --out demo-run/outputs/sample.tag-set.dcm \
  --audit demo-run/reports/tag-set-audit.json
```

If the tag already exists, the value is replaced. If the tag is missing and the DICOM dictionary knows the VR, the tag is inserted.

For private or unknown tags, provide a VR:

```bash
ddpt tag set demo-run/input/sample.synthetic.dcm 0019,1001 SYNTHETIC \
  --vr LO \
  --out demo-run/outputs/sample.private-tag.dcm \
  --audit demo-run/reports/private-tag-audit.json
```

## Blank a Tag

```bash
ddpt tag blank demo-run/input/sample.synthetic.dcm 0010,1040 \
  --out demo-run/outputs/sample.blank-address.dcm \
  --audit demo-run/reports/tag-blank-audit.json
```

## Delete a Tag

```bash
ddpt tag delete demo-run/input/sample.synthetic.dcm PatientTelephoneNumbers \
  --out demo-run/outputs/sample.delete-phone.dcm \
  --audit demo-run/reports/tag-delete-audit.json
```

## Safety Boundary

Low-level tag operations can damage DICOM files or remove clinically important metadata if used carelessly. Prefer `ddpt anonymize` for standard de-identification workflows, and use `ddpt tag` for targeted expert operations on synthetic or explicitly approved test files.
