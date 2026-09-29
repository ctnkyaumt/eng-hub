#!/usr/bin/env python3
"""Forwarder to root refresh.py for backward compatibility."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if __name__ == "__main__":
    from refresh import main
    main()
