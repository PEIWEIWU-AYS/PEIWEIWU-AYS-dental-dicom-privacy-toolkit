#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from ddpt.pipeline import run_demo_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic demo assets for Dental DICOM Privacy Toolkit."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("demo-run"),
        help="Output directory for generated demo assets.",
    )
    parser.add_argument(
        "--profile",
        default="dental-basic",
        help="Profile name or YAML path.",
    )
    parser.add_argument(
        "--rect",
        default="1,0,1,1",
        help="Pixel redaction rectangle in x,y,width,height format.",
    )
    args = parser.parse_args()

    result = run_demo_pipeline(args.out, profile=args.profile, rectangle=args.rect)
    print(f"Demo assets written to: {result.output_dir}")
    print(f"Summary HTML: {result.summary_html}")
    print(f"Encrypted package: {result.package_path}")
    print(f"Package key: {result.key_path}")
    print(f"Validation passed: {result.validation_passed}")
    print(f"Package entries: {result.package_entries}")


if __name__ == "__main__":
    main()
