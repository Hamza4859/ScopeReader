import pyvisa

SCOPE_IP = "10.24.98.200"


def query_channel_measurement(
    scope,
    channel: int,
    measure_item: str = "MINimum",
) -> float | None:
    """Helper function to query a single channel using an open scope session."""
    try:
        scope.write("*CLS")
        scope.write(":MEASure:MODE ON")

        # Enable measurement on target channel
        scope.write(f":MEASure:CHANnel{channel}:{measure_item}:STATe ON")

        # Read value
        cmd = f":MEASure:CHANnel{channel}:{measure_item}:VALue?"
        response = scope.query(cmd).strip()

        raw_val = response.split()[-1] if " " in response else response

        # Return strictly a single float value
        return float(raw_val)

    except (pyvisa.VisaIOError, ValueError):
        return None


# --- Execution ---

channels = list(range(1, 17))
measure_item = "MINimum"

rm = pyvisa.ResourceManager("@py")

try:
    # Open the VISA connection ONCE for all 16 channels
    with rm.open_resource(f"TCPIP0::{SCOPE_IP}::INSTR", timeout=10000) as scope:
        for channel in channels:
            val = query_channel_measurement(
                scope=scope, channel=channel, measure_item=measure_item
            )

            val_str = f"{val:.4f}" if val is not None else "None"
            type_name = type(val).__name__ if val is not None else "NoneType"

            print(f"Channel {channel:02d} ({measure_item}): {val_str} (Type: {type_name})")

except pyvisa.VisaIOError as e:
    print(f"Failed to connect to oscilloscope at {SCOPE_IP}: {e}")