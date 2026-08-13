"""
Plot waveforms from previously saved CSV files (produced by acquire_waveforms.py).

Usage:
    from plot_waveforms import plot_csv_files
    plot_csv_files(['./data/waveform_ch01.csv', './data/waveform_ch02.csv'],
                   output_path='plot.png', num_phases=3)

    # or run as script:
    python plot_waveforms.py --csvs ch01.csv ch02.csv ch03.csv ch04.csv --output plot.png --phases 6
"""

import os
import numpy as np
import matplotlib.pyplot as plt

MAX_PLOT_POINTS = 50000   # downsampling for plotting

# Fixed channel colors – updated to your specifications
CHANNEL_COLORS = {
    1: 'orange',
    2: 'green',
    3: '#DC2BFF',   # purple
    4: '#FF2B2B',   # bright red
    5: '#2BB8FF',   # light blue
    6: '#FF2B8A',   # pink
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

def plot_csv_files(csv_paths, output_path=None, title=None, max_points=MAX_PLOT_POINTS, num_phases=None):
    """
    Plot up to 6 waveform CSV files in grouped subplots (two channels per plot).
    Groups are defined by phases: (1,2), (3,4), (5,6).
    Channel colors: CH1=Orange, CH2=Green, CH3=#B78AFF, CH4=#FF2B2B, CH5=#8A8AFF, CH6=#FF2B8A.
    """
    # Filter out invalid paths
    valid_paths = [p for p in csv_paths if p and isinstance(p, str) and os.path.isfile(p)]
    if not valid_paths:
        print("No valid CSV files to plot.")
        return

    # Determine the number of phases from filenames if not provided
    if num_phases is None:
        max_ch = 0
        for p in valid_paths:
            try:
                basename = os.path.basename(p)
                ch_str = basename.split('_')[1].split('.')[0]  # e.g., 'ch01'
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

    # Define channel pairs per phase
    if num_phases == 3:
        groups = [(1, 2)]
    elif num_phases == 6:
        groups = [(1, 2), (3, 4)]
    else:  # 9
        groups = [(1, 2), (3, 4), (5, 6)]

    # Build a mapping from channel number to its data (time, voltage)
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
            voltage = data[:, 3]
            channel_data[ch] = (time_sec, voltage)
        except Exception as e:
            print(f"  Error loading {p}: {e}")
            continue

    # Determine number of subplots (one per group)
    num_plots = len(groups)
    if num_plots == 0:
        print("No valid data to plot.")
        return

    # Set dark style and create figure with REDUCED SIZE
    plt.style.use('dark_background')
    fig, axes = plt.subplots(num_plots, 1, figsize=(8, 2.0 * num_plots), sharex=True)   # <-- reduced from 12x2.5
    if num_plots == 1:
        axes = [axes]

    fig.patch.set_facecolor('black')
    for ax in axes:
        ax.set_facecolor('black')

    # Plot each group
    for idx, (ch1, ch2) in enumerate(groups):
        ax = axes[idx]
        # Plot ch1 if available
        if ch1 in channel_data:
            t, v = channel_data[ch1]
            t_plot, v_plot = peak_detect_downsample(t, v, max_points)
            color1 = CHANNEL_COLORS.get(ch1, 'white')
            ax.plot(t_plot, v_plot, label=f"CH{ch1:02d}", color=color1, linewidth=0.8)
            # Compute stats for annotation
            min_v, max_v = np.min(v), np.max(v)
            rms_v = float(np.sqrt(np.mean(v**2)))
            ax.text(0.01, 0.95, f"CH{ch1:02d}: Min={min_v:.3f}V Max={max_v:.3f}V RMS={rms_v:.4f}V",
                    transform=ax.transAxes, fontsize=8, color='white',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor='white', alpha=0.7),
                    verticalalignment='top')
        else:
            ax.text(0.5, 0.5, f"CH{ch1:02d} not available", ha='center', va='center',
                    transform=ax.transAxes, color='gray', fontsize=10)

        # Plot ch2 if available
        if ch2 in channel_data:
            t, v = channel_data[ch2]
            t_plot, v_plot = peak_detect_downsample(t, v, max_points)
            color2 = CHANNEL_COLORS.get(ch2, 'white')
            ax.plot(t_plot, v_plot, label=f"CH{ch2:02d}", color=color2, linewidth=0.8)
            min_v, max_v = np.min(v), np.max(v)
            rms_v = float(np.sqrt(np.mean(v**2)))
            ax.text(0.01, 0.85, f"CH{ch2:02d}: Min={min_v:.3f}V Max={max_v:.3f}V RMS={rms_v:.4f}V",
                    transform=ax.transAxes, fontsize=8, color='white',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="black", edgecolor='white', alpha=0.7),
                    verticalalignment='top')
        else:
            ax.text(0.5, 0.4, f"CH{ch2:02d} not available", ha='center', va='center',
                    transform=ax.transAxes, color='gray', fontsize=10)

        ax.set_ylabel("Voltage (V)", fontsize=9, fontweight="bold", color='white')
        ax.set_title(f"Group {idx+1}: CH{ch1:02d} & CH{ch2:02d}", fontsize=10, loc='left', color='white')
        ax.grid(True, linestyle="--", alpha=0.3, color='gray')
        ax.tick_params(colors='white')

    axes[-1].set_xlabel("Time Relative to Trigger (s)", fontsize=10, fontweight="bold", color='white')

    if title:
        fig.suptitle(title, fontsize=14, color='white')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
        print(f"Plot saved to {output_path}")

    print("Displaying plot... Close the window to complete script execution.")
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Plot waveforms from CSV files")
    parser.add_argument("--csvs", nargs="+", required=True, help="List of CSV file paths (up to 6)")
    parser.add_argument("--output", help="Output image file path (optional)")
    parser.add_argument("--title", help="Figure title")
    parser.add_argument("--phases", type=int, choices=[3,6,9], help="Number of phases (3, 6, or 9). If omitted, inferred from filenames.")
    args = parser.parse_args()

    if len(args.csvs) > 6:
        print("Warning: More than 6 CSV files provided; only first 6 will be used.")
        args.csvs = args.csvs[:6]

    plot_csv_files(args.csvs, args.output, args.title, num_phases=args.phases)