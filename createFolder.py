import shutil
from datetime import datetime
from enum import Enum
from pathlib import Path


# Global configuration - change this to update the report location everywhere
BASE_PATH = r"C:\Essais\02 - Rapport"
EOL_TESTING_BASE_PATH = r"C:\EOL_Testing"


#Define allowed TestType  
class TestType(str, Enum):
    BMF = "BMF"
    OVERSPEED = "OverSpeed"
    FREEWHEEL = "Free Wheel"
    LOCKEDWHEEL = "Locked Wheel"
    E11 = "E11"


#Create test report directory
def create_test_report_directory(
    pn: str,
    motor_sn: str,
    drive_sn: str,
    test_type: str,
) -> str:
    """
    Constructs and creates a folder directory for test reports.

    Path structure:
    BASE_PATH / PN / MotorSN_DriveSN / MotorSN_DriveSN_TestType
    """
    # Validate test_type against allowed values
    try:
        test_type_value = TestType(test_type).value
    except ValueError:
        valid_options = [e.value for e in TestType]
        raise ValueError(f"Invalid test_type '{test_type}'. Must be one of: {valid_options}")

    # Construct component names
    motor_drive_combo = f"{motor_sn}_{drive_sn}"
    motor_drive_test = f"{motor_drive_combo}_{test_type_value}"

    # Build full path using the global BASE_PATH
    full_path = Path(BASE_PATH) / pn / motor_drive_combo / motor_drive_test

    # Create directory tree if it doesn't exist
    full_path.mkdir(parents=True, exist_ok=True)

    return str(full_path)


#Get most recent folder
def get_most_recent_folder(base_path: str) -> Path:
    base = Path(base_path)

    if not base.exists():
        raise FileNotFoundError(f"Base path does not exist: {base_path}")

    folders = [p for p in base.iterdir() if p.is_dir()]

    if not folders:
        raise FileNotFoundError(f"No subfolders found in: {base_path}")

    most_recent = max(folders, key=lambda p: p.stat().st_mtime)
    return most_recent


#Moves only the content of the source
def move_files_content(destination: str) -> None:
    source_path = get_most_recent_folder(EOL_TESTING_BASE_PATH)
    destination_path = Path(destination)  # string -> Path conversion happens here

    if source_path.is_file():
        if destination_path.is_dir():
            destination_path = destination_path / source_path.name
        else:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(destination_path))

    elif source_path.is_dir():
        destination_path.mkdir(parents=True, exist_ok=True)
        for item in list(source_path.iterdir()):
            if item.is_file():
                shutil.move(str(item), str(destination_path / item.name))

    else:
        raise ValueError(f"Source path is neither a file nor a directory: {source_path}")
        


#Copy only the content of the folder
def copy_files_content(source: str, destination: str) -> None:
    source_path = Path(source)
    destination_path = Path(destination)

    if not source_path.exists():
        raise FileNotFoundError(f"Source path does not exist: {source}")

    if source_path.is_file():
        if destination_path.is_dir():
            destination_path = destination_path / source_path.name
        else:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)

    elif source_path.is_dir():
        destination_path.mkdir(parents=True, exist_ok=True)
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, destination_path / item.name)

    else:
        raise ValueError(f"Source path is neither a file nor a directory: {source}")