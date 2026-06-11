# Research Sharing Profile | 研究共享匿名化配置

`dental-research-sharing` is a configurable anonymization profile for synthetic
dental imaging research demos.

`dental-research-sharing` 是一个面向合成牙科影像研究演示的匿名化配置。

It keeps the same core privacy stance as `dental-basic`: direct identifiers are
replaced or blanked, UIDs are regenerated, and private tags are removed by
default. Its extra behavior is deterministic date shifting for study-level dates.

它和 `dental-basic` 一样会替换或清空直接标识符、重建 UID、默认移除 private tags。
额外能力是对研究常用日期做确定性偏移。

For longitudinal demos that need the same synthetic subject to stay linkable
across files, use `dental-linkable-research` instead. That profile adds
deterministic pseudonymization for `PatientName` and `PatientID`.

## Why Date Shifting

Some research workflows need relative timing while reducing direct
re-identification risk. For example, a reviewer may need to know that two images
were taken weeks apart without seeing the original calendar dates.

Date shifting helps preserve intervals while moving dates away from their real
values. It does not guarantee de-identification and should still be reviewed
against the intended sharing context.

## Profile Behavior

The built-in profile:

- replaces `PatientName`, `PatientID`, `AccessionNumber`, `StudyDescription`,
  `SeriesDescription`, and `InstitutionName`
- blanks direct identifiers, clinician names, device/station fields, protocol
  text, and study/series/acquisition/content times
- shifts `StudyDate`, `SeriesDate`, `AcquisitionDate`, and `ContentDate` by
  `-3650` days
- regenerates `StudyInstanceUID`, `SeriesInstanceUID`, `SOPInstanceUID`, and
  `FrameOfReferenceUID`
- removes private tags by default

## Commands

Inspect the profile:

```bash
ddpt profile show dental-research-sharing --json reports/research-profile.json
```

Preview changes without writing a DICOM file:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-research-sharing \
  --dry-run \
  --audit demo-run/reports/research-dry-run.json \
  --html demo-run/reports/research-dry-run.html
```

Write an anonymized research-sharing copy:

```bash
ddpt anonymize demo-run/input/sample.synthetic.dcm \
  --profile dental-research-sharing \
  --out demo-run/outputs/sample.research-sharing.dcm \
  --audit demo-run/reports/research-sharing-audit.json \
  --html demo-run/reports/research-sharing-audit.html
```

Check coverage:

```bash
ddpt profile coverage dental-research-sharing
```

## Safety Notes

Use synthetic data for public demos. Date shifting is one privacy control, not a
standalone anonymization guarantee. Pixel-level burned-in identifiers, unusual
free text, rare combinations, and external linkage risks still require review.
