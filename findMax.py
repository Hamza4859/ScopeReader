import csv
from pathlib import Path

def get_max_values(folder_path_str: str):
    folder_path = Path(folder_path_str)
    
    # Search for the first file matching *VRMS.csv
    try:
        target_file = next(folder_path.glob("*VRMS.csv"))
    except StopIteration:
        raise FileNotFoundError(f"No file ending with 'VRMS.csv' found in {folder_path_str}")

    max_col2 = max_col3 = max_col4 = None

    with open(target_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # skip header safely even if file is empty

        for row in reader:
            if len(row) < 4:
                continue  # skip incomplete rows
            try:
                val2, val3, val4 = float(row[1]), float(row[2]), float(row[3])
            except ValueError:
                continue  # skip rows with non-numeric data

            max_col2 = val2 if max_col2 is None else max(max_col2, val2)
            max_col3 = val3 if max_col3 is None else max(max_col3, val3)
            max_col4 = val4 if max_col4 is None else max(max_col4, val4)

    return [max_col2, max_col3, max_col4]