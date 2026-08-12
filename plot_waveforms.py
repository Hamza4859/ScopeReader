"""
Plot waveforms from previously saved CSV files (produced by acquire_waveforms.py).

Usage:
    from plot_waveforms import plot_csv_files
    plot_csv_files(['./data/waveform_ch01.csv', './data/waveform_ch02.csv'], output_path='plot.png')

    # or run as script:
    python plot_waveforms.py --csvs ch01.csv ch02.csv ch03.csv --output plot.png
"""

import os
import numpy as np
import matplotlib.pyplot as plt

MAX_PLOT_POINTS = 50000   # downsampling for plotting

def peak_detect_downsample(x, y, max_points):
    n = len(y)
    if n <= max_points:
        return x, y
    bin_size = int(np.ceil(n / (max_points / 2)))
    num_bins = int(np.ceil(n / bin_size))
    x_res, y_res = [], []
    for i in range(num_bins):
        start = i * bin_size
        end = min((i + 1) * bin_size, n)
        if start >= end:
            break
        bin_y = y[start:end]
        bin_x = x[start:end]
        min_idx = np.argmin(bin_y)
        max_idx = np.argmax(bin_y)
        if min_idx < max_idx:
            x_res.extend([bin_x[min_idx], bin_x[max_idx]])
            y_res.extend([bin_y[min_idx], bin_y[max_idx]])
        else:
            x_res.extend([bin_x[max_idx], bin_x[min_idx]])
            y_res.extend([bin_y[max_idx], bin_y[min_idx]])
    return np.array(x_res), np.array(y_res)

def plot_csv_files(csv_paths, output_path=None, title=None, max_points=MAX_PLOT_POINTS):
    """
    Plot up to 6 waveform CSV files in separate subplots.

    Parameters:
        csv_paths (list): List of up to 6 file paths (strings). Empty strings or None are ignored.
        output_path (str, optional): If provided, save the figure to this path instead of showing.
        title (str, optional): Overall figure title.
        max_points (int): Maximum number of points to plot (downsampled if needed).
    """
    # Filter out invalid paths: skip None, empty string, or non-existent files
    valid_paths = [p for p in csv_paths if p and isinstance(p, str) and os.path.isfile(p)]
    if not valid_paths:
        print("No valid CSV files to plot.")
        return

    num_plots = len(valid_paths)
    fig, axes = plt.subplots(num_plots, 1, figsize=(12, 2.5 * num_plots), sharex=True)
    if num_plots == 1:
        axes = [axes]

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    for idx, csv_file in enumerate(valid_paths):
        # Extract channel number from filename (assumes waveform_chXX.csv)
        try:
            basename = os.path.basename(csv_file)
            ch_str = basename.split('_')[1].split('.')[0]  # e.g., 'ch01'
            ch = int(ch_str[2:]) if ch_str.startswith('ch') else idx+1
        except:
            ch = idx+1

        try:
            data = np.genfromtxt(csv_file, delimiter=",", skip_header=1)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            time_sec = data[:, 1]
            voltage = data[:, 3]
        except Exception as e:
            print(f"  Error loading {csv_file}: {e}")
            continue

        if len(time_sec) == 0:
            print(f"  No data in {csv_file}")
            continue

        min_v, max_v = np.min(voltage), np.max(voltage)
        rms_v = float(np.sqrt(np.mean(voltage**2)))

        t_plot, v_plot = peak_detect_downsample(time_sec, voltage, max_points)

        ax = axes[idx]
        ax.plot(t_plot, v_plot, label=f"CH{ch:02d}", color=colors[idx % len(colors)], linewidth=0.8)
        ax.set_ylabel("Voltage (V)", fontsize=9, fontweight="bold")
        ax.set_title(f"Channel {ch:02d} Waveform ({len(time_sec):,} pts stored)", fontsize=10, loc="left")
        ax.grid(True, linestyle="--", alpha=0.5)

        ax.text(
            0.01, 0.05,
            f"Min: {min_v:.3f} V | Max: {max_v:.3f} V | RMS: {rms_v:.4f} V",
            transform=ax.transAxes,
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8),
        )

    axes[-1].set_xlabel("Time Relative to Trigger (s)", fontsize=10, fontweight="bold")
    if title:
        fig.suptitle(title, fontsize=14)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=200, bbox_inches="tight")
        print(f"Plot saved to {output_path}")
    else:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Plot waveforms from CSV files")
    parser.add_argument("--csvs", nargs="+", required=True, help="List of CSV file paths (up to 6)")
    parser.add_argument("--output", help="Output image file path (optional)")
    parser.add_argument("--title", help="Figure title")
    args = parser.parse_args()

    if len(args.csvs) > 6:
        print("Warning: More than 6 CSV files provided; only first 6 will be used.")
        args.csvs = args.csvs[:6]

    plot_csv_files(args.csvs, args.output, args.title)