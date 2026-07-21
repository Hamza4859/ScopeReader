import time
import pyvisa


def _query_channel_measurement(
    channel: int,
    measure_item: str = "MINimum",
    scope_ip: str = "10.24.98.202",
) -> float | None:
    """Helper function to execute the PyVISA query for a single channel."""
    rm = pyvisa.ResourceManager("@py")
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write("*CLS")
        scope.write(":MEASure:MODE ON")

        # Enable measurement on the target channel
        scope.write(f":MEASure:CHANnel{channel}:{measure_item}:STATe ON")

        # Trigger single acquisition
        scope.write(":SSTart")
        time.sleep(0.5)

        # Read value
        cmd = f":MEASure:CHANnel{channel}:{measure_item}:VALue?"
        response = scope.query(cmd).strip()

        raw_val = response.split()[-1] if " " in response else response

        scope.close()

        # Check for invalid / off-channel responses
        if (
            "NAN" in raw_val.upper()
            or "9.9E+37" in raw_val
            or "9.90000E+37" in raw_val
        ):
            return None

        return float(raw_val)

    except (pyvisa.VisaIOError, ValueError):
        return None


# --- The 3 Dedicated Helper Methods ---


def get_frequency(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns the measurement value for Frequency (Channel 10)."""
    return _query_channel_measurement(
        channel=10, measure_item=measure_item, scope_ip=scope_ip
    )


def get_v1(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns the measurement value for V1 (Channel 11)."""
    return _query_channel_measurement(
        channel=11, measure_item=measure_item, scope_ip=scope_ip
    )


def get_v2(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns the measurement value for V2 (Channel 12)."""
    return _query_channel_measurement(
        channel=12, measure_item=measure_item, scope_ip=scope_ip
    )


# --- Usage Example ---
freq = get_frequency()
v1 = get_v1()
v2 = get_v2()

print(f"Frequency: {freq}")
print(f"V1: {v1}")
print(f"V2: {v2}")