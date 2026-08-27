import time
import pyvisa
 
SCOPE_IP = "10.24.98.206"
 
 
def _query_channel_measurement(
    scope: pyvisa.Resource,
    channel: int,
    measure_item: str = "MINimum",
) -> float | None:
    """Helper function to query a single channel on an open scope connection."""
    try:
        scope.write("*CLS")
        scope.write(":MEASure:MODE ON")
 
        # Enable measurement on target channel
        scope.write(f":MEASure:CHANnel{channel}:{measure_item}:STATe ON")
 
        # Read value
        cmd = f":MEASure:CHANnel{channel}:{measure_item}:VALue?"
        response = scope.query(cmd).strip()
 
        raw_val = response.split()[-1] if " " in response else response
        return float(raw_val)
 
    except (pyvisa.VisaIOError, ValueError):
        return None
 
 
def start_scope(scope_ip: str = SCOPE_IP) -> None:
    # Default empty argument initializes the native NI-VISA C-library
    rm = pyvisa.ResourceManager()
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write(":SSTart")
        scope.close()
    except pyvisa.VisaIOError:
        pass
 
 
def stop_scope(scope_ip: str = SCOPE_IP) -> None:
    rm = pyvisa.ResourceManager()
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
        scope.write(":STOP")
        scope.close()
    except pyvisa.VisaIOError:
        pass
 
 
def get_3phases_values(
    scope: pyvisa.Resource, measure_item: str = "MINimum"
) -> list[float | None]:
    channels = [10, 11, 12]
    return [_query_channel_measurement(scope, ch, measure_item) for ch in channels]
 
 
def get_6phases_values(
    scope: pyvisa.Resource, measure_item: str = "MINimum"
) -> list[float | None]:
    channels = [10, 11, 12, 13, 14]
    return [_query_channel_measurement(scope, ch, measure_item) for ch in channels]
 
 
def get_9phases_values(
    scope: pyvisa.Resource, measure_item: str = "MINimum"
) -> list[float | None]:
    channels = [10, 11, 12, 13, 14, 15, 16]
    return [_query_channel_measurement(scope, ch, measure_item) for ch in channels]
 
 
def get_phases_values(
    phase_count: str,
    scope_ip: str = SCOPE_IP,
    measure_item: str = "MINimum",
) -> list[float | None]:
    """Dynamically fetches phase measurements using NI-VISA (max 7 channels: 10 to 16)
 
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
 
    # Initialize NI-VISA Resource Manager
    rm = pyvisa.ResourceManager()
 
    try:
        scope = rm.open_resource(f"TCPIP0::{scope_ip}::INSTR", timeout=10000)
       
        # 1. Fetch raw measurements using open connection
        raw_values = phase_map[phase_count](scope, measure_item=measure_item)
       
        scope.close()
    except pyvisa.VisaIOError:
        raw_values = []
 
    # 2. Replace any failed queries (None) with -9999
    cleaned_values = [
        val if val is not None else -9999.0 for val in raw_values
    ]
 
    # 3. Pad to length 7 with -9999
    return (cleaned_values + [-9999.0] * 7)[:7]