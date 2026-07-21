import time
import pyvisa


def get_target_measurements(
    scope_ip="10.24.98.202", measure_item="MINimum"
) -> dict[str, float | None]:
    """Connects to the scope, triggers a single acquisition, and returns

    a dict mapping ['Frequency', 'V1', 'V2'] to their numerical values (or None
    if invalid).
    """
    channel_map = {10: "Frequency", 11: "V1", 12: "V2"}
    results = {}

    rm = pyvisa.ResourceManager("@py")
    try:
        scope = rm.open_resource(
            f"TCPIP0::{scope_ip}::INSTR", timeout=10000
        )  # 10s timeout
        scope.write("*CLS")
        scope.write(":MEASure:MODE ON")

        # 1. Enable specified measurement item on targets
        for ch in channel_map:
            scope.write(f":MEASure:CHANnel{ch}:{measure_item}:STATe ON")

        # 2. Single acquisition trigger
        scope.write(":SSTart")
        time.sleep(0.5)

        # 3. Read values
        for ch, label in channel_map.items():
            cmd = f":MEASure:CHANnel{ch}:{measure_item}:VALue?"
            response = scope.query(cmd).strip()

            raw_val = response.split()[-1] if " " in response else response

            # Filter out invalid/overflow responses (e.g., 9.9E+37 or NaN)
            if (
                "NAN" in raw_val.upper()
                or "9.9E+37" in raw_val
                or "9.90000E+37" in raw_val
            ):
                results[label] = None
            else:
                try:
                    results[label] = float(raw_val)
                except ValueError:
                    results[label] = None

        scope.close()
        return results

    except pyvisa.VisaIOError:
        return {label: None for label in channel_map.values()}


# Usage example:
data = get_target_measurements()
print(data)
# Output: {'Frequency': 0.0012, 'V1': -1.245, 'V2': 3.312}