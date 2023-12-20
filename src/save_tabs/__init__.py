"""Allows importing between modules to occur without issues."""
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
