"""
Create citizen-level dataset from raw incident data
Expands each incident to one row per citizen
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
print("CREATING CITIZEN-LEVEL DATASET")
print("=" * 80)
print(f"\nStarting with {len(raw_df):,} incidents")
print(f"Expected total citizens: {raw_df['Subject Count'].sum():,}")

# Function to parse comma-separated values
def parse_list(text):
    if pd.isna(text) or text == '':
        return []
    return [x.strip() for x in str(text).split(',') if x.strip()]

# Create citizen-level records
citizen_records = []

for idx, row in raw_df.iterrows():
    subject_count = row['Subject Count']

    # Parse names and races
    names = parse_list(row['Subject Full Name'])
    races = parse_list(row['Subject Race'])
    force_by_subject = parse_list(row['Type of Force Used By Subject'])

    # If we have fewer races than subjects, extend with the last available race
    # This handles cases where 2 subjects have 1 race listed
    if len(races) < subject_count:
        if len(races) > 0:
            # Use the single race for all subjects
            races = [races[0]] * subject_count
        else:
            races = ['Unknown'] * subject_count

    # If we have fewer names than subjects, fill with Unknown
    if len(names) < subject_count:
        if len(names) > 0:
            names.extend(['Unknown'] * (subject_count - len(names)))
        else:
            names = ['Unknown'] * subject_count

    # If we have fewer force types than subjects, extend or fill
    if len(force_by_subject) < subject_count:
        if len(force_by_subject) > 0:
            force_by_subject.extend([None] * (subject_count - len(force_by_subject)))
        else:
            force_by_subject = [None] * subject_count

    # Parse date
    date = pd.to_datetime(row['Event Start Date'])

    # Create tracking_id (hash of REN)
    tracking_id = hashlib.md5(str(row['REN']).encode()).hexdigest()

    # Create one record per citizen
    for i in range(subject_count):
        citizen_name = names[i] if i < len(names) else 'Unknown'
        citizen_race = races[i] if i < len(races) else 'Unknown'
        citizen_force = force_by_subject[i] if i < len(force_by_subject) else None

        # Create unique citizen_uid
        citizen_uid = hashlib.md5(f"{row['REN']}_citizen_{i}_{citizen_name}_{citizen_race}".encode()).hexdigest()

        citizen_records.append({
            # Incident identifiers
            'ren': row['REN'],
            'tracking_id': tracking_id,
            'incident_date': row['Event Start Date'],
            'incident_year': date.year,
            'incident_month': date.month,
            'incident_day': date.day,

            # Department/Agency
            # Normalize Troop N -> Troop NOLA (both refer to New Orleans)
            'troop': 'Troop NOLA' if row['Troop'] == 'Troop N' else row['Troop'],
            'department_desc': 'troop nola' if row['Troop'] == 'Troop N' else row['Troop'].lower(),
            'agency': 'louisiana-state-pd',

            # Citizen-specific data (expanded from multi-subject incidents)
            'citizen_index': i + 1,  # Which citizen this is in the incident (1st, 2nd, etc.)
            'citizen_name': citizen_name,
            'citizen_race': citizen_race.lower() if pd.notna(citizen_race) and citizen_race != '' else None,
            'use_of_force_by_citizen': citizen_force.lower() if pd.notna(citizen_force) and citizen_force != '' else None,
            'citizen_uid': citizen_uid,

            # Incident-level counts (same for all citizens in the incident)
            'subject_count': row['Subject Count'],
            'trooper_officer_count': row['Trooper/Officer Count'],
            'number_of_uses_of_force': row['# of Uses of Force'],

            # All subjects/officers in the incident (not expanded)
            'all_subject_names': row['Subject Full Name'],
            'all_subject_races': row['Subject Race'],

            # Officer data (applies to all citizens in the incident)
            'type_of_force_used_by_officer': row['Type of Force Used By Officer'],
            'trooper_officer_names': row['Trooper/Officer Name'],
            'trooper_officer_races': row['Trooper/Officer Race'],

            # Additional incident info
            'justified': row['Justified (Y/N)'],
        })

# Create dataframe
citizen_df = pd.DataFrame(citizen_records)

print(f"\nCreated {len(citizen_df):,} citizen records")
print(f"Expected: {raw_df['Subject Count'].sum():,}")
print(f"Match: {len(citizen_df) == raw_df['Subject Count'].sum()}")

# Verify counts
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

print(f"\nUnique tracking_ids: {citizen_df['tracking_id'].nunique():,}")
print(f"Original incidents: {len(raw_df):,}")

# Check distribution
print("\nCitizens per incident distribution:")
tracking_counts = citizen_df['tracking_id'].value_counts().value_counts().sort_index()
for count, freq in tracking_counts.items():
    print(f"  {count} citizen(s): {freq:,} incidents")

# Year distribution
print("\nYear distribution:")
year_counts = citizen_df['incident_year'].value_counts().sort_index()
for year, count in year_counts.items():
    print(f"  {year}: {count:,} citizens")

# Race distribution
print("\nRace distribution:")
race_counts = citizen_df['citizen_race'].fillna('unknown').value_counts()
for race, count in race_counts.items():
    print(f"  {race}: {count:,}")

# Save to CSV
output_path = OUTPUT_DIR / 'uof_cit_louisiana_state_pd_2022_2024.csv'
citizen_df.to_csv(output_path, index=False)
print("\n" + "=" * 80)
print(f"Citizen-level data saved to: {output_path}")
print("=" * 80)

# Show sample - select key columns for display
print("\nSample records (key columns):")
display_cols = ['ren', 'incident_date', 'troop', 'citizen_name', 'citizen_race',
                'subject_count', 'trooper_officer_count', 'citizen_index']
print(citizen_df[display_cols].head(10).to_string())

print(f"\nTotal columns in dataset: {len(citizen_df.columns)}")
print(f"Column names: {list(citizen_df.columns)}")
