import time
import pyvisa

SCOPE_IP = "10.24.98.202"

# 1. Initialize Connection
rm = pyvisa.ResourceManager("@py")
scope = rm.open_resource(f"TCPIP0::{SCOPE_IP}::INSTR")
scope.timeout = 10000  # 10s timeout


def drain_errors():
    """Clear and print error queue for debugging."""
    print("\n--- Error Queue ---")
    while True:
        try:
            err = scope.query(":STATus:ERRor?").strip()
            if err.startswith("0,") or err == "0":
                break
            print("  Scope Error:", err)
        except pyvisa.VisaIOError:
            break


# 2. Setup Scope
scope.write("*CLS")
scope.write(":MEASure:MODE ON")  # Enable automated measurement system

# Define the measurement parameters to query
MEASURE_ITEMS = ["MINimum", "FREQuency"]
channels_to_read = range(1, 17)

print("\n" + "=" * 70)
print("ENABLING MEASUREMENTS: MINIMUM VOLTAGE & FREQUENCY FOR CH1-CH16")
print("=" * 70)

# 3. Enable MINimum and FREQuency measurement items on each channel
for ch in channels_to_read:
    for item in MEASURE_ITEMS:
        try:
            scope.write(f":MEASure:CHANnel{ch}:{item}:STATe ON")
        except pyvisa.VisaIOError as e:
            print(f"Failed to enable {item} on CH{ch}: {e}")

# 4. Trigger Acquisition & Wait for Processing
try:
    print("\nTriggering single acquisition (:SSTart)...")
    scope.write(":SSTart")
    time.sleep(0.5)  # Wait for single-shot capture & measurement engine

except pyvisa.VisaIOError as e:
    print(f"Acquisition control error: {e}")
    drain_errors()

# 5. Fetch Measurements for Each Channel
print("\n" + "=" * 70)
print("FETCHING MEASUREMENT RESULTS")
print("=" * 70)

# Track channel data and overall minimums
results = {ch: {} for ch in channels_to_read}
valid_v_min = []
valid_freq = []

for ch in channels_to_read:
    print(f"\n--- Channel {ch:02d} ---")
    
    for item in MEASURE_ITEMS:
        cmd = f":MEASure:CHANnel{ch}:{item}:VALue?"
        try:
            response = scope.query(cmd).strip()

            # Handle header-prefixed response (e.g. ":MEASURE:CHANNEL1:MINIMUM:VALUE -1.23E+00")
            raw_val = response.split()[-1] if " " in response else response

            # Check for invalid signal, uncalculated range, or NAN
            if "NAN" in raw_val.upper() or "9.9E+37" in raw_val or "9.90000E+37" in raw_val:
                results[ch][item] = None
                print(f"  {item:10s}: N/A (Signal invalid or Channel OFF)")
            else:
                val_float = float(raw_val)
                results[ch][item] = val_float

                # Format with units
                unit = "V" if item == "MINimum" else "Hz"
                print(f"  {item:10s}: {val_float:.4f} {unit} ({val_float:.6E})")

                # Store valid numbers for overall minimum comparison
                if item == "MINimum":
                    valid_v_min.append((ch, val_float))
                elif item == "FREQuency":
                    valid_freq.append((ch, val_float))

        except pyvisa.VisaIOError as e:
            print(f"  {item:10s}: Query Failed ({e})")
            drain_errors()
        except ValueError:
            print(f"  {item:10s}: Raw response -> '{response}'")

# 6. Display Summary of Lowest Values
print("\n" + "=" * 70)
print("SUMMARY OF MINIMUM VALUES")
print("=" * 70)

if valid_v_min:
    min_ch_v, min_val_v = min(valid_v_min, key=lambda x: x[1])
    print(f"Lowest Voltage (MINimum) : CH{min_ch_v:02d} = {min_val_v:.4f} V ({min_val_v:.6E})")
else:
    print("Lowest Voltage (MINimum) : No valid channel measurements found")

if valid_freq:
    min_ch_f, min_val_f = min(valid_freq, key=lambda x: x[1])
    print(f"Lowest Frequency         : CH{min_ch_f:02d} = {min_val_f:.4f} Hz ({min_val_f:.6E})")
else:
    print("Lowest Frequency         : No valid channel measurements found")

# 7. Clean up
scope.close()
print("\nConnection closed successfully.")