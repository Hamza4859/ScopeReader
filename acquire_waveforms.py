import os
import numpy as np
import pyvisa

# ========== CONFIGURATION (adjust as needed) ==========
SCOPE_IP = "10.24.98.206"
TIME_WINDOW_START = None          # None = entire record
TIME_WINDOW_END   = None
MAX_TRANSFER_SAMPLES = None
DOWNSAMPLE_CSV = False
CSV_MAX_POINTS = 50000
DATA_FORMAT = "WORD"
BYTE_ORDER = "BIG"                # or "LITTLE"
# =====================================================

def drain_errors(scope):
    errors = []
    while True:
        try:
            err = scope.query(":STATus:ERRor?").strip()
            if err.startswith("0,") or err == "0" or "No error" in err:
                break
            errors.append(err)
        except pyvisa.VisaIOError:
            break
    return errors

def calculate_physical_values(
    raw_data,
    range_val,
    offset_val,
    data_format="WORD",
    module_type="VOLTAGE",
):
    fmt = data_format.upper()
    mod = module_type.upper()
    division = 93.75 if fmt == "BYTE" else 24000.0
    if mod in ["VOLTAGE", "ACCELERATION", "FREQUENCY"]:
        return (range_val * raw_data * 10.0) / division + offset_val
    elif mod == "STRAIN":
        strain_div = 187.5 if fmt == "BYTE" else 48000.0
        return (range_val * raw_data * 10.0) / strain_div + offset_val
    elif mod == "TEMPERATURE":
        temp_div = 25.6 if fmt == "BYTE" else 0.1
        return raw_data * temp_div
    elif mod in ["CAN", "SENT", "LIN"]:
        return (range_val * raw_data) + offset_val
    else:
        return (range_val * raw_data * 10.0) / division + offset_val

def acquire_waveforms(directory, num_phases, scope_ip=SCOPE_IP):

    # Validate num_phases
    valid_phases = {3: [1,2], 6: [1,2,3,4], 9: [1,2,3,4,5,6]}
    if num_phases not in valid_phases:
        raise ValueError(f"num_phases must be 3, 6, or 9; got {num_phases}")
    channels_to_read = valid_phases[num_phases]

    # Create directory if it does not exist
    os.makedirs(directory, exist_ok=True)

    # Initialize VISA connection
    rm = pyvisa.ResourceManager("@py")
    scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR")
    scope.timeout = 20000

    # Configure scope
    try:
        scope.write(":ACQuire:SRATe MAX")  # may not be supported
    except Exception:
        pass

    scope.write(f":WAVeform:FORMat {DATA_FORMAT}")
    byte_order_str = "MSBFirst" if BYTE_ORDER == "BIG" else "LSBFirst"
    scope.write(f":WAVeform:BYTeorder {byte_order_str}")

    # We will collect paths for channels 1..6 - use empty string for missing
    result_paths = [""] * 6   # index 0 -> ch1, ..., 5 -> ch6

    for ch in channels_to_read:
        print(f"\n--- Processing Channel {ch:02d} ---")
        scope.write(f":WAVeform:TRACe {ch}")

        errs = drain_errors(scope)
        if any("241" in e or "Hardware missing" in e for e in errs):
            print(f"  CH{ch:02d}: No hardware module installed. Skipping.")
            continue

        try:
            range_val = float(scope.query(":WAVeform:RANGe?").strip().split()[-1])
            offset_val = float(scope.query(":WAVeform:OFFSet?").strip().split()[-1])
        except (pyvisa.VisaIOError, ValueError):
            drain_errors(scope)
            print(f"  CH{ch:02d}: Disabled or unpopulated channel.")
            continue

        try:
            x_increment = float(scope.query(":WAVeform:XINCrement?").strip().split()[-1])
        except Exception:
            x_increment = 1.0

        try:
            x_offset = float(scope.query(":WAVeform:XOFFset?").strip().split()[-1])
        except Exception:
            x_offset = 0.0

        try:
            length_resp = scope.query(":WAVeform:LENGth?").strip()
            total_length = int(length_resp.split()[-1])
        except Exception:
            total_length = 0

        if total_length == 0:
            print(f"  CH{ch:02d}: No record data found in memory.")
            continue

        sample_rate_hz = 1.0 / x_increment if x_increment > 0 else 0.0
        sr_str = f"{sample_rate_hz/1e6:.3f} MS/s" if sample_rate_hz >= 1e6 else \
                 f"{sample_rate_hz/1e3:.3f} kS/s" if sample_rate_hz >= 1e3 else \
                 f"{sample_rate_hz:.2f} S/s"
        print(f"  Sampling Rate: {sr_str} (x_inc: {x_increment:.6e} s)")
        print(f"  x_offset: {x_offset:.6f} s, total_length: {total_length:,} pts")
        print(f"  Record spans from {x_offset:.6f} s to {x_offset + (total_length-1)*x_increment:.6f} s")

        # Determine transfer bounds
        start_point = 0
        end_point = total_length - 1

        if TIME_WINDOW_START is not None and TIME_WINDOW_END is not None:
            start_idx = int(round((TIME_WINDOW_START - x_offset) / x_increment))
            end_idx   = int(round((TIME_WINDOW_END   - x_offset) / x_increment))
            start_idx = max(0, min(start_idx, total_length - 1))
            end_idx   = max(0, min(end_idx,   total_length - 1))
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
            if end_idx - start_idx < 10:
                print(f"  WARNING: Time window yields only {end_idx - start_idx + 1} samples!")
                print(f"  Using first {min(1000, total_length)} samples instead.")
                start_idx = 0
                end_idx = min(1000, total_length) - 1
            start_point = start_idx
            end_point = end_idx
            print(f"  Time window: {TIME_WINDOW_START:.6f} s to {TIME_WINDOW_END:.6f} s  ->  samples {start_point} to {end_point} (of {total_length:,})")
        elif MAX_TRANSFER_SAMPLES is not None and MAX_TRANSFER_SAMPLES < total_length:
            start_point = 0
            end_point = MAX_TRANSFER_SAMPLES - 1
            print(f"  Fetching only first {MAX_TRANSFER_SAMPLES:,} samples.")
        else:
            print(f"  Fetching all {total_length:,} samples.")

        scope.write(f":WAVeform:STARt {start_point}")
        scope.write(f":WAVeform:END {end_point}")

        try:
            datatype_map = {"BYTE": "b", "WORD": "h"}
            dtype = datatype_map.get(DATA_FORMAT, "h")
            is_big_endian = BYTE_ORDER == "BIG"

            raw_data = scope.query_binary_values(
                ":WAVeform:SEND?",
                datatype=dtype,
                is_big_endian=is_big_endian,
                container=np.ndarray,
            )

            samples_retrieved = len(raw_data)
            print(f"  Retrieved {samples_retrieved:,} raw samples")

            if samples_retrieved == 0:
                print(f"  CH{ch:02d}: No data retrieved.")
                continue

            # Scale to physical values
            scaled_data = calculate_physical_values(
                raw_data=raw_data,
                range_val=range_val,
                offset_val=offset_val,
                data_format=DATA_FORMAT,
                module_type="VOLTAGE",
            )

            # RMS
            rms_val = float(np.sqrt(np.mean(scaled_data**2)))

            # Time vector
            indices = np.arange(samples_retrieved)
            time_vector = x_offset + (start_point + indices) * x_increment

            # Downsample CSV if requested
            if DOWNSAMPLE_CSV and samples_retrieved > CSV_MAX_POINTS:
                step = int(np.ceil(samples_retrieved / CSV_MAX_POINTS))
                indices = indices[::step]
                time_vector = time_vector[::step]
                raw_data = raw_data[::step]
                scaled_data_csv = scaled_data[::step]
                print(f"  Decimating CSV to ~{len(scaled_data_csv):,} samples (1 in {step})")
            else:
                scaled_data_csv = scaled_data
                print(f"  Exporting CSV at full rate ({len(scaled_data):,} samples)")

            # Save CSV
            csv_filename = f"waveform_ch{ch:02d}.csv"
            csv_path = os.path.join(directory, csv_filename)
            export_matrix = np.column_stack((indices, time_vector, raw_data, scaled_data_csv))
            header_str = "Sample_Index,Time_Relative_Trigger_s,Raw_Count,Voltage_V"
            np.savetxt(
                csv_path,
                export_matrix,
                delimiter=",",
                header=header_str,
                comments="",
                fmt=["%d", "%.8e", "%d", "%.6f"],
            )

            # Store path (string) in result list
            result_paths[ch-1] = csv_path

            print(f"  --> CH{ch:02d} Summary: Min = {np.min(scaled_data):.3f} V | "
                  f"Max = {np.max(scaled_data):.3f} V | RMS = {rms_val:.4f} V")

        except pyvisa.VisaIOError as e:
            print(f"  Failed on CH{ch:02d}: {e}")
            scope.clear()
            drain_errors(scope)

    scope.close()
    return result_paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Acquire waveforms from DL850E")
    parser.add_argument("--dir", required=True, help="Directory to save CSV files")
    parser.add_argument("--phases", type=int, required=True, choices=[3,6,9],
                        help="Number of phases (3->ch1-2, 6->ch1-4, 9->ch1-6)")
    parser.add_argument("--ip", default=SCOPE_IP, help="Scope IP address")
    args = parser.parse_args()

    paths = acquire_waveforms(args.dir, args.phases, args.ip)
    print("\nAcquisition complete. Generated CSVs:")
    for i, p in enumerate(paths, start=1):
        status = p if p else "not acquired"
        print(f"  CH{i:02d}: {status}")