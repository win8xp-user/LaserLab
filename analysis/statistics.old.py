# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 19:57:15 2026

@author: Measmatic

statistics.py

LaserLab Analysis Module

Statistical analysis routines for measurement data.

Project: LaserLab
Version: 1.0.0
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def compute_statistics(samples):
    """
    Compute descriptive statistics for a measurement array.

    Parameters
    ----------
    samples : array_like
        1-D measurement array.

    Returns
    -------
    dict
        Dictionary containing descriptive statistics.
    """

    x = np.asarray(samples, dtype=float)

    if x.ndim != 1:
        raise ValueError("samples must be a 1-D array")

    if len(x) < 2:
        raise ValueError("At least two samples are required.")

    mean = np.mean(x)
    median = np.median(x)
    std = np.std(x, ddof=1)
    variance = np.var(x, ddof=1)

    minimum = np.min(x)
    maximum = np.max(x)

    peak_to_peak = maximum - minimum

    p5 = np.percentile(x, 5)
    p25 = np.percentile(x, 25)
    p75 = np.percentile(x, 75)
    p95 = np.percentile(x, 95)

    iqr = p75 - p25

    rsd = 100.0 * std / mean if mean != 0 else np.nan

    skewness = stats.skew(x, bias=False)
    kurtosis = stats.kurtosis(x, fisher=True, bias=False)

    rms = np.sqrt(np.mean(x**2))

    return {
        "samples": len(x),

        "mean": mean,
        "median": median,

        "std": std,
        "variance": variance,
        "rms": rms,

        "min": minimum,
        "max": maximum,
        "peak_to_peak": peak_to_peak,

        "p5": p5,
        "p25": p25,
        "p75": p75,
        "p95": p95,

        "iqr": iqr,

        "rsd": rsd,

        "skewness": skewness,
        "kurtosis": kurtosis,
    }