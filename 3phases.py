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

# Target ONLY Channels 10, 11, and 12
channels_to_read = [10, 11, 12]
MEASURE_ITEM = "MINimum"

# Map channel numbers to custom display labels
CHANNEL_LABELS = {
    10: "Frequency",
    11: "V1",
    12: "V2"
}

print("\n" + "=" * 60)
print("READING Values for Frequency, V1 and V2")
print("=" * 60)

# 3. Enable MINimum measurement item only on target channels
for ch in channels_to_read:
    ch_label = CHANNEL_LABELS.get(ch, f"CH{ch:02d}")
    try:
        scope.write(f":MEASure:CHANnel{ch}:{MEASURE_ITEM}:STATe ON")
    except pyvisa.VisaIOError as e:
        print(f"Failed to enable {MEASURE_ITEM} on {ch_label}: {e}")

# 4. Trigger Acquisition & Wait for Processing
try:
    print("Triggering single acquisition (:SSTart)...")
    scope.write(":SSTart")
    time.sleep(0.5)  # Wait for capture & processing

except pyvisa.VisaIOError as e:
    print(f"Acquisition control error: {e}")
    drain_errors()

# 5. Fetch & Display Clean Results for Frequency, V1, and V2
print("\n" + "-" * 40)
print("MINIMUM MEASUREMENTS RESULTS")
print("-" * 40)

valid_v_min = []

for ch in channels_to_read:
    ch_label = CHANNEL_LABELS.get(ch, f"CH{ch:02d}")
    cmd = f":MEASure:CHANnel{ch}:{MEASURE_ITEM}:VALue?"
    try:
        response = scope.query(cmd).strip()

        # Extract numerical value from header response
        raw_val = response.split()[-1] if " " in response else response

        # Filter out invalid / off channel signals
        if "NAN" in raw_val.upper() or "9.9E+37" in raw_val or "9.90000E+37" in raw_val:
            print(f"{ch_label} MINimum: N/A (Signal invalid or Channel OFF)")
        else:
            val_float = float(raw_val)
            valid_v_min.append((ch_label, val_float))
            print(f"{ch_label} MINimum: {val_float:.4f}  ({val_float:.6E})")

    except pyvisa.VisaIOError as e:
        print(f"{ch_label} MINimum: Query Failed ({e})")
        drain_errors()
    except ValueError:
        # Replaced line with hardcoded label structure:
        print(f"{ch_label} MINimum: Raw response -> '{response}'")


# 7. Clean up
scope.close()
print("\nConnection closed successfully.")