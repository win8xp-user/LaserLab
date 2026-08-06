# -*- coding: utf-8 -*-
"""
statistics.py - LaserLab Analysis Module
Version 1.1.0
"""
from __future__ import annotations
from typing import Any
import csv
import numpy as np
from numpy.typing import ArrayLike
from scipy import stats
__version__="1.1.0"

def compute_statistics(samples:ArrayLike)->dict[str,Any]:
    x=np.asarray(samples,dtype=float)
    x=x[np.isfinite(x)]
    if x.ndim!=1: raise ValueError("samples must be a 1-D array")
    if x.size<2: raise ValueError("At least two finite samples are required.")
    mean=float(np.mean(x)); median=float(np.median(x))
    std=float(np.std(x,ddof=1)); var=float(np.var(x,ddof=1))
    sem=float(std/np.sqrt(x.size)); rms=float(np.sqrt(np.mean(x**2)))
    mn=float(np.min(x)); mx=float(np.max(x)); rng=float(mx-mn)
    rsd=float(100*std/mean) if mean!=0 else float("nan")
    return {
      "samples":int(x.size),"mean":mean,"median":median,"std":std,
      "variance":var,"sem":sem,"confidence95":float(1.96*sem),
      "rms":rms,"min":mn,"max":mx,"range":rng,"peak_to_peak":rng,
      "dynamic_range":float(mx/mn) if mn>0 else float("nan"),
      "p5":float(np.percentile(x,5)),"p25":float(np.percentile(x,25)),
      "p75":float(np.percentile(x,75)),"p95":float(np.percentile(x,95)),
      "iqr":float(np.percentile(x,75)-np.percentile(x,25)),
      "rsd":rsd,"cv":rsd,
      "skewness":float(stats.skew(x,bias=False)),
      "kurtosis":float(stats.kurtosis(x,fisher=True,bias=False))
    }

def engineering(value:float,unit:str="")->str:
    value=float(value); a=abs(value)
    for s,p in [(1e9,"G"),(1e6,"M"),(1e3,"k"),(1,""),(1e-3,"m"),(1e-6,"µ"),(1e-9,"n"),(1e-12,"p")]:
        if a>=s: return f"{value/s:.3f} {p}{unit}".strip()
    return f"{value:.3e} {unit}".strip()

def save_statistics_csv(filename:str,statistics:dict[str,Any])->None:
    with open(filename,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["Parameter","Value"])
        [w.writerow([k,v]) for k,v in statistics.items()]
