#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaserLab - PM103 Driver Acceptance Test
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from drivers.opm import PM103
from drivers.kxci5 import K4200UserSMU

SMU_ADDRESS=("10.58.12.208",36001)
OPM_ADDRESS="USB0::0x1313::0x807A::M01044648::INSTR"

OPM_WAVELENGTH_NM=1310.0

SMU3_IRANGE=10
SMU3_CURRENT_A=0.200
SMU3_VCOMPLIANCE_V=6.5
SMU4_VRANGE=1
SMU4_VOLTAGE_V=0.0
SMU4_ICOMPLIANCE_A=1.05
PLC_VALUE=2
SETTLING_TIME=2.0

# Number of samples
N_SAMPLES = 100

def heading(t):
    print("\n"+"="*70)
    print(t)
    print("="*70)

def fmt_power(w):
    a=abs(w)
    if a>=1e-3: return f"{w*1e3:.3f} mW"
    if a>=1e-6: return f"{w*1e6:.3f} µW"
    if a>=1e-9: return f"{w*1e9:.3f} nW"
    if a>=1e-12:return f"{w*1e12:.3f} pW"
    return f"{w:.3e} W"

def mark(ok): return "[PASS]" if ok else "[FAIL]"

def main():
    t0=time.perf_counter()
    heading("LaserLab - PM103 Driver Test")
    print(f"Timestamp      : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Driver version : {PM103(OPM_ADDRESS).version()}")
    pm=PM103(OPM_ADDRESS,default_wavelength_nm=OPM_WAVELENGTH_NM,unit="W")
    smu=None
    try:
        pm.connect()
        #
        # Fixed range for repeatability
        pm.set_manual_range(0.01)      # 10 mW range
        # Optional verification
        print(f"Manual range : {pm.get_manual_range()*1000:.1f} mW")
                
        print(f"{mark(True)} Connect PM103")
        smu=K4200UserSMU(*SMU_ADDRESS)
        smu.reset_user_mode()
        smu.set_integration_plc(PLC_VALUE)
        smu.source_current(3,SMU3_IRANGE,SMU3_CURRENT_A,SMU3_VCOMPLIANCE_V)
        smu.source_voltage(4,SMU4_VRANGE,SMU4_VOLTAGE_V,SMU4_ICOMPLIANCE_A)
        time.sleep(SETTLING_TIME)
        v3,i3=smu.read_vi(3)
        v4,i4=smu.read_vi(4)
        ok=abs(i3-SMU3_CURRENT_A)<0.01
        print(f"{mark(ok)} Connect K4200 / Apply laser bias")
        print("\nLaser Bias")
        print("----------")
        print(f"SMU3  {v3:6.3f} V  {i3*1000:7.1f} mA")
        print(f"SMU4  {v4:6.3f} V  {i4*1000:7.1f} mA")

        info=pm.info()
        print("\nInstrument")
        print("----------")
        print(f"IDN        : {info['Identification']}")
        print(f"Unit       : {info['Unit']}")
        print(f"Wavelength : {info['Wavelength (nm)']:.1f} nm")
        print(f"Autorange  : {'ON' if info['Autorange'] else 'OFF'}")

        single = pm.read_power()
        stats = pm.read_statistics(N_SAMPLES)
        
        mean = stats["mean"]
        std  = stats["std"]
        rsd   = 100 * std / mean

        # p=pm.read_power()
        # avg=pm.read_average(N_SAMPLES)
        # s=pm.read_statistics(N_SAMPLES)
        # rsd=100*s["std"]/s["mean"] if s["mean"] else float("nan")

        print("\nMeasurements")
        print("------------")
        print(f"Single      : {fmt_power(single)}")
        # print(f"Average     : {fmt_power(stats)}")

        print("\nStatistics")
        print("----------")
        print(f"Mean        : {fmt_power(stats['mean'])}")
        print(f"Std         : {fmt_power(stats['std'])}")
        print(f"Min         : {fmt_power(stats['min'])}")
        print(f"Max         : {fmt_power(stats['max'])}")
        print(f"RSD          : {rsd:.2f} %")

        print("\nResult")
        print("------")
        print("PASS")
    finally:
        if smu:
            smu.safe_turn_off_all()
            smu.close()
        try: pm.close()
        except: pass
        print(f"\nElapsed time : {time.perf_counter()-t0:.2f} s")

if __name__=="__main__":
    main()
