#!/usr/bin/env python
"""
Test script for the DL850E acquisition and plotting modules.
It imports the two helper modules and runs a complete test.
Simply set NUM_PHASES to 3, 6, or 9 and run.
"""

import os
import sys

sys.dont_write_bytecode = True

# Import the main functions from the helper modules
from acquire_waveforms import acquire_waveforms
from plot_waveforms import plot_csv_files

# ==================== CONFIGURATION ====================
# Directory where CSV files will be stored
BASE_DIR = r"C:\Users\hamza.rtelbennani\Desktop\Scope Reader\ScopeReader\csv waves"

# Number of phases: 3 (ch1-2), 6 (ch1-4), or 9 (ch1-6)
NUM_PHASES = 9   # <-- Change this to 3, 6, or 9 as needed
# ======================================================

def main():
    # Validate NUM_PHASES
    if NUM_PHASES not in (3, 6, 9):
        print(f"Error: NUM_PHASES must be 3, 6, or 9; got {NUM_PHASES}")
        sys.exit(1)

    print(f"=== Starting acquisition for {NUM_PHASES} phases ===")
    # Acquire waveforms; returns a list of 6 paths (None for unused channels)
    paths = acquire_waveforms(BASE_DIR, NUM_PHASES)

    # Print which files were generated
    print("\n=== Acquisition complete ===")
    for i, p in enumerate(paths, start=1):
        if p is not None:
            print(f"CH{i:02d}: {p}")
        else:
            print(f"CH{i:02d}: (not acquired)")

    # Filter out None values for plotting
    valid_paths = [p for p in paths if p is not None]
    if valid_paths:
        print(f"\n=== Plotting {len(valid_paths)} waveform(s) ===")
        output_plot = os.path.join(BASE_DIR, "waveforms_plot.png")
        plot_csv_files(valid_paths, output_path=output_plot)
        print(f"Plot saved to {output_plot}")
    else:
        print("\nNo valid CSV files to plot.")


if __name__ == "__main__":
    main()