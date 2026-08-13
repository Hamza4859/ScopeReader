#!/usr/bin/env python
"""
Test script for the DL850E acquisition and plotting modules.
It imports the two helper modules and runs a complete test.
Simply set NUM_PHASES to 3, 6, or 9 and run.
"""

import os
import sys
import shutil   # for deleting entire folder contents

sys.dont_write_bytecode = True

# Import the main functions from the helper modules
from acquire_waveforms import acquire_waveforms
from plot_waveforms import plot_csv_files

# ==================== CONFIGURATION ====================
# Directory where CSV files will be stored
BASE_DIR = r"C:\Users\hamza.rtelbennani\Desktop\Scope Reader\ScopeReader\csv waves"

# Number of phases: 3 (ch1-2), 6 (ch1-4), or 9 (ch1-6)
NUM_PHASES = 9  # <-- Change this to 3, 6, or 9 as needed
# ======================================================

def clean_folder(directory):
    """Delete ALL contents (files and subfolders) inside the given directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        return

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed folder: {item_path}")
        except Exception as e:
            print(f"Could not remove {item_path}: {e}")

def main():
    # Validate NUM_PHASES
    if NUM_PHASES not in (3, 6, 9):
        print(f"Error: NUM_PHASES must be 3, 6, or 9; got {NUM_PHASES}")
        sys.exit(1)

    # Clean the folder before acquisition
    print(f"Cleaning folder: {BASE_DIR}")
    clean_folder(BASE_DIR)

    print(f"=== Starting acquisition for {NUM_PHASES} phases ===")
    # Acquire waveforms; returns a list of 6 strings (empty for missing)
    paths = acquire_waveforms(BASE_DIR, NUM_PHASES)

    # Print which files were generated
    print("\n=== Acquisition complete ===")
    for i, p in enumerate(paths, start=1):
        status = p if p else "not acquired"
        print(f"CH{i:02d}: {status}")

    # Filter out empty strings for plotting
    valid_paths = [p for p in paths if p]   # skip empty strings
    if valid_paths:
        print(f"\n=== Plotting {len(valid_paths)} waveform(s) ===")
        output_plot = os.path.join(BASE_DIR, "waveforms_plot.png")
        plot_csv_files(valid_paths, output_path=output_plot, num_phases=NUM_PHASES)
    else:
        print("\nNo valid CSV files to plot.")


if __name__ == "__main__":
    main()