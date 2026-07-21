import time
import pyvisa

SCOPE_IP = "10.24.98.202"

# 1. Initialize Connection
rm = pyvisa.ResourceManager("@py")
scope = rm.open_resource(f"TCPIP0::{SCOPE_IP}::INSTR")
scope.timeout = 20000  # Increased to 20s as image transfers take longer


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


# 2. Setup Scope & Image Format
scope.write("*CLS")

print("\n" + "=" * 60)
print("CAPTURING SCREENSHOT VIA (:IMAGe:SEND?)")
print("=" * 60)

try:
    # Optional: Configure desired format (PNG, BMP, JPEG)
    # Yokogawa defaults to PNG or BMP depending on model setup
    scope.write(":IMAGe:FORMat PNG")
except pyvisa.VisaIOError:
    pass

# 3. Request and Fetch Raw Screen Capture Data
try:
    print("Requesting screen capture from scope...")

    # query_binary_values handles the IEEE 488.2 header (#8000...) automatically
    # datatype='B' yields raw uint8 bytes, container=bytes keeps it as a byte array
    img_bytes = scope.query_binary_values(
        ":IMAGe:SEND?", 
        datatype="B", 
        container=bytes
    )

    # Output details directly to the terminal
    print("\n--- SCREENSHOT DATA RETRIEVED ---")
    print(f"Data Type:         {type(img_bytes)}")
    print(f"Total Size:        {len(img_bytes)} bytes ({len(img_bytes) / 1024:.2f} KB)")
    print(f"Header Preview:    {img_bytes[:16]}")
    
    # Save the binary data locally
    output_filename = "scope_screenshot.png"
    with open(output_filename, "wb") as f:
        f.write(img_bytes)

    print(f"\nSuccess! Screenshot saved locally to '{output_filename}'")

except pyvisa.VisaIOError as e:
    print(f"\nFailed to capture image: {e}")
    drain_errors()

# 4. Clean up
scope.close()
print("\nConnection closed successfully.")