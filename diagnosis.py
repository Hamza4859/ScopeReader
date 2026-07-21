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

# Optional: Set monitor verbosity OFF if you only want raw numeric values,
# or set ON if you want units included. Here we explicitly disable verbose
# mode so we get clean values, but the parser below handles both!
# scope.write(":MONitor:VERBose OFF")

print("\n" + "=" * 60)
print("CONFIGURING & READING MONITOR DATA (:MONitor:ASENd?)")
print("=" * 60)

# 3. Control Acquisition (Stop -> Single Start -> Wait)
try:
    print("Triggering single acquisition (:SSTart)...")
    scope.write(":SSTart")
    time.sleep(0.5)  # Wait for acquisition/measurement update

except pyvisa.VisaIOError as e:
    print(f"Acquisition control error: {e}")
    drain_errors()

# 4. Fetch All Active Channels via Monitor Query
try:
    # Fetch all monitor data in a single ASCII string
    raw_response = scope.query(":MONitor:ASENd?").strip()
    
    # Split response by semicolon (0x3b) delimiter
    channel_entries = [entry.strip() for entry in raw_response.split(";") if entry.strip()]

    print(f"\nReceived {len(channel_entries)} channel entries:\n")

    for idx, entry in enumerate(channel_entries, start=1):
        # Parse entry depending on verbose mode (Label Value Unit vs Raw Value)
        tokens = entry.split()

        if not tokens:
            continue

        # Extract numeric candidate (usually the center token if verbose, or the only token)
        val_str = tokens[-2] if len(tokens) >= 3 else tokens[0]
        unit = tokens[-1] if len(tokens) >= 3 else ""

        # Handle overflow / invalid values
        if "NAN" in val_str.upper() or "9.9E+37" in val_str or "9.90000E+37" in val_str:
            formatted_val = "N/A (Signal invalid or Channel OFF)"
        else:
            try:
                val_float = float(val_str)
                formatted_val = f"{val_float:.4f} {unit}".strip()
            except ValueError:
                formatted_val = f"Raw string -> '{entry}'"

        print(f"Channel Entry {idx:02d}: {formatted_val}")

except pyvisa.VisaIOError as e:
    print(f"Failed to query :MONitor:ASENd? - {e}")
    drain_errors()

# 5. Clean up
scope.close()
print("\nConnection closed successfully.")