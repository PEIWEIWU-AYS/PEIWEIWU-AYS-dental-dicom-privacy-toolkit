from __future__ import annotations

import importlib.util
import platform
import sys

from ddpt import __version__
from ddpt.models import DoctorCheck, DoctorReport

REQUIRED_MODULES = {
    "cryptography": "encryption and package protection",
    "jinja2": "HTML report rendering",
    "numpy": "pixel processing",
    "PIL": "PNG preview rendering",
    "pydantic": "typed report models",
    "pydicom": "DICOM reading and writing",
    "rich": "terminal output",
    "typer": "CLI framework",
    "yaml": "YAML anonymization profiles",
}


def run_doctor() -> DoctorReport:
    checks = [_python_version_check()]
    checks.extend(_module_check(name, purpose) for name, purpose in REQUIRED_MODULES.items())
    return DoctorReport(
        passed=all(check.passed for check in checks),
        python_version=platform.python_version(),
        platform=platform.platform(),
        package_version=__version__,
        checks=checks,
    )


def _python_version_check() -> DoctorCheck:
    passed = sys.version_info >= (3, 10)
    message = "Python version is supported." if passed else "Python 3.10 or newer is required."
    return DoctorCheck(name="python-version", passed=passed, message=message)


def _module_check(module_name: str, purpose: str) -> DoctorCheck:
    found = importlib.util.find_spec(module_name) is not None
    if found:
        message = f"{module_name} is available for {purpose}."
    else:
        message = f"{module_name} is missing; reinstall with python -m pip install -e '.[dev]'."
    return DoctorCheck(name=f"module:{module_name}", passed=found, message=message)
