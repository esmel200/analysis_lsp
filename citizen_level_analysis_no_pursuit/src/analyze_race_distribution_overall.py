"""
Analyze overall use of force incidents by citizen race (2022-2024)
Louisiana State Police
FILTERED: Pursuit-only incidents excluded
"""

import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('citizen_level_analysis_no_pursuit/input/uof_cit_louisiana_state_pd_2022_2024.csv')

# Fill null values in citizen_race with 'unknown'
df['citizen_race'] = df['citizen_race'].fillna('unknown')

# Capitalize the race entries
df['citizen_race'] = df['citizen_race'].str.title()

# Count incidents by citizen_race
race_counts = df['citizen_race'].value_counts().sort_values(ascending=False)

# Define colors for each race category
color_map = {
    'Black': '#4A90E2',           # Blue
    'White': '#7ED321',           # Green
    'Unknown': '#9B9B9B',         # Gray
    'Hispanic': '#F5A623',        # Orange
    'Asian / Pacific Islander': '#BD10E0',  # Purple
    'Native American': '#D0021B'  # Red
}

# Get colors in the order of race_counts
colors = [color_map.get(race, '#50E3C2') for race in race_counts.index]

# Print statistics
print("Incident Counts by Citizen Race:")
print("=" * 40)
for race, count in race_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{race:15} {count:5} ({percentage:5.2f}%)")
print("=" * 40)
print(f"{'TOTAL':15} {len(df):5} (100.00%)")

# Create the visualization
fig, ax = plt.subplots(figsize=(12, 6))

# Create bar chart with different colors
bars = ax.bar(range(len(race_counts)), race_counts.values, color=colors,
               edgecolor='black', linewidth=1.2)

# Customize the chart
ax.set_xlabel('Citizen Race', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
ax.set_title('Use of Force Incidents by Citizen Race (Pursuit Excluded)\nLouisiana State Police (2022-2024)',
             fontsize=14, fontweight='bold')
ax.set_xticks(range(len(race_counts)))
ax.set_xticklabels(race_counts.index, rotation=45, ha='right')

# Add value labels on top of bars
for i, (bar, count) in enumerate(zip(bars, race_counts.values)):
    percentage = (count / len(df)) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 15,
            f'{count}\n({percentage:.1f}%)',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

# Add grid for easier reading
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig('citizen_level_analysis_no_pursuit/output/citizen_race_distribution.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'citizen_race_distribution.png'")
