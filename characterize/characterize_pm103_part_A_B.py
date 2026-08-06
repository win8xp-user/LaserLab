
# -*- coding: utf-8 -*-
"""
LaserLab

Application:
    characterize_pm103.py

Part A - Initialization and Instrument Setup

Version:
    1.0.0

Description
-----------
Initializes the PM103 characterization experiment.

This part:
    - Creates a timestamped results directory
    - Connects to the PM103
    - Connects to the Keithley K4200
    - Configures the PM103
    - Applies laser bias
    - Creates experiment metadata

Part B will perform acquisition.
Part C will perform analysis and reporting.
"""

from __future__ import annotations

from pathlib import Path
import time

from drivers.opm import PM103
from drivers.kxci5 import K4200UserSMU

from utils.filesystem import (
    create_results_directory,
    timestamp,
)

from analysis.statistics import compute_statistics

from utils.filesystem import (
    save_metadata,
    save_statistics,
    save_raw_samples,
    save_report,
    measurement_summary,
)

    

APP_NAME = "LaserLab"
APP_VERSION = "1.0.0"

EXPERIMENT = "PM103"

RESULTS_DIR = Path(__file__).parent / "results"

PM103_ADDRESS = "USB0::0x1313::0x807A::M01044648::INSTR"
PM103_WAVELENGTH = 1310.0
PM103_MANUAL_RANGE = 0.01

SMU_ADDRESS = ("10.58.12.208", 36001)

SMU3_IRANGE = 10
SMU3_CURRENT = 0.200
SMU3_VCOMPLIANCE = 6.5

SMU4_VRANGE = 1
SMU4_VOLTAGE = 0.0
SMU4_ICOMPLIANCE = 1.05

PLC = 2

NUMBER_OF_SAMPLES = 1000
SAMPLE_INTERVAL = 0.1


def print_banner():
    print("=" * 62)
    print(APP_NAME)
    print("=" * 62)
    print()
    print(f"{EXPERIMENT} Characterization")
    print(f"Version : {APP_VERSION}")
    print()


def connect_pm103() -> PM103:
    print("[1/4] Connecting PM103...")
    pm = PM103(PM103_ADDRESS)
    pm.set_wavelength_nm(PM103_WAVELENGTH)
    pm.set_manual_range(PM103_MANUAL_RANGE)
    print("    ✓ Connected")
    print(f"    IDN : {pm.idn()}")
    return pm


def connect_k4200() -> K4200UserSMU:
    print("[2/4] Connecting K4200...")
    smu = K4200UserSMU(*SMU_ADDRESS)
    smu.__enter__()
    smu.reset_user_mode()
    smu.set_integration_plc(PLC)
    print("    ✓ Connected")
    return smu

def acquire_samples(
    pm,
    number_of_samples,
    sample_interval,
):
    """
    Acquire optical power samples.

    Returns
    -------
    list
        Optical power samples [W]
    """

    samples = []

    print()
    print("Acquiring samples")
    print("-----------------")

    for i in range(number_of_samples):

        samples.append(float(pm.measure()))

        if ((i + 1) % 100 == 0) or (i + 1 == number_of_samples):
            print(f"   Sample {i + 1:5d}/{number_of_samples}")

        time.sleep(sample_interval)

    print("✓ Acquisition complete")

    return samples


def process_measurement(
    samples,
    metadata,
    results_dir,
):
    """
    Compute statistics and save experiment.
    """

    print()
    print("Computing statistics...")
    statistics = compute_statistics(samples)

    metadata["statistics"] = statistics

    print("Saving experiment...")

    save_metadata(
        results_dir,
        metadata,
    )

    save_raw_samples(
        results_dir,
        samples,
        SAMPLE_INTERVAL,
    )

    save_statistics(
        results_dir,
        statistics,
    )

    report = measurement_summary(
        metadata,
        statistics,
    )

    save_report(
        results_dir,
        report,
    )

    print("✓ metadata.json")
    print("✓ raw_samples.csv")
    print("✓ statistics.csv")
    print("✓ report.txt")

    return statistics

def apply_bias(smu: K4200UserSMU):
    print("[3/4] Applying laser bias...")
    smu.source_current(3, SMU3_IRANGE, SMU3_CURRENT, SMU3_VCOMPLIANCE)
    smu.source_voltage(4, SMU4_VRANGE, SMU4_VOLTAGE, SMU4_ICOMPLIANCE)
    time.sleep(2)

    v3, i3 = smu.read_vi(3)
    v4, i4 = smu.read_vi(4)

    print(f"    SMU3 : {v3:6.3f} V   {i3*1000:7.1f} mA")
    print(f"    SMU4 : {v4:6.3f} V   {i4*1000:7.1f} mA")

    return {
        "SMU3_voltage_V": v3,
        "SMU3_current_A": i3,
        "SMU4_voltage_V": v4,
        "SMU4_current_A": i4,
    }


def create_metadata(bias: dict) -> dict:
    return {
        "application": APP_NAME,
        "application_version": APP_VERSION,
        "experiment": EXPERIMENT,
        "timestamp": timestamp(),
        "instrument": {
            "pm103_wavelength_nm": PM103_WAVELENGTH,
            "manual_range_W": PM103_MANUAL_RANGE,
        },
        "measurement": {
            "samples": NUMBER_OF_SAMPLES,
            "sample_interval_s": SAMPLE_INTERVAL,
        },
        "bias": bias,
    }


def main():
    print_banner()

    results = create_results_directory(EXPERIMENT, RESULTS_DIR)

    print(f"Timestamp : {timestamp()}")
    print(f"Results   : {results}")
    print()

    pm = None
    smu = None

    try:
        pm = connect_pm103()
        smu = connect_k4200()
        bias = apply_bias(smu)
        metadata = create_metadata(bias)
        
        print("[4/4] Initialization complete")
        print("    ✓ Metadata created")
        print()

        samples = acquire_samples(
            pm,
            NUMBER_OF_SAMPLES,
            SAMPLE_INTERVAL,
        )
        
        statistics = process_measurement(
            samples,
            metadata,
            results,
        )
        
        print()
        print("Ready for plotting (Part C).")
        return samples, statistics, metadata, results


    except Exception:
        raise

    finally:
        if smu is not None:
            try:
                smu.safe_turn_off_all()
                smu.__exit__(None, None, None)
            except Exception:
                pass


if __name__ == "__main__":
    main()
