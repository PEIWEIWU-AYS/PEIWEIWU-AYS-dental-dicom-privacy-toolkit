# GitHub Publish Preflight | GitHub 发布预检

`ddpt publish preflight` prepares this project for public GitHub publishing
without uploading files by itself.

It is designed for the current workflow:

- local MacBook development
- synthetic-data-only repository content
- bilingual README and discoverability checks
- public GitHub repository creation under `PEIWEIWU-AYS`
- safe manual creation of an empty remote repository before `git push`

## Command

```bash
ddpt publish preflight . \
  --json publish-preflight.json \
  --html publish-preflight.html
```

To verify that the GitHub repository already exists and the local account can
reach it:

```bash
ddpt publish preflight . \
  --check-remote \
  --json publish-preflight-remote.json \
  --html publish-preflight-remote.html
```

The default command does not contact GitHub. This keeps CI and offline MacBook
demos stable. `--check-remote` runs `git ls-remote` and can return
`action-required` when the repository has not been created yet.

## What It Checks

- the folder is a Git repository
- commit identity is configured
- current branch and HEAD commit are readable
- working tree is clean or clearly marked as needing action
- `origin` points to the expected GitHub repository
- README has bilingual naming, keywords, topics, and synthetic-data language
- `docs/discoverability.md` is present and keyword-rich
- GitHub Actions includes lint, tests, and release audit
- repository safety scan passes before publishing
- optional remote existence check with `--check-remote`

## Expected Repository

```text
Owner: PEIWEIWU-AYS
Repository name: dental-dicom-privacy-toolkit
Visibility: Public
Initialize README: No
Add .gitignore: No
Choose license: No
```

Suggested one-line GitHub description:

```text
Dental DICOM anonymization, de-identification, privacy regression, audit evidence, and encrypted sharing toolkit.
```

Suggested topics:

```text
dicom dental-imaging medical-imaging dicom-anonymization de-identification dicom-confidentiality orthanc dcmodify privacy privacy-regression pseudonymization local-first healthcare dentistry open-source-healthcare
```

## Push After Creating the Empty Repository

```bash
git remote set-url origin https://github.com/PEIWEIWU-AYS/dental-dicom-privacy-toolkit.git
git push -u origin main
```

If GitHub says `Repository not found`, create the empty repository first or
confirm that the browser is logged into `PEIWEIWU-AYS`.

## Safety Boundary

Do not publish real DICOM files, patient photos, clinic exports, consent forms,
spreadsheets, private drafts, `.env` files, keys, certificates, or archives. This
repository should remain synthetic-data-only.
