# Pull Request

## Summary

- 

## Type

- [ ] Code
- [ ] Documentation
- [ ] Tests
- [ ] Privacy/safety wording
- [ ] Workflow/report output

## Safety Checklist

- [ ] I did not add real DICOM, CBCT, radiographs, photos, PDFs, spreadsheets, clinic exports, consent forms, or screenshots with PHI.
- [ ] Any sample data is synthetic and clearly labeled.
- [ ] Generated folders such as `demo-run/`, `evidence-run/`, `showcase-run/`, and `macbook-validation-run/` are not committed.
- [ ] I did not add credentials, tokens, private URLs, or local secrets.

## Verification

- [ ] `ruff check .`
- [ ] `pytest`
- [ ] `ddpt release audit .`
- [ ] `ddpt capability matrix --root .`

## Notes

- 
