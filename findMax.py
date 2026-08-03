import csv
import sys

def get_max_values(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header row; remove if no header

        max_col2 = max_col3 = max_col4 = None

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

        return max_col2, max_col3, max_col4

if __name__ == "__main__":
    path = r"C:\Users\hamza.rtelbennani\Downloads\10557250-SN_SP24000556_VRMS.csv"
    m2, m3, m4 = get_max_values(path)
    print(f"Max of column 2: {m2}")
    print(f"Max of column 3: {m3}")
    print(f"Max of column 4: {m4}")