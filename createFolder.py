from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Union

# Global configuration - change this to update the report location everywhere
BASE_PATH = r"C:\Essais\02 - Rapport"


# 1. Define the custom data type for TestType
class TestType(str, Enum):
    BMF = "BMF"
    OVERSPEED = "OverSpeed"
    FREEWHEEL = "FreeWheel"
    LOCKEDWHEEL = "LockedWheel"


# 2. Helper Method
def create_test_report_directory(
    pn: str,
    motor_sn: str,
    drive_sn: str,
    test_type: Union[TestType, str],
) -> Path:
    """
    Constructs and creates a folder directory for test reports.

    Path structure:
    BASE_PATH / PN / MotorSN_DriveSN / MotorSN_DriveSN_TestType / MotorSN_DriveSN_TestType_Date_Time
    """
    # Validate test_type
    if isinstance(test_type, str):
        try:
            test_type_value = TestType(test_type).value
        except ValueError:
            valid_options = [e.value for e in TestType]
            raise ValueError(f"Invalid test_type '{test_type}'. Must be one of: {valid_options}")
    elif isinstance(test_type, TestType):
        test_type_value = test_type.value
    else:
        raise TypeError("test_type must be an instance of TestType enum or a valid string.")

    # Generate current Date_Time string formatted for Windows path safety (YYYY-MM-DD_HH-MM-SS)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct component names
    motor_drive_combo = f"{motor_sn}_{drive_sn}"
    motor_drive_test = f"{motor_drive_combo}_{test_type_value}"
    final_folder_name = f"{motor_drive_test}_{timestamp}"

    # Build full path using the global BASE_PATH
    full_path = Path(BASE_PATH) / pn / motor_drive_combo / motor_drive_test / final_folder_name

    # Create directory tree if it doesn't exist
    full_path.mkdir(parents=True, exist_ok=True)

    return full_path


path = create_test_report_directory("10434039", "DEVELOP", "CO205A", "OverSpeed")

print(path)