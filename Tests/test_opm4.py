#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 22:06:33 2026

@author: TM0019
"""

from opm import PM103
import statistics
import time


ADDRESS = "USB0::0x1313::0x80B0::XXXXXXXX::INSTR"


def heading(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():

    heading("PM103 Driver Test")

    pm = PM103(
        address=ADDRESS,
        default_wavelength_nm=1310,
        unit="W",
        verbose=False,
    )

    try:

        print("Connecting...")
        pm.connect()

        print("Connected")
        print(pm.identify())

        heading("Instrument information")

        info = pm.info()

        for key, value in info.items():
            print(f"{key:20s}: {value}")

        heading("Single measurement")

        p = pm.read_power()

        print(f"Power = {p:.6e} W")

        heading("Average")

        pavg = pm.read_average(samples=20)

        print(f"Average = {pavg:.6e} W")

        heading("Statistics")

        stats = pm.read_statistics(samples=50)

        for k, v in stats.items():
            print(f"{k:10s}: {v}")

    finally:

        pm.close()

        print("\nDisconnected")


if __name__ == "__main__":
    main()
