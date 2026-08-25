#!/usr/bin/env python
"""
Test script for the DL850E acquisition and plotting modules.
It imports the two helper modules and runs a complete test.
Simply set NUM_PHASES to 3, 6, or 9 and run.
"""

import os
import sys
import shutil

sys.dont_write_bytecode = True

# Import the main functions from the helper modules
from acquire_waveforms import acquire_waveforms
from plot_waveforms import plot_csv_files
from getPhases import get_phases_values   # <-- import from getPhases.py

# ==================== CONFIGURATION ====================
BASE_DIR = r"C:\Users\hamza.rtelbennani\Desktop\Scope Reader\ScopeReader\csv waves"
NUM_PHASES = 6  # 3, 6, or 9
SCOPE_IP = "10.24.98.206"
PART_NUMBER = "ABC123"      # Replace with actual
SERIAL_NUMBER = "SN001"     # Replace with actual
# ======================================================

def clean_folder(directory):
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
    if NUM_PHASES not in (3, 6, 9):
        print(f"Error: NUM_PHASES must be 3, 6, or 9; got {NUM_PHASES}")
        sys.exit(1)

    # Clean folder
    print(f"Cleaning folder: {BASE_DIR}")
    clean_folder(BASE_DIR)

    # Acquire waveforms
    print(f"=== Starting acquisition for {NUM_PHASES} phases ===")
    paths = acquire_waveforms(BASE_DIR, NUM_PHASES)

    print("\n=== Acquisition complete ===")
    for i, p in enumerate(paths, start=1):
        status = p if p else "not acquired"
        print(f"CH{i:02d}: {status}")

    # Get frequency from scope via getPhases
    phase_count_str = str(NUM_PHASES)
    # get_phases_values returns list of 7 values; first is frequency (channel 10)
    values = get_phases_values(phase_count_str, scope_ip=SCOPE_IP)
    frequency_hz = values[0] if values and values[0] != -9999.0 else None
    if frequency_hz is None:
        print("Warning: Could not retrieve frequency, setting to 0.0")
        frequency_hz = 0.0

    valid_paths = [p for p in paths if p]
    if valid_paths:
        print(f"\n=== Plotting {len(valid_paths)} waveform(s) ===")
        plot_csv_files(
            csv_paths=valid_paths,
            ip_address=SCOPE_IP,
            part_number=PART_NUMBER,
            serial_number=SERIAL_NUMBER,
            frequency_hz=frequency_hz,
            output_path=BASE_DIR,
            num_phases=NUM_PHASES
        )
    else:
        print("\nNo valid CSV files to plot.")

if __name__ == "__main__":
    main()