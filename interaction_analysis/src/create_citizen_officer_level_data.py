"""
Create citizen-officer level dataset from raw incident data
Expands each incident to one row per citizen-officer pair
Louisiana State Police (2022-2024)
"""

import pandas as pd
import hashlib
from pathlib import Path

# Get the directory where this script lives
SCRIPT_DIR = Path(__file__).parent.parent  # interaction_analysis/
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"

# Read the raw file
raw_df = pd.read_csv(INPUT_DIR / 'lsp_uof_22_24.csv')

print("=" * 80)
print("CREATING CITIZEN-OFFICER LEVEL DATASET")
print("=" * 80)
print(f"\nStarting with {len(raw_df):,} incidents")
print(f"Total citizens: {raw_df['Subject Count'].sum():,}")
print(f"Total officers: {raw_df['Trooper/Officer Count'].sum():,}")

# Calculate expected rows (citizen × officer for each incident)
expected_rows = (raw_df['Subject Count'] * raw_df['Trooper/Officer Count']).sum()
print(f"Expected citizen-officer pairs: {expected_rows:,}")

# Function to parse comma-separated values
def parse_list(text):
    if pd.isna(text) or text == '':
        return []
    return [x.strip() for x in str(text).split(',') if x.strip()]

# Create citizen-officer level records
records = []

for idx, row in raw_df.iterrows():
    subject_count = row['Subject Count']
    officer_count = row['Trooper/Officer Count']

    # Parse subject data
    subject_names = parse_list(row['Subject Full Name'])
    subject_races = parse_list(row['Subject Race'])
    force_by_subject = parse_list(row['Type of Force Used By Subject'])

    # Parse officer data
    officer_names = parse_list(row['Trooper/Officer Name'])
    officer_races = parse_list(row['Trooper/Officer Race'])

    # Extend lists if needed
    if len(subject_races) < subject_count:
        if len(subject_races) > 0:
            subject_races = [subject_races[0]] * subject_count
        else:
            subject_races = ['Unknown'] * subject_count

    if len(subject_names) < subject_count:
        if len(subject_names) > 0:
            subject_names.extend(['Unknown'] * (subject_count - len(subject_names)))
        else:
            subject_names = ['Unknown'] * subject_count

    if len(force_by_subject) < subject_count:
        if len(force_by_subject) > 0:
            force_by_subject.extend([None] * (subject_count - len(force_by_subject)))
        else:
            force_by_subject = [None] * subject_count

    # Extend officer lists if needed
    if len(officer_races) < officer_count:
        if len(officer_races) > 0:
            officer_races = [officer_races[0]] * officer_count
        else:
            officer_races = ['Unknown'] * officer_count

    if len(officer_names) < officer_count:
        if len(officer_names) > 0:
            officer_names.extend(['Unknown'] * (officer_count - len(officer_names)))
        else:
            officer_names = ['Unknown'] * officer_count

    # Parse date
    date = pd.to_datetime(row['Event Start Date'])

    # Create tracking_id (hash of REN)
    tracking_id = hashlib.md5(str(row['REN']).encode()).hexdigest()

    # Create one record per citizen-officer pair (cartesian product)
    for citizen_idx in range(subject_count):
        citizen_name = subject_names[citizen_idx]
        citizen_race = subject_races[citizen_idx]
        citizen_force = force_by_subject[citizen_idx]

        for officer_idx in range(officer_count):
            officer_name = officer_names[officer_idx]
            officer_race = officer_races[officer_idx]

            # Create unique IDs
            citizen_uid = hashlib.md5(f"{row['REN']}_citizen_{citizen_idx}_{citizen_name}_{citizen_race}".encode()).hexdigest()
            officer_uid = hashlib.md5(f"{row['REN']}_officer_{officer_idx}_{officer_name}_{officer_race}".encode()).hexdigest()
            interaction_uid = hashlib.md5(f"{row['REN']}_c{citizen_idx}_o{officer_idx}".encode()).hexdigest()

            records.append({
                # Incident identifiers
                'ren': row['REN'],
                'tracking_id': tracking_id,
                'interaction_uid': interaction_uid,
                'incident_date': row['Event Start Date'],
                'incident_year': date.year,
                'incident_month': date.month,
                'incident_day': date.day,

                # Department/Agency
                'troop': row['Troop'],
                'department_desc': row['Troop'].lower(),
                'agency': 'louisiana-state-pd',

                # Citizen-specific data
                'citizen_index': citizen_idx + 1,
                'citizen_name': citizen_name,
                'citizen_race': citizen_race.lower() if pd.notna(citizen_race) and citizen_race != '' else None,
                'use_of_force_by_citizen': citizen_force.lower() if pd.notna(citizen_force) and citizen_force != '' else None,
                'citizen_uid': citizen_uid,

                # Officer-specific data
                'officer_index': officer_idx + 1,
                'officer_name': officer_name,
                'officer_race': officer_race.lower() if pd.notna(officer_race) and officer_race != '' else None,
                'officer_uid': officer_uid,

                # Incident-level counts
                'subject_count': row['Subject Count'],
                'trooper_officer_count': row['Trooper/Officer Count'],
                'number_of_uses_of_force': row['# of Uses of Force'],

                # Incident-level data
                'type_of_force_used_by_officer': row['Type of Force Used By Officer'],
                'justified': row['Justified (Y/N)'],
            })

# Create dataframe
df = pd.DataFrame(records)

print(f"\nCreated {len(df):,} citizen-officer pair records")
print(f"Expected: {expected_rows:,}")
print(f"Match: {len(df) == expected_rows}")

# Verify counts
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

print(f"\nUnique tracking_ids (incidents): {df['tracking_id'].nunique():,}")
print(f"Unique citizen_uids: {df['citizen_uid'].nunique():,}")
print(f"Unique officer_uids: {df['officer_uid'].nunique():,}")

# Year distribution
print("\nYear distribution:")
year_counts = df['incident_year'].value_counts().sort_index()
for year, count in year_counts.items():
    print(f"  {year}: {count:,} citizen-officer pairs")

# Race distributions
print("\nCitizen race distribution:")
citizen_race_counts = df['citizen_race'].fillna('unknown').value_counts()
for race, count in citizen_race_counts.head(10).items():
    print(f"  {race}: {count:,}")

print("\nOfficer race distribution:")
officer_race_counts = df['officer_race'].fillna('unknown').value_counts()
for race, count in officer_race_counts.head(10).items():
    print(f"  {race}: {count:,}")

# Save to CSV
output_path = OUTPUT_DIR / 'uof_cit_officer_louisiana_state_pd_2022_2024.csv'
df.to_csv(output_path, index=False)

print("\n" + "=" * 80)
print(f"Citizen-officer level data saved to: {output_path}")
print("=" * 80)

print(f"\nTotal columns: {len(df.columns)}")
print(f"Columns: {list(df.columns)}")

# Show sample
print("\nSample records (key columns):")
display_cols = ['ren', 'incident_date', 'citizen_name', 'citizen_race',
                'officer_name', 'officer_race', 'subject_count', 'trooper_officer_count']
print(df[display_cols].head(15).to_string())
