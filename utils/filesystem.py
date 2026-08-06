# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 21:18:34 2026

@author: Measmatic

LaserLab

utils/filesystem.py

General filesystem utilities.

Project : LaserLab
Version : 1.0.0
"""

from __future__ import annotations

import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Any, Iterable
import csv
import json
import re

__version__ = "1.0.0"


# =============================================================================
# Timestamp
# =============================================================================

def timestamp() -> str:
    """Return timestamp in YYYYMMDD_HHMMSS format."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# Safe filename
# =============================================================================

def safe_filename(name: str) -> str:
    """
    Convert a string into a filesystem-safe filename.
    """
    name = name.strip()
    name = name.replace(" ", "_")
    name = re.sub(r'[<>:"/\\\\|?*]', "", name)
    return name


# =============================================================================
# Create results directory
# =============================================================================

# def create_results_directory(
#     experiment: str,
#     base_directory: str | Path = "test_results",
# ) -> Path:
#     """
#     Create a timestamped experiment directory.

#     Example
#     -------
#     test_results/

#         PM103_20260806_214352/
#     """

#     experiment = safe_filename(experiment)

#     folder = (
#         Path(base_directory)
#         / f"{experiment}_{timestamp()}"
#     )

#     folder.mkdir(
#         parents=True,
#         exist_ok=True,
#     )

#     return folder

def create_results_directory(
    experiment: str,
    base_directory: str | Path,
) -> Path:
    """
    Create a timestamped experiment directory.

    Parameters
    ----------
    experiment : str
        Experiment name.

    base_directory : str or Path
        Root directory where results will be stored.

    Returns
    -------
    Path
        Path to the newly created experiment directory.

    Example
    -------
    create_results_directory(
        "PM103",
        "characterize/results"
    )

    creates

    characterize/results/

        PM103_20260806_214352/
    """

    experiment = safe_filename(experiment)

    folder = Path(base_directory) / f"{experiment}_{timestamp()}"

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return folder

# =============================================================================
# Prevent overwriting
# =============================================================================

def get_next_filename(filename: str | Path) -> Path:
    """
    If filename exists:

        report.txt

    becomes

        report_001.txt

        report_002.txt

        ...
    """

    filename = Path(filename)

    if not filename.exists():
        return filename

    stem = filename.stem
    suffix = filename.suffix
    parent = filename.parent

    i = 1

    while True:

        new_file = parent / f"{stem}_{i:03d}{suffix}"

        if not new_file.exists():
            return new_file

        i += 1


# =============================================================================
# Save text
# =============================================================================

def save_text(
    filename: str | Path,
    text: str,
) -> Path:

    filename = get_next_filename(filename)

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:

        f.write(text)

    return filename


# =============================================================================
# Save JSON
# =============================================================================

def save_json(
    filename: str | Path,
    data: Any,
) -> Path:

    filename = get_next_filename(filename)

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )

    return filename


# =============================================================================
# Save CSV
# =============================================================================

def save_csv(
    filename: str | Path,
    rows: Iterable,
    header: Iterable[str] | None = None,
) -> Path:

    filename = get_next_filename(filename)

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.writer(f)

        if header is not None:
            writer.writerow(header)

        writer.writerows(rows)

    return filename


# Part B
def save_metadata(results_dir, metadata):
    """
    Save experiment metadata to metadata.json.
    """
    filename = Path(results_dir) / "metadata.json"
    return save_json(filename, metadata)

def save_statistics(results_dir, statistics):
    """
    Save statistics dictionary to statistics.csv.
    """

    filename = Path(results_dir) / "statistics.csv"

    rows = [
        (key, value)
        for key, value in statistics.items()
    ]

    return save_csv(
        filename,
        rows,
        header=["Parameter", "Value"],
    )


def save_raw_samples(
    results_dir,
    samples,
    sample_interval=None,
):
    """
    Save raw measurement samples.
    """

    filename = Path(results_dir) / "raw_samples.csv"

    samples = np.asarray(samples)

    rows = []

    for i, value in enumerate(samples):

        if sample_interval is None:
            rows.append([i + 1, value])

        else:
            rows.append(
                [
                    i + 1,
                    i * sample_interval,
                    value,
                ]
            )

    header = ["Sample", "Value"]

    if sample_interval is not None:
        header = [
            "Sample",
            "Time_s",
            "Value",
        ]

    return save_csv(
        filename,
        rows,
        header,
    )

def save_report(
    results_dir,
    report,
):
    """
    Save report.txt.
    """

    filename = Path(results_dir) / "report.txt"

    return save_text(
        filename,
        report,
    )

def load_json(filename):
    """
    Load JSON file.
    """

    filename = Path(filename)

    with open(
        filename,
        encoding="utf-8",
    ) as f:

        return json.load(f)
    
def load_csv(filename):
    """
    Load CSV file.

    Returns
    -------
    list
    """

    filename = Path(filename)

    with open(
        filename,
        newline="",
        encoding="utf-8",
    ) as f:

        return list(csv.reader(f))

def measurement_summary(
    metadata: dict,
    statistics: dict,
) -> str:
    """
    Generate a human-readable experiment summary.
    """

    lines = []

    lines.append("=" * 60)
    lines.append("LaserLab Measurement Report")
    lines.append("=" * 60)
    lines.append("")

    lines.append("Experiment")
    lines.append("----------")
    lines.append(f"Name       : {metadata.get('experiment','')}")
    lines.append(f"Timestamp  : {metadata.get('timestamp','')}")
    lines.append("")

    lines.append("Measurement")
    lines.append("-----------")
    meas = metadata.get("measurement", {})
    lines.append(f"Samples    : {meas.get('samples','')}")
    lines.append(f"Interval   : {meas.get('sample_interval_s','')} s")
    lines.append("")

    lines.append("Statistics")
    lines.append("----------")

    lines.append(f"Mean       : {statistics['mean']:.6e} W")
    lines.append(f"Std        : {statistics['std']:.6e} W")
    lines.append(f"Min        : {statistics['min']:.6e} W")
    lines.append(f"Max        : {statistics['max']:.6e} W")
    lines.append(f"Median     : {statistics['median']:.6e} W")
    lines.append(f"RSD        : {statistics['rsd']:.2f} %")

    return "\n".join(lines)


