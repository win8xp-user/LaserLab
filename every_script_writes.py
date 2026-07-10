#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 20:55:58 2026

@author: serge
"""

from config import CONFIG
osa_host = CONFIG["instruments"]["osa20"]["host"]

from config import CONFIG
# osa = OSA20(CONFIG["instruments"]["osa20"])
# pm = PM103(CONFIG["instruments"]["pm103"])
# mpi = Sentio(CONFIG["instruments"]["mpi"])
PROBE_SIDE = CONFIG["laboratory"]["probe_station"]["side"]
FIBER_TYPE = CONFIG["laboratory"]["probe_station"]["fiber_type"]
