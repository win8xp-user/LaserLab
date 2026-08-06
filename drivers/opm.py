#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 22:04:26 2026

===============================================================================
LaserLab
===============================================================================

Module
------
opm.py

Instrument
----------
Thorlabs PM103 Optical Power Meter

Description
-----------
LaserLab driver for the Thorlabs PM103 Optical Power Meter.

This driver is intentionally lightweight and contains only instrument
communication. It does not contain any experiment logic, plotting,
or file handling.

Python
------
Python 3.10

Dependencies
------------
pyvisa

Status
------
DEVELOPMENT

Version
-------
4.0.0

History
-------
4.0.0
    Initial LaserLab implementation.
===============================================================================
"""

from __future__ import annotations

import time
from typing import Optional

import pyvisa

__version__ = "4.0.0"


# =============================================================================
# Exceptions
# =============================================================================

class PM103Error(RuntimeError):
    """Base exception raised by the PM103 driver."""


class PM103ConnectionError(PM103Error):
    """Unable to establish communication with the PM103."""


class PM103CommunicationError(PM103Error):
    """Communication with the PM103 failed."""


# =============================================================================
# PM103 Driver
# =============================================================================

class PM103:
    """
    LaserLab driver for the Thorlabs PM103 Optical Power Meter.

    Notes
    -----
    The constructor only stores the configuration.

    Communication with the instrument starts when connect() is called.

    Example
    -------
    >>> pm = PM103(resource)
    >>> pm.connect()
    >>> power = pm.read_power()
    >>> pm.close()
    """

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(
        self,
        address: str,
        timeout_ms: int = 5000,
        query_delay_s: float = 0.02,
        default_wavelength_nm: Optional[float] = None,
        averaging_count: Optional[int] = None,
        unit: str = "W",
        strict_errors: bool = True,
        verbose: bool = False,
    ) -> None:

        self.address = address

        self.timeout_ms = timeout_ms
        self.query_delay_s = query_delay_s

        self.default_wavelength_nm = default_wavelength_nm
        self.averaging_count = averaging_count

        self.unit = unit
        self.strict_errors = strict_errors

        self.verbose = verbose

        self.rm = None
        self.instrument = None

        self.idn = ""

    # -------------------------------------------------------------------------
    # Connection
    # -------------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the PM103.
        """

        if self.instrument is not None:
            return

        try:

            self.rm = pyvisa.ResourceManager()

            self.instrument = self.rm.open_resource(
                self.address,
                read_termination="\n",
                write_termination="\n",
            )

            self.instrument.timeout = self.timeout_ms
            self.instrument.query_delay = self.query_delay_s

            # Clear status

            self.instrument.write("*CLS")

            # Read identification

            self.idn = self.instrument.query("*IDN?").strip()

            # Apply default configuration

            self.set_unit(self.unit)

            if self.default_wavelength_nm is not None:
                self.set_wavelength_nm(
                    self.default_wavelength_nm
                )

            # if self.averaging_count is not None:
            #     self.set_averaging_count(
            #         self.averaging_count
            #     )

            self.set_autorange(True)

        except Exception as err:

            raise PM103ConnectionError(
                f"Unable to connect to PM103:\n{err}"
            ) from err

    def disconnect(self) -> None:
        """
        Disconnect from the instrument.
        """

        try:

            if self.instrument is not None:
                self.instrument.close()

        finally:

            self.instrument = None

            if self.rm is not None:
                try:
                    self.rm.close()
                except Exception:
                    pass

            self.rm = None

    def close(self) -> None:
        """
        Alias for disconnect().
        """
        self.disconnect()

    # -------------------------------------------------------------------------
    # Context manager
    # -------------------------------------------------------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.disconnect()

        return False

    # -------------------------------------------------------------------------
    # Internal communication
    # -------------------------------------------------------------------------

    def _check_connection(self) -> None:

        if self.instrument is None:
            raise PM103ConnectionError(
                "PM103 is not connected."
            )

    def _write(self, command: str) -> None:

        self._check_connection()

        if self.verbose:
            print(f"PM103 >> {command}")

        self.instrument.write(command)

        if self.strict_errors:
            self._raise_if_error()

    def _query(self, command: str) -> str:

        self._check_connection()

        if self.verbose:
            print(f"PM103 >> {command}")

        reply = self.instrument.query(command).strip()

        if self.verbose:
            print(f"PM103 << {reply}")

        return reply

    def _raise_if_error(self) -> None:

        try:

            err = self.instrument.query(
                "SYST:ERR?"
            ).strip()

        except Exception as exc:

            raise PM103CommunicationError(
                f"Unable to query error queue:\n{exc}"
            ) from exc

        if not (
            err.startswith("0")
            or err.lower().startswith("no error")
        ):

            raise PM103CommunicationError(err)

    # -------------------------------------------------------------------------
    # General utilities
    # -------------------------------------------------------------------------

    def identify(self) -> str:
        """
        Return the instrument identification string.
        """
        return self.idn

    def is_connected(self) -> bool:
        """
        True if connected.
        """
        return self.instrument is not None

# ===== End of Part A =====
# 
# =============================================================================
# Configuration
# =============================================================================

    def reset(self) -> None:
        """
        Reset the PM103 to its default state.
        """
        self._write("*RST")
        time.sleep(0.2)

    # -------------------------------------------------------------------------

    def set_unit(self, unit: str = "W") -> None:
        """
        Set measurement unit.

        Parameters
        ----------
        unit : str

            "W"   : Watts

            "DBM" : dBm
        """

        unit = unit.upper()

        if unit not in ("W", "DBM"):
            raise ValueError(
                "Unit must be 'W' or 'DBM'."
            )

        self._write(
            f"SENSE:POWER:UNIT {unit}"
        )

        self.unit = unit

    # -------------------------------------------------------------------------

    def get_unit(self) -> str:
        """
        Return the current measurement unit.
        """
        return self._query(
            "SENSE:POWER:UNIT?"
        )

    # -------------------------------------------------------------------------

    def set_wavelength_nm(
        self,
        wavelength_nm: float
    ) -> None:
        """
        Set calibration wavelength.
        """

        if wavelength_nm <= 0:
            raise ValueError(
                "Wavelength must be positive."
            )

        self._write(
            f"SENSE:CORRECTION:WAVELENGTH "
            f"{wavelength_nm}"
        )

        self.default_wavelength_nm = wavelength_nm

    # -------------------------------------------------------------------------

    def get_wavelength_nm(self) -> float:
        """
        Return calibration wavelength in nm.
        """

        return float(
            self._query(
                "SENSE:CORRECTION:WAVELENGTH?"
            )
        )

    # -------------------------------------------------------------------------

    def set_autorange(
        self,
        enable: bool = True
    ) -> None:
        """
        Enable or disable autoranging.
        """

        state = "ON" if enable else "OFF"

        self._write(
            f"SENSE:POWER:DC:RANGE:AUTO {state}"
        )

        time.sleep(0.05)

    # -------------------------------------------------------------------------

    def autorange_state(self) -> bool:
        """
        Return True if autoranging is enabled.
        """

        reply = self._query(
            "SENSE:POWER:DC:RANGE:AUTO?"
        )

        return reply.upper() in ("1", "ON")

    # -------------------------------------------------------------------------

    def auto_range_off(self) -> None:
        """
        Disable autoranging.
        """

        self.set_autorange(False)

    # -------------------------------------------------------------------------

    def set_manual_range(
        self,
        upper_watts: float
    ) -> None:
        """
        Set manual power range.
        """

        if upper_watts <= 0:
            raise ValueError(
                "Range must be positive."
            )

        self.auto_range_off()

        self._write(
            f"SENSE:POWER:DC:RANGE:UPPER "
            f"{upper_watts}"
        )

        time.sleep(0.05)

    # -------------------------------------------------------------------------

    def get_manual_range(self) -> float:
        """
        Return current manual range in Watts.
        """

        return float(
            self._query(
                "SENSE:POWER:DC:RANGE:UPPER?"
            )
        )

    # -------------------------------------------------------------------------

    def zero(self) -> None:
        """
        Perform zero adjustment.

        Note
        ----
        No optical power should be incident on the sensor.
        """

        self._write(
            "SENSE:CORRECTION:COLLECT:ZERO"
        )

    # -------------------------------------------------------------------------

    def info(self) -> dict:
        """
        Return instrument information.
        """

        return {

            "Instrument": "Thorlabs PM103",

            "Identification": self.identify(),

            "Connected": self.is_connected(),

            "Unit": self.get_unit(),

            "Wavelength (nm)": self.get_wavelength_nm(),

            "Autorange": self.autorange_state()
        }
    
# ===== End of Part B =====

# =============================================================================
# Measurements
# =============================================================================

    def read_power(self) -> float:
        """
        Read optical power.

        Returns
        -------
        float
            Optical power in the currently selected unit.
        """

        try:

            return float(
                self._query("MEASURE:POWER?")
            )

        except PM103CommunicationError:
            raise

        except Exception:

            # Some firmware versions prefer READ?
            return float(
                self._query("READ?")
            )

    # -------------------------------------------------------------------------

    # Backward compatibility
    measure = read_power

    # -------------------------------------------------------------------------

    def read_average(
        self,
        samples: int = 10,
        delay_s: float = 0.02
    ) -> float:
        """
        Read the average optical power.

        Parameters
        ----------
        samples : int
            Number of samples.

        delay_s : float
            Delay between samples.

        Returns
        -------
        float
            Average optical power.
        """

        if samples <= 0:
            raise ValueError(
                "samples must be positive."
            )

        values = []

        for _ in range(samples):

            values.append(
                self.read_power()
            )

            if delay_s > 0:
                time.sleep(delay_s)

        return sum(values) / len(values)

    # -------------------------------------------------------------------------

    def read_statistics(
        self,
        samples: int = 20,
        delay_s: float = 0.02
    ) -> dict:
        """
        Read simple statistics.

        Returns
        -------
        dict
            mean
            std
            min
            max
            samples
        """

        if samples <= 0:
            raise ValueError(
                "samples must be positive."
            )

        values = []

        for _ in range(samples):

            values.append(
                self.read_power()
            )

            if delay_s > 0:
                time.sleep(delay_s)

        mean = sum(values) / len(values)

        if len(values) > 1:

            variance = sum(
                (v - mean) ** 2
                for v in values
            ) / (len(values) - 1)

            std = variance ** 0.5

        else:

            std = 0.0

        return {

            "mean": mean,

            "std": std,

            "min": min(values),

            "max": max(values),

            "samples": len(values)
        }

    # -------------------------------------------------------------------------

    def version(self) -> str:
        """
        Return driver version.
        """

        return __version__


# =============================================================================
# Backward compatibility
# =============================================================================

OPM = PM103


# =============================================================================
# End of file
# =============================================================================