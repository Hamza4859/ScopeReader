import time
import pyvisa


def _query_channel_measurement(
    channel: int,
    measure_item: str = "MINimum",
    scope_ip: str = "10.24.98.202",
) -> float | None:
    """Helper function to query a single channel and return a single float or None."""
    rm = pyvisa.ResourceManager("@py")
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write("*CLS")
        scope.write(":MEASure:MODE ON")

        # Enable measurement on the target channel
        scope.write(f":MEASure:CHANnel{channel}:{measure_item}:STATe ON")

        # Read value
        cmd = f":MEASure:CHANnel{channel}:{measure_item}:VALue?"
        response = scope.query(cmd).strip()

        raw_val = response.split()[-1] if " " in response else response

        scope.close()


        # Return strictly a single float value
        val = float(raw_val)
        return val

    except (pyvisa.VisaIOError, ValueError):
        return None


# --- The 3 Dedicated Helper Methods ---


def get_frequency(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for Frequency (CH10) or None."""
    return _query_channel_measurement(
        channel=10, measure_item=measure_item, scope_ip=scope_ip
    )


def get_v1(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for V1 (CH11) or None."""
    return _query_channel_measurement(
        channel=11, measure_item=measure_item, scope_ip=scope_ip
    )


def get_v2(
    scope_ip: str = "10.24.98.202", measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for V2 (CH12) or None."""
    return _query_channel_measurement(
        channel=12, measure_item=measure_item, scope_ip=scope_ip
    )


# --- Example Usage ---
freq = get_frequency()
v1 = get_v1()
v2 = get_v2()

# Check types explicitly
print(f"Frequency: {freq} (Type: {type(freq).__name__})")
print(f"V1: {v1} (Type: {type(v1).__name__})")
print(f"V2: {v2} (Type: {type(v2).__name__})")