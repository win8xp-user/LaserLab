#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 20:48:37 2026

@author: serge
"""

from pathlib import Path
import json

CONFIG_FILE = Path(__file__).with_name("config.json")

with open(CONFIG_FILE) as f:
    CONFIG = json.load(f)