# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 20:57:43 2026

"""

# kxci5.py
# ---------------------------------------------------------------
# USER‑MODE driver for Keithley 4200/4200A KXCI
# Single-socket (stable, flicker-free output).
# ---------------------------------------------------------------

from socket import socket, AF_INET, SOCK_STREAM
import time

class KXCIInstrument:
    def __init__(self, address: str, port: int, read_timeout_s: float = 2.0):
        self.fd = socket(AF_INET, SOCK_STREAM)
        self.fd.connect((address, port))
        self.fd.settimeout(read_timeout_s)
        self._rx = b""  # frame buffer

    def close(self):
        try:
            self.fd.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    # -------------------------
    # Framed transport
    # -------------------------
    def _send(self, cmd: str):
        self.fd.sendall((cmd + "\0").encode("ascii"))

    def _read_frame(self, timeout_s=2.0):
        end = time.time() + timeout_s
        while True:
            idx = self._rx.find(b"\0")
            if idx != -1:
                msg = self._rx[:idx]
                self._rx = self._rx[idx+1:]
                return msg.decode("ascii", errors="ignore").strip()

            if time.time() >= end:
                raise TimeoutError("Timeout waiting for KXCI frame")

            self.fd.settimeout(max(0.0, end - time.time()))
            chunk = self.fd.recv(4096)
            if not chunk:
                time.sleep(0.001)
                continue
            self._rx += chunk

    def run(self, cmd: str, expect_reply=False, timeout_s=2.0):
        self._send(cmd)
        first = self._read_frame(timeout_s)
        if not expect_reply:
            return first

        if first != "ACK":
            return first

        end = time.time() + timeout_s
        while True:
            if time.time() > end:
                return first
            nxt = self._read_frame(timeout_s)
            if nxt != "ACK":
                return nxt

    def query(self, cmd: str, timeout_s=2.0):
        return self.run(cmd, expect_reply=True, timeout_s=timeout_s)


# ================================================================
# USER‑MODE high-level driver
# ================================================================
class K4200UserSMU(KXCIInstrument):

    # ------------------------------------------------
    # USER-MODE INIT
    # ------------------------------------------------
    def reset_user_mode(self):
        """Reset instrument + enter USER MODE (global state)."""
        self.run("*RST")
        self.run("US")      # USER MODE
        self.run("BC")      # clear buffer
        self.run("SP")      # clear status

    def set_integration_plc(self, plc: float):
        if float(plc).is_integer():
            self.run(f"IT{int(plc)}")
        else:
            self.run(f"IT{float(plc)}")

    # ------------------------------------------------
    # SOURCING
    # ------------------------------------------------
    def source_current(self, ch: int, irange: int, current_A: float, vcomp_V: float):
        self.run(f"DI{ch}, {irange}, {current_A:.9g}, {vcomp_V:.9g}")

    def source_voltage(self, ch: int, vrange: int, voltage_V: float, icomp_A: float):
        self.run(f"DV{ch}, {vrange}, {voltage_V:.9g}, {icomp_A:.9g}")

    def output_off(self, ch: int, mode: str):
        mode = mode.upper()
        if mode == "I":
            self.run(f"DI{ch}")
        elif mode == "V":
            self.run(f"DV{ch}")
        else:
            raise ValueError("Mode must be 'I' or 'V'")

    def safe_turn_off_all(self):
        for ch in (1,2,3,4):
            try: self.output_off(ch,"I")
            except: pass
            try: self.output_off(ch,"V")
            except: pass

    # ------------------------------------------------
    # MEASUREMENT (TV/TI)
    # ------------------------------------------------
    @staticmethod
    def _parse_value(line: str):
        if not line:
            return float("nan")
        s=line.strip()
        i=0
        while i < len(s) and s[i] not in "+-0123456789.":
            i+=1
        try:
            return float(s[i:])
        except:
            return float("nan")

    def measure_voltage(self, ch: int):
        return self._parse_value(self.run(f"TV {ch}"))

    def measure_current(self, ch: int):
        return self._parse_value(self.run(f"TI {ch}"))

    def read_vi(self, ch: int):
        return self.measure_voltage(ch), self.measure_current(ch)