import pyvisa

SCOPE_IP = "10.24.98.206"


def recall_setup_visa(ip_address: str, phases: int) -> None:
    """Recalls setup data on a Yokogawa DL850E based on the specified phase configuration.

    :param ip_address: IP address of the oscilloscope
    :param phases: Phase count (3, 6, or 9) mapped to internal setup numbers (16, 7, or 8)
    """
    # Mapping phase counts to setup numbers x (1 to 16)
    phase_map = {
        3: 16,
        6: 7,
        9: 8,
    }

    if phases not in phase_map:
        raise ValueError(
            f"Unsupported phases value: {phases}. Allowed values are 3, 6, or 9."
        )

    setup_number = phase_map[phases]

    rm = pyvisa.ResourceManager()
    resource_str = f"TCPIP0::{ip_address}::inst0::INSTR"

    try:
        with rm.open_resource(resource_str) as inst:
            inst.timeout = 5000  # 5 seconds
            inst.write_termination = "\n"

            command = f":RECALL:SETUP{setup_number}:EXECUTE"
            inst.write(command)

            print(
                f"Successfully sent '{command}' (phases={phases}) to {ip_address}"
            )

    except pyvisa.VisaIOError as e:
        print(f"VISA Error communicating with DL850E at {ip_address}: {e}")  # Example: recall setup for 6 phases