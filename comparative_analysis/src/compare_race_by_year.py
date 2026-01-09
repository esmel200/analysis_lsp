"""
Compare use of force incidents by citizen race over time (2022-2024) across three datasets.
Shows year-over-year trends for each dataset side by side.
Louisiana State Police
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Define paths to all three datasets
BASE_DIR = Path(__file__).parent.parent.parent
DATASETS = {
    'All Incidents': BASE_DIR / 'citizen_level_analysis/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'Pursuit-Only Excluded': BASE_DIR / 'citizen_level_analysis_no_pursuit/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'All Pursuits Excluded': BASE_DIR / 'citizen_level_analysis_exclude_all_pursuits/input/uof_cit_louisiana_state_pd_2022_2024.csv',
}
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df['citizen_race'] = df['citizen_race'].fillna('Unknown').str.title()
    race_mapping = {
        'American Indian Or Alaska Native': 'Native American',
        'Asian / Pacific Islander': 'Asian',
    }
    df['citizen_race'] = df['citizen_race'].replace(race_mapping)
    return df

# Load all datasets
dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

# Get yearly counts by race for top 3 races (Black, White, Hispanic)
RACES_TO_PLOT = ['Black', 'White', 'Hispanic']
YEARS = [2022, 2023, 2024]

# Create subplots for each race
fig, axes = plt.subplots(1, 3, figsize=(16, 6))

dataset_colors = {
    'All Incidents': '#2E86AB',
    'Pursuit-Only Excluded': '#A23B72',
    'All Pursuits Excluded': '#F18F01'
}
dataset_markers = {
    'All Incidents': 'o',
    'Pursuit-Only Excluded': 's',
    'All Pursuits Excluded': '^'
}

# Print summary
print("=" * 100)
print("YEAR-OVER-YEAR RACE DISTRIBUTION COMPARISON")
print("Louisiana State Police (2022-2024)")
print("=" * 100)

for race_idx, race in enumerate(RACES_TO_PLOT):
    ax = axes[race_idx]

    print(f"\n{race.upper()} CITIZENS:")
    print(f"{'Dataset':<25} {'2022':>8} {'2023':>8} {'2024':>8} {'Change':>10}")
    print("-" * 60)

    for dataset_name, df in dfs.items():
        yearly = df[df['citizen_race'] == race].groupby('incident_year').size()
        counts = [yearly.get(year, 0) for year in YEARS]

        ax.plot(YEARS, counts, marker=dataset_markers[dataset_name],
                color=dataset_colors[dataset_name], linewidth=2, markersize=8,
                label=dataset_name)

        # Add data labels
        for year, count in zip(YEARS, counts):
            ax.annotate(str(count), (year, count), textcoords="offset points",
                       xytext=(0, 8), ha='center', fontsize=9, fontweight='bold',
                       color=dataset_colors[dataset_name])

        change = counts[-1] - counts[0]
        print(f"{dataset_name:<25} {counts[0]:>8} {counts[1]:>8} {counts[2]:>8} {change:>+10}")

    ax.set_title(f'{race} Citizens', fontsize=12, fontweight='bold')
    ax.set_xlabel('Year', fontsize=10)
    ax.set_ylabel('Number of Incidents', fontsize=10)
    ax.set_xticks(YEARS)
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.2)

    if race_idx == 2:
        ax.legend(loc='upper right', fontsize=8)

# Overall title
fig.suptitle('Use of Force by Race — Year-over-Year Comparison\nLouisiana State Police (2022-2024)',
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'compare_race_by_year.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {OUTPUT_DIR / 'compare_race_by_year.png'}")

# Additional analysis: Show percentage changes
print("\n" + "=" * 100)
print("PERCENTAGE OF BLACK CITIZENS IN EACH DATASET")
print("=" * 100)
print(f"{'Dataset':<25} {'2022':>12} {'2023':>12} {'2024':>12} {'Overall':>12}")
print("-" * 65)

for dataset_name, df in dfs.items():
    yearly_totals = df.groupby('incident_year').size()
    yearly_black = df[df['citizen_race'] == 'Black'].groupby('incident_year').size()

    pcts = []
    for year in YEARS:
        total = yearly_totals.get(year, 0)
        black = yearly_black.get(year, 0)
        pct = (black / total * 100) if total > 0 else 0
        pcts.append(f"{pct:.1f}%")

    overall_pct = len(df[df['citizen_race'] == 'Black']) / len(df) * 100
    print(f"{dataset_name:<25} {pcts[0]:>12} {pcts[1]:>12} {pcts[2]:>12} {overall_pct:>11.1f}%")
