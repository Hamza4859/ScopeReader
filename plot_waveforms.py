#!/usr/bin/env python
"""
Plot waveforms from previously saved CSV files (produced by acquire_waveforms.py).

Usage:
    from plot_waveforms import plot_csv_files
    plot_csv_files(
        csv_paths=['./data/waveform_ch01.csv', './data/waveform_ch02.csv'],
        ip_address='10.24.98.206',
        part_number='ABC123',
        serial_number='SN001',
        frequency_hz=50.0,          # from getPhases.py
        output_path='./data',       # Directory path where plot.jpeg will be saved
        num_phases=3
    )

    # or run as script:
    python plot_waveforms.py --csvs ch01.csv ch02.csv ch03.csv ch04.csv \
        --ip 10.24.98.206 --pn ABC123 --sn SN001 --freq 50.0 --output ./data --phases 6
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Configuration defaults
LOGO_FILENAME = "logo.png"          # Image placed in the same directory as script
MAX_PLOT_POINTS = 50000             # Downsampling for plotting

# Fixed channel colours
CHANNEL_COLORS = {
    1: 'orange',
    2: 'green',
    3: '#2BB8FF',   # light blue
    4: '#FF2B8A',   # pink
    5: '#DC2BFF',   # purple
    6: '#FF2B2B',   # bright red
}


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


def plot_csv_files(csv_paths, ip_address, part_number, serial_number, frequency_hz,
                   output_path=None, title=None,
                   max_points=MAX_PLOT_POINTS, num_phases=None):

    valid_paths = [p for p in csv_paths if p and isinstance(p, str) and os.path.isfile(p)]
    if not valid_paths:
        print("No valid CSV files to plot.")
        return

    # Use the passed frequency
    freq_str = f"{frequency_hz:.2f} Hz" if frequency_hz is not None else "N/A"

    # Determine number of phases from filenames if not provided
    if num_phases is None:
        max_ch = 0
        for p in valid_paths:
            try:
                basename = os.path.basename(p)
                ch_str = basename.split('_')[1].split('.')[0]
                if ch_str.startswith('ch'):
                    ch = int(ch_str[2:])
                    if ch > max_ch:
                        max_ch = ch
            except:
                pass
        if max_ch <= 2:
            num_phases = 3
        elif max_ch <= 4:
            num_phases = 6
        else:
            num_phases = 9
    elif num_phases not in (3, 6, 9):
        raise ValueError("num_phases must be 3, 6, or 9")

    if num_phases == 3:
        groups = [(1, 2)]
    elif num_phases == 6:
        groups = [(1, 2), (3, 4)]
    else:  # 9
        groups = [(1, 2), (3, 4), (5, 6)]

    channel_data = {}
    for p in valid_paths:
        try:
            basename = os.path.basename(p)
            ch_str = basename.split('_')[1].split('.')[0]
            if ch_str.startswith('ch'):
                ch = int(ch_str[2:])
            else:
                continue
        except:
            continue
        try:
            data = np.genfromtxt(p, delimiter=",", skip_header=1)
            if data.ndim == 1:
                data = data.reshape(1, -1)
            time_sec = data[:, 1]
            voltage = data[:, 2]
            channel_data[ch] = (time_sec, voltage)
        except Exception as e:
            print(f"Error loading {p}: {e}")
            continue

    num_plots = len(groups)
    if num_plots == 0:
        print("No valid data to plot.")
        return

    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10.5, 2.3 * num_plots))
    fig.patch.set_facecolor('black')

    gs = fig.add_gridspec(num_plots, 2, width_ratios=[4, 1.1],
                          wspace=0.15, hspace=0.35)

    # Display PN, SN, and IP in top‑right corner
    info_text = f"PN: {part_number}\nSN: {serial_number}\nIP: {ip_address}"
    fig.text(0.98, 0.98, info_text,
             transform=fig.transFigure, ha='right', va='top',
             color='white', fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3",
                       facecolor='black', edgecolor='#444444', alpha=0.7))

    # Load logo (top‑left) if present
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_logo_path = os.path.join(script_dir, LOGO_FILENAME)
    if os.path.exists(full_logo_path):
        try:
            logo_img = plt.imread(full_logo_path)
            logo_ax = fig.add_axes([0.01, 0.85, 0.18, 0.14], anchor='NW', zorder=10)
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')
        except Exception as e:
            print(f"Could not load logo image: {e}")

    axes = []
    for idx, (ch1, ch2) in enumerate(groups):
        if idx == 0:
            ax = fig.add_subplot(gs[idx, 0])
        else:
            ax = fig.add_subplot(gs[idx, 0], sharex=axes[0])
        axes.append(ax)

        ax.set_facecolor('black')
        stats_text = []

        # Plot CH1
        if ch1 in channel_data:
            t, v = channel_data[ch1]
            t_plot, v_plot = peak_detect_downsample(t, v, max_points)
            color1 = CHANNEL_COLORS.get(ch1, 'white')
            ax.plot(t_plot, v_plot, label=f"CH{ch1:02d}", color=color1, linewidth=0.8)
            rms_v = float(np.sqrt(np.mean(v**2)))
            stats_text.append(f"CH{ch1:02d} RMS: {rms_v:.4f} V")
        else:
            stats_text.append(f"CH{ch1:02d}: N/A")

        # Plot CH2
        if ch2 in channel_data:
            t, v = channel_data[ch2]
            t_plot, v_plot = peak_detect_downsample(t, v, max_points)
            color2 = CHANNEL_COLORS.get(ch2, 'white')
            ax.plot(t_plot, v_plot, label=f"CH{ch2:02d}", color=color2, linewidth=0.8)
            rms_v = float(np.sqrt(np.mean(v**2)))
            stats_text.append(f"CH{ch2:02d} RMS: {rms_v:.4f} V")
        else:
            stats_text.append(f"CH{ch2:02d}: N/A")

        stats_text.append(f"Line Freq: {freq_str}")

        ax.set_ylabel("Voltage (V)", fontsize=9, fontweight="bold", color='white')
        ax.set_title(f"Group {idx+1}: CH{ch1:02d} & CH{ch2:02d}",
                     fontsize=10, loc='left', color='white')
        ax.grid(True, linestyle="--", alpha=0.3, color='gray')
        ax.tick_params(colors='white')

        # Side panel for stats
        ax_stats = fig.add_subplot(gs[idx, 1])
        ax_stats.set_facecolor('black')
        ax_stats.axis('off')
        info_box = "\n".join(stats_text)
        ax_stats.text(0.05, 0.5, info_box,
                      transform=ax_stats.transAxes, fontsize=8, color='white',
                      verticalalignment='center', horizontalalignment='left',
                      bbox=dict(boxstyle="round,pad=0.5",
                                facecolor="#111111", edgecolor='#444444', alpha=0.9))

    axes[-1].set_xlabel("Time Relative to Trigger (s)",
                        fontsize=10, fontweight="bold", color='white')

    if title:
        fig.suptitle(title, fontsize=14, color='white', y=0.98)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.84])

    if output_path:
        # Ensure the directory exists
        os.makedirs(output_path, exist_ok=True)
        # Construct path to always name the output as plot.jpeg
        file_save_path = os.path.join(output_path, "plot.jpeg")
        
        fig.savefig(file_save_path, dpi=200, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"Plot saved to {file_save_path}")

    print("Displaying plot... Close the window to complete script execution.")
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Plot waveforms from CSV files")
    parser.add_argument("--csvs", nargs="+", required=True,
                        help="List of CSV file paths (up to 6)")
    parser.add_argument("--ip", required=True, help="Oscilloscope IP address")
    parser.add_argument("--pn", required=True, help="Part Number")
    parser.add_argument("--sn", required=True, help="Serial Number")
    parser.add_argument("--freq", type=float, required=True,
                        help="Line frequency in Hz (from scope)")
    parser.add_argument("--output", help="Output directory path (optional)")
    parser.add_argument("--title", help="Figure title")
    parser.add_argument("--phases", type=int, choices=[3,6,9],
                        help="Number of phases (3, 6, or 9).")
    args = parser.parse_args()

    if len(args.csvs) > 6:
        print("Warning: More than 6 CSV files provided; only first 6 will be used.")
        args.csvs = args.csvs[:6]

    plot_csv_files(args.csvs, args.ip, args.pn, args.sn, args.freq,
                   args.output, args.title, num_phases=args.phases)