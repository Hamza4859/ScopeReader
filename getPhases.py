import time
import pyvisa

SCOPE_IP = "10.24.98.200"


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


def get_frequency(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for Frequency (CH10) or None."""
    return _query_channel_measurement(
        channel=10, scope_ip=scope_ip, measure_item=measure_item
    )


def get_v1(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for V1 (CH11) or None."""
    return _query_channel_measurement(
        channel=11, scope_ip=scope_ip, measure_item=measure_item
    )


def get_v2(
    scope_ip: str = SCOPE_IP, measure_item: str = "MINimum"
) -> float | None:
    """Returns a single float for V2 (CH12) or None."""
    return _query_channel_measurement(
        channel=12, scope_ip=scope_ip, measure_item=measure_item
    )


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



"""""
# Target IP address (defaults to SCOPE_IP if omitted)
target_ip = SCOPE_IP

phases_3 = get_3phases_values(scope_ip=target_ip)
phases_6 = get_6phases_values(scope_ip=target_ip)
phases_9 = get_9phases_values(scope_ip=target_ip)

# Check types explicitly

print(f"3 Phases: {phases_3}")
print(f"6 Phases: {phases_6}")
print(f"9 Phases: {phases_9}")
"""