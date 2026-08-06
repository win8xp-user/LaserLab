# -*- coding: utf-8 -*-
"""
LaserLab
analysis/plots.py

Plotting utilities (Part A)

Version : 1.0.0
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch

# Part A
try:
    from .statistics import engineering
except Exception:
    def engineering(v, unit=""):
        return f"{v:.3g} {unit}".strip()

__version__ = "1.2.0"

FIGSIZE = (8,5)
DPI = 150
LINEWIDTH = 2
GRID_ALPHA = 0.30
FONT_SIZE = 11


def create_figure(title:str):
    plt.rcParams.update({"font.size": FONT_SIZE})
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_title(title)
    ax.grid(True, alpha=GRID_ALPHA)
    return fig, ax


def statistics_textbox(stats:dict, unit="W")->str:
    return (
        f"Samples : {stats['samples']}\n"
        f"Mean : {engineering(stats['mean'],unit)}\n"
        f"Std  : {engineering(stats['std'],unit)}\n"
        f"RSD  : {stats['rsd']:.2f}%\n"
        f"Min  : {engineering(stats['min'],unit)}\n"
        f"Max  : {engineering(stats['max'],unit)}"
    )


def finalize_figure(fig,
                    filename:Path,
                    show:bool=True,
                    close:bool=False):
    filename.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(filename,dpi=DPI,bbox_inches="tight")
    if show:
        plt.show()
    if close:
        plt.close(fig)
    return filename


def plot_time_trace(samples,
                    sample_interval:float=1.0,
                    statistics:Optional[dict]=None,
                    results_dir=".",
                    experiment="Measurement",
                    timestamp="",
                    show=True):

    y=np.asarray(samples,float)
    x=np.arange(len(y))*sample_interval

    title=f"{experiment} - Time Trace"
    if timestamp:
        title += f"\n{timestamp}"

    fig,ax=create_figure(title)

    ax.plot(x,y,lw=LINEWIDTH)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal")

    if statistics:
        ax.text(0.98,0.98,
                statistics_textbox(statistics),
                transform=ax.transAxes,
                va="top",
                ha="right",
                fontsize=9,
                bbox=dict(boxstyle="round",
                          facecolor="white",
                          alpha=0.85))

    fn=Path(results_dir)/"time_trace.png"
    return finalize_figure(fig,fn,show)


def plot_histogram(samples,
                   statistics:Optional[dict]=None,
                   results_dir=".",
                   experiment="Measurement",
                   timestamp="",
                   bins=30,
                   show=True):

    y=np.asarray(samples,float)

    title=f"{experiment} - Histogram"
    if timestamp:
        title += f"\n{timestamp}"

    fig,ax=create_figure(title)

    ax.hist(y,bins=bins,density=True,alpha=0.7,label="Histogram")

    if statistics:
        mu=statistics["mean"]
        sigma=statistics["std"]
        xs=np.linspace(y.min(),y.max(),400)
        pdf=(1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((xs-mu)/sigma)**2)
        ax.plot(xs,pdf,lw=2,label="Gaussian")
        ax.axvline(mu,color="r",ls="--",label="Mean")
        ax.axvline(mu-sigma,color="g",ls=":")
        ax.axvline(mu+sigma,color="g",ls=":")
        ax.text(0.98,0.98,
                statistics_textbox(statistics),
                transform=ax.transAxes,
                va="top",
                ha="right",
                fontsize=9,
                bbox=dict(boxstyle="round",
                          facecolor="white",
                          alpha=0.85))
    ax.set_xlabel("Signal")
    ax.set_ylabel("Probability Density")
    ax.legend()

    fn=Path(results_dir)/"histogram.png"
    return finalize_figure(fig,fn,show)


# Part B
def plot_cdf(samples, statistics=None, results_dir=".", experiment="Measurement",
             timestamp="", show=True):
    y=np.sort(np.asarray(samples,float))
    p=np.arange(1,len(y)+1)/len(y)
    title=f"{experiment} - Empirical CDF"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.plot(y,p,lw=2)
    ax.set_xlabel("Signal")
    ax.set_ylabel("Cumulative Probability")
    ax.set_ylim(0,1.02)
    if statistics:
        ax.text(0.98,0.02,statistics_textbox(statistics),
                transform=ax.transAxes,ha="right",va="bottom",
                fontsize=9,bbox=dict(boxstyle="round",facecolor="white",alpha=0.85))
    return finalize_figure(fig,Path(results_dir)/"cdf.png",show)

def plot_boxplot(samples, statistics=None, results_dir=".", experiment="Measurement",
                 timestamp="", show=True):
    y=np.asarray(samples,float)
    title=f"{experiment} - Box Plot"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.boxplot(y,vert=True,patch_artist=True,showmeans=True)
    ax.set_ylabel("Signal")
    ax.set_xticks([1]); ax.set_xticklabels([experiment])
    if statistics:
        ax.text(0.98,0.98,statistics_textbox(statistics),
                transform=ax.transAxes,ha="right",va="top",
                fontsize=9,bbox=dict(boxstyle="round",facecolor="white",alpha=0.85))
    return finalize_figure(fig,Path(results_dir)/"boxplot.png",show)

def plot_probability(samples, results_dir=".", experiment="Measurement",
                     timestamp="", show=True):
    """
    Normal probability (Q-Q) plot.
    Requires SciPy.
    """
    from scipy import stats
    y=np.asarray(samples,float)
    title=f"{experiment} - Normal Probability Plot"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    stats.probplot(y,dist="norm",plot=ax)
    ax.grid(True,alpha=0.3)
    return finalize_figure(fig,Path(results_dir)/"probability.png",show)

# Part C
def autocorrelation(samples):
    x=np.asarray(samples,float)
    x=x-np.mean(x)
    ac=np.correlate(x,x,mode="full")
    ac=ac[ac.size//2:]
    ac/=ac[0]
    return np.arange(len(ac)),ac

def plot_autocorrelation(samples,results_dir=".",experiment="Measurement",
                         timestamp="",show=True):
    lag,ac=autocorrelation(samples)
    title=f"{experiment} - Autocorrelation"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.plot(lag,ac,lw=2)
    ax.set_xlabel("Lag (samples)")
    ax.set_ylabel("Correlation")
    ax.set_ylim(-1.05,1.05)
    return finalize_figure(fig,Path(results_dir)/"autocorrelation.png",show)

def plot_fft(samples,sample_rate,results_dir=".",experiment="Measurement",
             timestamp="",show=True):
    y=np.asarray(samples,float)
    y=y-np.mean(y)
    n=len(y)
    freq=np.fft.rfftfreq(n,d=1/sample_rate)
    amp=np.abs(np.fft.rfft(y))/n
    title=f"{experiment} - FFT"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.plot(freq,amp,lw=2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    return finalize_figure(fig,Path(results_dir)/"fft.png",show)

def plot_psd(samples,sample_rate,results_dir=".",experiment="Measurement",
             timestamp="",show=True):
    y=np.asarray(samples,float)
    f,psd=welch(y,fs=sample_rate,nperseg=min(256,len(y)))
    title=f"{experiment} - Power Spectral Density"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.semilogy(f,psd,lw=2)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("PSD")
    return finalize_figure(fig,Path(results_dir)/"psd.png",show)

def allan_deviation(samples,sample_rate):
    x=np.asarray(samples,float)
    taus=[]; adev=[]
    max_m=len(x)//4
    m=1
    while m<=max_m:
        n=len(x)//m
        if n<2: break
        y=x[:n*m].reshape(n,m).mean(axis=1)
        av=np.sqrt(0.5*np.mean(np.diff(y)**2))
        taus.append(m/sample_rate)
        adev.append(av)
        m*=2
    return np.asarray(taus),np.asarray(adev)

def plot_allan(samples,sample_rate,results_dir=".",experiment="Measurement",
               timestamp="",show=True):
    tau,adev=allan_deviation(samples,sample_rate)
    title=f"{experiment} - Allan Deviation"
    if timestamp: title+=f"\n{timestamp}"
    fig,ax=create_figure(title)
    ax.loglog(tau,adev,marker="o")
    ax.set_xlabel("Averaging time τ (s)")
    ax.set_ylabel("Allan deviation")
    ax.grid(True,which="both",alpha=0.3)
    return finalize_figure(fig,Path(results_dir)/"allan.png",show)
