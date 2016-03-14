#!/usr/bin/env python

# Runs the standard XOS synchronizer

import importlib
import os
import sys

synchronizer_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../synchronizers/base")
sys.path.append(synchronizer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()

