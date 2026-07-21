import sys
import pyvisa

# ==========================================
# CONFIGURATION
# ==========================================
SCOPE_IP = "10.24.98.202"
TIMEOUT_MS = 5000  # 5 seconds timeout for commands


def connect_to_scope(ip: str) -> pyvisa.Resource:
    """Establishes a connection to the oscilloscope via TCPIP."""
    resource_name = f"TCPIP0::{ip}::INSTR"
    
    # Initialize PyVISA with the pure-Python backend
    rm = pyvisa.ResourceManager("@py")
    
    print(f"Connecting to oscilloscope at {ip}...")
    try:
        scope = rm.open_resource(resource_name)
        scope.timeout = TIMEOUT_MS
        
        # Query identification (*IDN? is a standard SCPI command)
        idn_response = scope.query("*IDN?").strip()
        print(f"SUCCESS: Connected to {idn_response}")
        
        return scope
        
    except pyvisa.VisaIOError as e:
        print(f"ERROR: Could not connect to {ip}.")
        print(f"Details: {e}")
        sys.exit(1)


def main():
    # 1. Connect
    scope = connect_to_scope(SCOPE_IP)

    # 2. Example: Query basic settings or trigger a measurement
    # (You can add your custom SCPI commands here)
    print("\n--- Scope Status ---")
    
    # Close connection cleanly when finished
    scope.close()
    print("Connection closed safely.")


if __name__ == "__main__":
    main()