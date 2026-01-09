"""
Compare overall use of force incidents by citizen race across three datasets:
1. All incidents
2. Pursuit-only excluded
3. All pursuit incidents excluded
Louisiana State Police (2022-2024)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Define paths to all three datasets
BASE_DIR = Path(__file__).parent.parent.parent
DATASETS = {
    'All Incidents': BASE_DIR / 'citizen_level_analysis/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'Pursuit-Only\nExcluded': BASE_DIR / 'citizen_level_analysis_no_pursuit/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'All Pursuits\nExcluded': BASE_DIR / 'citizen_level_analysis_exclude_all_pursuits/input/uof_cit_louisiana_state_pd_2022_2024.csv',
}
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Race categories to display (in order)
RACE_ORDER = ['Black', 'White', 'Unknown', 'Hispanic', 'Asian', 'Native American']

# Color map for races
RACE_COLORS = {
    'Black': '#4A90E2',
    'White': '#7ED321',
    'Unknown': '#9B9B9B',
    'Hispanic': '#F5A623',
    'Asian': '#BD10E0',
    'Native American': '#D0021B'
}

# Load and process each dataset
def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df['citizen_race'] = df['citizen_race'].fillna('unknown').str.title()

    # Standardize race labels
    race_mapping = {
        'American Indian Or Alaska Native': 'Native American',
        'Asian / Pacific Islander': 'Asian',
    }
    df['citizen_race'] = df['citizen_race'].replace(race_mapping)

    return df

# Load all datasets
dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

# Get race counts for each dataset
race_counts = {}
for name, df in dfs.items():
    counts = df['citizen_race'].value_counts()
    race_counts[name] = {race: counts.get(race, 0) for race in RACE_ORDER}

# Print summary statistics
print("=" * 90)
print("COMPARATIVE RACE DISTRIBUTION ANALYSIS")
print("Louisiana State Police (2022-2024)")
print("=" * 90)

print(f"\n{'Dataset':<25} {'Total':>10} {'Black':>10} {'White':>10} {'Hispanic':>10}")
print("-" * 90)
for name, df in dfs.items():
    counts = race_counts[name]
    name_clean = name.replace('\n', ' ')
    print(f"{name_clean:<25} {len(df):>10} {counts['Black']:>10} {counts['White']:>10} {counts['Hispanic']:>10}")

# Calculate percentages
print(f"\n{'Dataset':<25} {'Black %':>10} {'White %':>10} {'Hispanic %':>10}")
print("-" * 90)
for name, df in dfs.items():
    total = len(df)
    counts = race_counts[name]
    name_clean = name.replace('\n', ' ')
    print(f"{name_clean:<25} {counts['Black']/total*100:>9.1f}% {counts['White']/total*100:>9.1f}% {counts['Hispanic']/total*100:>9.1f}%")

# Create the visualization
fig, ax = plt.subplots(figsize=(16, 8))

x = np.arange(len(RACE_ORDER))
width = 0.25
multiplier = 0

dataset_colors = ['#2E86AB', '#A23B72', '#F18F01']

for idx, (name, counts) in enumerate(race_counts.items()):
    values = [counts[race] for race in RACE_ORDER]
    total = sum(values)
    offset = width * multiplier
    bars = ax.bar(x + offset, values, width, label=f"{name} (n={total})",
                  color=dataset_colors[idx], edgecolor='white', linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, values):
        if val > 0:
            pct = val / total * 100
            ax.annotate(f'{val}\n({pct:.1f}%)',
                       xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=7, fontweight='bold')

    multiplier += 1

# Customize chart
ax.set_xlabel('Citizen Race', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
ax.set_title('Use of Force Incidents by Citizen Race — Comparative Analysis\n'
             'Louisiana State Police (2022-2024)', fontsize=14, fontweight='bold', pad=20)

ax.set_xticks(x + width)
ax.set_xticklabels(RACE_ORDER, fontsize=11)
ax.legend(loc='upper right', fontsize=10, title='Dataset', title_fontsize=10)

ax.yaxis.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

# Add explanatory note
note = ("Note: 'Pursuit-Only Excluded' removes incidents where force type = 'Pursuit' only.\n"
        "'All Pursuits Excluded' removes any incident containing 'Pursuit' in the force type.")
ax.text(0.5, -0.12, note, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'compare_race_distribution.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {OUTPUT_DIR / 'compare_race_distribution.png'}")
