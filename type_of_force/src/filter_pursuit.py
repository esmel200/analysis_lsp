"""
Filter out rows where type_of_force_used_by_officer is exactly 'Pursuit'.
"""

import csv
from pathlib import Path

INPUT_FILE = Path(__file__).parent.parent / "input" / "uof_cit_louisiana_state_pd_2022_2024.csv"
OUTPUT_FILE = Path(__file__).parent.parent / "output" / "uof_cit_louisiana_state_pd_2022_2024_filtered.csv"


def main():
    with open(INPUT_FILE, "r", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        with open(OUTPUT_FILE, "w", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            total_rows = 0
            filtered_rows = 0
            for row in reader:
                total_rows += 1
                force_type = row["type_of_force_used_by_officer"].strip()
                if force_type == "Pursuit":
                    filtered_rows += 1
                    continue
                writer.writerow(row)

    print(f"Total rows processed: {total_rows}")
    print(f"Rows filtered out (Pursuit only): {filtered_rows}")
    print(f"Rows written: {total_rows - filtered_rows}")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
