"""
Analyze use of force incidents normalized by population demographics
Louisiana State Police (2022-2024)
FILTERED: Pursuit-only incidents excluded
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the use of force data
uof_df = pd.read_csv('citizen_level_analysis_no_pursuit/input/uof_cit_louisiana_state_pd_2022_2024.csv')
uof_df['citizen_race'] = uof_df['citizen_race'].fillna('unknown').str.title()

# Map data categories to standardized names
race_mapping = {
    'Asian': 'Asian / Pacific Islander',
    'American Indian Or Alaska Native': 'Native American',
}
uof_df['citizen_race'] = uof_df['citizen_race'].replace(race_mapping)

# Read the census demographics data
census_df = pd.read_csv('citizen_level_analysis_no_pursuit/input/lsp_troop_demographics_16plus.csv')

# Sum up the population across all troops
total_black = census_df['black_16plus'].sum()
total_white = census_df['white_16plus'].sum()
total_hispanic = census_df['hispanic_16plus'].sum()
total_native = census_df['native_american_16plus'].sum()
total_asian_pi = census_df['asian_pacific_islander_16plus'].sum()
total_pop = census_df['total_16plus'].sum()

# Calculate population percentages
pop_data = {
    'Black': (total_black, total_black / total_pop * 100),
    'White': (total_white, total_white / total_pop * 100),
    'Hispanic': (total_hispanic, total_hispanic / total_pop * 100),
    'Native American': (total_native, total_native / total_pop * 100),
    'Asian / Pacific Islander': (total_asian_pi, total_asian_pi / total_pop * 100),
    'Unknown': (0, 0)  # No population data for unknown
}

# Count use of force incidents by race (INCLUDING Unknown)
uof_counts = uof_df['citizen_race'].value_counts()
total_uof = len(uof_df)

# Calculate use of force percentages
uof_data = {
    'Black': (uof_counts.get('Black', 0), uof_counts.get('Black', 0) / total_uof * 100),
    'White': (uof_counts.get('White', 0), uof_counts.get('White', 0) / total_uof * 100),
    'Hispanic': (uof_counts.get('Hispanic', 0), uof_counts.get('Hispanic', 0) / total_uof * 100),
    'Native American': (uof_counts.get('Native American', 0), uof_counts.get('Native American', 0) / total_uof * 100),
    'Asian / Pacific Islander': (uof_counts.get('Asian / Pacific Islander', 0), uof_counts.get('Asian / Pacific Islander', 0) / total_uof * 100),
    'Unknown': (uof_counts.get('Unknown', 0), uof_counts.get('Unknown', 0) / total_uof * 100),
}

# Print summary report
print("=" * 85)
print("POPULATION-NORMALIZED USE OF FORCE ANALYSIS (PURSUIT EXCLUDED)")
print("Louisiana State Police (2022-2024)")
print("=" * 85)
print(f"\nTotal Population (16+): {total_pop:,}")
print(f"Total Use of Force Incidents: {total_uof:,}")
print("\n" + "=" * 85)
print(f"{'Race':<28} {'Population %':>15} {'UoF Incidents %':>18} {'Disparity':>15}")
print("=" * 85)

disparity_data = {}
for race in ['Black', 'White', 'Hispanic', 'Asian / Pacific Islander', 'Native American', 'Unknown']:
    pop_pct = pop_data[race][1]
    uof_pct = uof_data[race][1]

    if race == 'Unknown':
        disparity_str = 'N/A'
        print(f"{race:<28} {pop_pct:>14.1f}% {uof_pct:>17.1f}% {disparity_str:>15}")
    else:
        disparity = uof_pct / pop_pct if pop_pct > 0 else 0
        disparity_data[race] = disparity
        print(f"{race:<28} {pop_pct:>14.1f}% {uof_pct:>17.1f}% {disparity:>14.2f}x")

print("=" * 85)
print("\nNotes:")
print("- Disparity ratio shows UoF incident % divided by population %")
print("- A ratio > 1.0 indicates over-representation in UoF incidents")
print("- A ratio < 1.0 indicates under-representation in UoF incidents")
print("- Unknown race incidents included in total counts and percentages")
print("- Unknown has no population comparison (N/A)")
print("- PURSUIT-ONLY INCIDENTS HAVE BEEN EXCLUDED FROM THIS ANALYSIS")
print("=" * 85)

# Prepare data for visualization
races = ['Black', 'White', 'Unknown', 'Hispanic', 'Asian / Pacific Islander', 'Native American']
pop_percentages = [
    total_black / total_pop * 100,
    total_white / total_pop * 100,
    0,  # No population data for unknown
    total_hispanic / total_pop * 100,
    total_asian_pi / total_pop * 100,
    total_native / total_pop * 100,
]
uof_percentages = [
    uof_counts.get('Black', 0) / total_uof * 100,
    uof_counts.get('White', 0) / total_uof * 100,
    uof_counts.get('Unknown', 0) / total_uof * 100,
    uof_counts.get('Hispanic', 0) / total_uof * 100,
    uof_counts.get('Asian / Pacific Islander', 0) / total_uof * 100,
    uof_counts.get('Native American', 0) / total_uof * 100,
]

# Create the visualization
fig, ax = plt.subplots(figsize=(14, 7))

x = np.arange(len(races))
width = 0.35

# Create bars
bars1 = ax.bar(x - width/2, pop_percentages, width, label='Population (16+)',
               color='#B8B8B8', edgecolor='black', linewidth=1.2)
bars2 = ax.bar(x + width/2, uof_percentages, width, label='Use of Force Incidents',
               color='#4A90E2', edgecolor='black', linewidth=1.2)

# Customize the chart
ax.set_xlabel('Citizen Race', fontsize=12, fontweight='bold')
ax.set_ylabel('Percentage', fontsize=12, fontweight='bold')
ax.set_title('Use of Force Incidents vs Population Demographics (Pursuit Excluded)\nLouisiana State Police (2022-2024)',
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(races, rotation=45, ha='right')
ax.legend(fontsize=11, loc='upper right')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontweight='bold', fontsize=9)

# Add grid
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add note about unknown cases
note_text = f"Note: Unknown has no population comparison. Total incidents: {total_uof:,} (Pursuit excluded)"
ax.text(0.5, -0.25, note_text, transform=ax.transAxes,
        ha='center', fontsize=9, style='italic')

plt.tight_layout()
plt.savefig('citizen_level_analysis_no_pursuit/output/citizen_race_population_normalized.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'citizen_race_population_normalized.png'")
