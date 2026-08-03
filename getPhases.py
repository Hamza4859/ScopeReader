import time
import pyvisa

SCOPE_IP = "10.24.98.206"


def _query_channel_measurement(
    channel: int,
    scope_ip: str = SCOPE_IP,
    measure_item: str = "MINimum",
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


def start_scope(scope_ip: str = SCOPE_IP) -> None:
    rm = pyvisa.ResourceManager("@py")
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write(":SSTart")
        scope.close()
    except pyvisa.VisaIOError:
        pass


def stop_scope(scope_ip: str = SCOPE_IP) -> None:
    rm = pyvisa.ResourceManager("@py")
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write(":STOP")
        scope.close()
    except pyvisa.VisaIOError:
        pass


# --- The Dedicated Helper Methods ---


def get_3phases_values(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> list[float | None]:
    """Queries hardcoded channels 10, 11, 12."""
    channels = [10, 11, 12]
    return [
        _query_channel_measurement(
            channel=ch, scope_ip=scope_ip, measure_item=measure_item
        )
        for ch in channels
    ]


def get_6phases_values(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> list[float | None]:
    """Queries hardcoded channels 10, 11, 12, 13, 14."""
    channels = [10, 11, 12, 13, 14]
    return [
        _query_channel_measurement(
            channel=ch, scope_ip=scope_ip, measure_item=measure_item
        )
        for ch in channels
    ]


def get_9phases_values(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> list[float | None]:
    """Queries hardcoded channels 10, 11, 12, 13, 14, 15, 16."""
    channels = [10, 11, 12, 13, 14, 15, 16]
    return [
        _query_channel_measurement(
            channel=ch, scope_ip=scope_ip, measure_item=measure_item
        )
        for ch in channels
    ]

def get_phases_values(
    phase_count: str,
    scope_ip: str = SCOPE_IP,
    measure_item: str = "MINimum",
) -> list[float | None]:
    """Dynamically fetches phase measurements (max 7 channels: 10 to 16)

    and ensures the returned list is always padded to length 7 with -9999.
    """
    phase_map = {
        "3": get_3phases_values,
        "6": get_6phases_values,
        "9": get_9phases_values,
    }

    if phase_count not in phase_map:
        raise ValueError(
            f"Invalid phase_count '{phase_count}'. Expected '3', '6', or '9'."
        )

    # 1. Fetch raw measurements
    raw_values = phase_map[phase_count](
        scope_ip=scope_ip, measure_item=measure_item
    )

    # 2. Replace any failed queries (None) with -9999
    cleaned_values = [
        val if val is not None else -9999.0 for val in raw_values
    ]

    # 3. Pad to length 7 with -9999 for non-queried channels (or slice to 7 max)
    padded_values = (cleaned_values + [-9999.0] * 7)[:7]

    return padded_values



target_ip = SCOPE_IP

start_scope(target_ip)


# Target IP address (defaults to SCOPE_IP if omitted)


# Testing all 3 dynamic phase usages
phases_3 = get_phases_values("3", scope_ip=target_ip)
phases_6 = get_phases_values("6", scope_ip=target_ip)
phases_9 = get_phases_values("9", scope_ip=target_ip)

print(f"3 Phases (len={len(phases_3)}): {phases_3}")
print(f"6 Phases (len={len(phases_6)}): {phases_6}")
print(f"9 Phases (len={len(phases_9)}): {phases_9}")
