# Competitor Analysis | 竞品分析

This document studies established DICOM anonymization and privacy tools, then turns their strengths and gaps into concrete design requirements for Dental DICOM Privacy Toolkit.

## Summary

The mature ecosystem already has strong general-purpose DICOM tools. The opportunity for this project is not to pretend they do not exist. The opportunity is to combine the best lessons into a dental-focused, synthetic-demo-friendly, command-line-first privacy workflow with readable audit reports and encrypted sharing packages.

## Comparison Matrix

| Project | Strengths | Gaps for this project | What we should learn |
| --- | --- | --- | --- |
| RSNA DICOM Anonymizer | Research-oriented anonymizer, configurable behavior, GUI workflow, reputable source | Not dental-specific, less focused on lightweight CLI demos and bilingual discoverability | Configurable anonymization, research credibility, careful UI language |
| DicomCleaner | GUI cleanup, DICOM header cleaning, pixel/burned-in annotation handling, accessible for non-programmers | Desktop GUI workflow is harder to automate in CI; not designed as a Python package for reproducible CLI reports | Pixel data risks matter; non-technical users need readable outputs |
| Orthanc | DICOM server, Web UI, REST API, anonymization endpoint, production-grade ecosystem | Heavier server architecture; less suitable as a small local research toolkit | REST/API design, workflow integration, practical deployment maturity |
| RSNA CTP | Pipeline-based clinical trial processor, DICOM anonymizer stage, mature multi-stage architecture | Heavy Java/server pipeline; too much infrastructure for a first dental toolkit | Pipeline thinking, stage-by-stage processing, auditability |
| DCMTK `dcmodify` | Precise low-level DICOM tag edit/delete/insert command-line utility | Low-level tool; users must know exactly which tags to modify | Deterministic CLI behavior, explicit tag operations |
| pydicom anonymization example | Clear Python-level anonymization patterns, easy to adapt, good learning source | Example-level only; not a complete product with CLI, reports, encryption, tests, or dental profiles | Build core logic on understandable Python primitives |

## What Existing Tools Do Well

### Anonymization and De-identification

Mature tools can remove, replace, or modify DICOM attributes. This is a necessary baseline. Our toolkit must support explicit tag handling, configurable profiles, and repeatable anonymization behavior.

### GUI Accessibility

RSNA Anonymizer and DicomCleaner show that non-programmer workflows matter. Our first version can be CLI-first, but it should generate readable HTML reports so dental users and collaborators can understand the result.

### Pipeline Thinking

RSNA CTP and Orthanc show that real imaging workflows are pipelines, not one-off scripts. Our commands should feel like stages:

1. inspect
2. classify risk
3. anonymize
4. validate
5. report
6. package
7. verify

### Low-Level Precision

DCMTK proves that expert users value exact control over DICOM tags. Our toolkit should expose transparent profiles and audit logs instead of hiding all decisions.

### Python Learnability

pydicom makes DICOM handling approachable. Our project should use readable Python code so researchers and developers can understand and extend it.

## What Existing Tools Often Do Not Combine

Many tools do one or two things very well, but they do not always combine all of the following in a small dental-focused open-source package:

- dental/CBCT/oral imaging positioning
- synthetic demo data as a first-class workflow
- multi-file synthetic DICOM study folders for batch and repeated-subject demos
- bilingual English/Chinese discoverability
- CLI that works cleanly in CI
- static HTML reports for non-programmers
- local browser workbench for GUI-style synthetic workflow review
- static local review dashboard for non-programmer walkthroughs
- competitor-informed capability matrix that maps claims to repository evidence
- PNG previews for GitHub-friendly visual review
- pixel review reports with original, overlay, and redacted previews
- read-only directory inventory before anonymization
- RSNA CTP-inspired YAML workflow recipes
- HTML workflow reports for staged pipeline review
- anonymization dry-run previews before writing DICOM files
- before/after de-identification comparison reports
- deterministic date shifting for research-sharing profiles
- profile lint checks for custom YAML configuration quality
- profile comparison reports for transparent configuration review
- exportable DICOM privacy policy registry in JSON, CSV, and HTML
- reusable YAML pixel redaction plans for known burned-in regions
- DCMTK-style exact tag operations with audit JSON
- Orthanc-inspired local REST API without heavy PACS infrastructure
- local browser workbench that runs against the REST API without cloud upload
- JSON audit events and manifests
- release-readiness audit for docs, discoverability, workflow coverage, CI, safety, and profile coverage
- local evidence bundle that packages environment, safety, release, demo, workflow, audit, and sharing proof
- encrypted sharing package demo
- receiver-side package verification receipts for sharing evidence
- GitHub-friendly screenshots, docs, and one-command demo
- clear safety language about de-identification limits

## Our Target Differentiation

Dental DICOM Privacy Toolkit should aim to be:

- dental-first rather than generic imaging-first
- synthetic-demo-first rather than real-data-first
- CLI-first for reproducibility
- report-first for presentation and trust
- profile-first for transparent anonymization decisions
- audit-first for research and compliance conversations
- encryption-aware for sharing workflows
- bilingual and keyword-rich for GitHub search

## Necessary Features to Inherit

The project should include these baseline capabilities from the best existing tools:

- DICOM metadata inspection
- explicit tag risk classification
- configurable anonymization profile
- removal or replacement of direct identifiers
- private tag removal by default
- deterministic CLI commands
- validation after anonymization
- clear warnings about burned-in pixel data
- reproducible synthetic examples

## Features to Add Beyond the Baseline

The project should add:

- dental-specific profile names and documentation
- audit event JSON output
- directory inventory with JSON, CSV, and HTML exports
- multi-stage YAML workflow runner with step-level artifacts
- human-readable HTML report for workflow execution
- pre-write anonymization dry-run reports for safer profile review
- research-sharing profile with deterministic date shifting and audited date-shift actions
- profile lint JSON and HTML reports for custom configuration review
- profile comparison JSON and HTML reports for explaining configuration differences
- policy registry export for transparent DICOM keyword risk/action rationale
- PNG preview generation for before/after workflow review
- pixel review HTML report for known burned-in annotation regions
- percent-based pixel redaction plans for repeated dental export layouts
- exact tag dump/set/blank/delete commands with write-operation audits
- local REST API endpoints for inventory, inspection, anonymization, validation, and preview
- local browser workbench for synthetic demo, inventory, inspect, anonymize, validate, and preview
- static HTML reports
- release-readiness audit with JSON and HTML output before public GitHub milestones
- capability matrix with JSON and HTML output for competitor-informed project review
- static review dashboard that gathers report links and synthetic PNG previews
- side-by-side de-identification comparison HTML for reviewer-friendly evidence
- portable de-identification certificate for synthetic sharing handoff evidence
- evidence bundle with JSON and HTML index for MacBook validation and public demonstrations
- encrypted sharing package with manifest and checksums
- package verification receipts with JSON and HTML outputs
- share-readiness gate that combines privacy, pixel, package, and audit evidence
- manual pixel redaction audit for known burned-in annotation regions
- one-command synthetic demo path
- multi-file synthetic study generator for safe batch workflow testing
- GitHub topics and bilingual keyword strategy
- report screenshots in later milestones

## References

- RSNA DICOM Anonymizer: https://github.com/RSNA/Anonymizer
- PixelMed DicomCleaner: https://www.pixelmed.com/cleaner.html
- Orthanc Book, anonymization: https://orthanc.uclouvain.be/book/users/anonymization.html
- RSNA Clinical Trial Processor: https://mircwiki.rsna.org/index.php?title=MIRC_CTP
- DCMTK `dcmodify`: https://support.dcmtk.org/docs/dcmodify.html
- pydicom anonymization example: https://pydicom.github.io/pydicom/stable/auto_examples/metadata_processing/plot_anonymize.html
- DICOM Attribute Confidentiality Profiles: https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_e.html
