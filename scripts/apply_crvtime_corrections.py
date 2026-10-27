#!/usr/bin/env python3
"""Subtract channel-by-channel CRVTime corrections."""

from decimal import Decimal
from pathlib import Path
import argparse
import re


DATA_RE = re.compile(
    r"^\s*(?P<channel>\d+)\s*(?:,\s*|\s+)"
    r"(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*$"
)


def read_values(path: Path) -> dict[int, Decimal]:
    values = {}

    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            stripped = line.strip()

            if not stripped or stripped.startswith("#") or stripped.upper().startswith("TABLE "):
                continue

            match = DATA_RE.match(line)
            if not match:
                raise ValueError(
                    f"Invalid data at {path}:{line_number}: {line.rstrip()}"
                )

            channel = int(match.group("channel"))
            if channel in values:
                raise ValueError(f"Duplicate channel {channel} in {path}")

            values[channel] = Decimal(match.group("value"))

    return values


def apply_corrections(
    calibration_file: Path,
    correction_file: Path,
    output_file: Path,
) -> None:
    calibrations = read_values(calibration_file)
    corrections = read_values(correction_file)

    if set(calibrations) != set(corrections):
        missing = sorted(set(calibrations) - set(corrections))
        extra = sorted(set(corrections) - set(calibrations))
        raise ValueError(f"Channel mismatch: missing={missing}, extra={extra}")

    with calibration_file.open(encoding="utf-8") as source, \
         output_file.open("w", encoding="utf-8") as destination:

        for line in source:
            match = DATA_RE.match(line)

            if not match:
                # Keep headers and comments, changing the calibration identifier.
                destination.write(line.replace("cid 301", "cid 302"))
                continue

            channel = int(match.group("channel"))
            corrected = calibrations[channel] - corrections[channel]
            destination.write(f"{channel:5d},{corrected:8.3f}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "calibration",
        type=Path,
        help="Input calibration file, e.g. CRVTime_cid_301.txt",
    )
    parser.add_argument(
        "corrections",
        type=Path,
        help="Correction file, e.g. CRVTime_cid_301_corr.txt",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("CRVTime_cid_302.txt"),
    )
    args = parser.parse_args()

    apply_corrections(args.calibration, args.corrections, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
