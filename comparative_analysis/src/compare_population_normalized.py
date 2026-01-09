"""
Compare use of force incidents normalized by population demographics across three datasets.
Shows disparity ratios (UoF % / Population %) for each dataset.
Louisiana State Police (2022-2024)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).parent.parent.parent
DATASETS = {
    'All Incidents': BASE_DIR / 'citizen_level_analysis/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'Pursuit-Only Excluded': BASE_DIR / 'citizen_level_analysis_no_pursuit/input/uof_cit_louisiana_state_pd_2022_2024.csv',
    'All Pursuits Excluded': BASE_DIR / 'citizen_level_analysis_exclude_all_pursuits/input/uof_cit_louisiana_state_pd_2022_2024.csv',
}
CENSUS_PATH = BASE_DIR / 'comparative_analysis/input/lsp_troop_demographics_16plus.csv'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Race categories
RACES = ['Black', 'White', 'Hispanic', 'Asian / Pacific Islander', 'Native American']

def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df['citizen_race'] = df['citizen_race'].fillna('Unknown').str.title()
    race_mapping = {
        'American Indian Or Alaska Native': 'Native American',
        'Asian': 'Asian / Pacific Islander',
    }
    df['citizen_race'] = df['citizen_race'].replace(race_mapping)
    return df

# Load census data
census_df = pd.read_csv(CENSUS_PATH)
total_pop = census_df['total_16plus'].sum()

# Population percentages
pop_pct = {
    'Black': census_df['black_16plus'].sum() / total_pop * 100,
    'White': census_df['white_16plus'].sum() / total_pop * 100,
    'Hispanic': census_df['hispanic_16plus'].sum() / total_pop * 100,
    'Asian / Pacific Islander': census_df['asian_pacific_islander_16plus'].sum() / total_pop * 100,
    'Native American': census_df['native_american_16plus'].sum() / total_pop * 100,
}

# Load all UoF datasets
dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

# Calculate UoF percentages and disparity ratios
disparity_data = {}
uof_pct_data = {}

for dataset_name, df in dfs.items():
    total_uof = len(df)
    counts = df['citizen_race'].value_counts()

    uof_pct = {}
    disparities = {}
    for race in RACES:
        count = counts.get(race, 0)
        pct = count / total_uof * 100
        uof_pct[race] = pct
        disparities[race] = pct / pop_pct[race] if pop_pct[race] > 0 else 0

    uof_pct_data[dataset_name] = uof_pct
    disparity_data[dataset_name] = disparities

# Print detailed analysis
print("=" * 100)
print("POPULATION-NORMALIZED COMPARATIVE ANALYSIS")
print("Louisiana State Police (2022-2024)")
print("=" * 100)

print(f"\nTotal Population (16+): {total_pop:,}")
print("\nDataset sizes:")
for name, df in dfs.items():
    print(f"  {name}: {len(df):,} incidents")

print("\n" + "=" * 100)
print("DISPARITY RATIOS BY DATASET (UoF % ÷ Population %)")
print("=" * 100)
print(f"{'Race':<25} {'Population':>12} {'All':>12} {'No Pursuit-Only':>16} {'No Pursuits':>14}")
print("-" * 100)

for race in RACES:
    all_disp = disparity_data['All Incidents'][race]
    no_pursuit_disp = disparity_data['Pursuit-Only Excluded'][race]
    excl_pursuit_disp = disparity_data['All Pursuits Excluded'][race]
    print(f"{race:<25} {pop_pct[race]:>11.1f}% {all_disp:>11.2f}x {no_pursuit_disp:>15.2f}x {excl_pursuit_disp:>13.2f}x")

print("=" * 100)
print("\nInterpretation:")
print("  > 1.0x = over-represented in UoF incidents relative to population")
print("  < 1.0x = under-represented in UoF incidents relative to population")
print("  = 1.0x = proportionate representation")

# Create visualization - Disparity ratios comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Plot 1: UoF Percentages vs Population
ax1 = axes[0]
x = np.arange(len(RACES))
width = 0.2

# Population bars
pop_vals = [pop_pct[race] for race in RACES]
ax1.bar(x - 1.5*width, pop_vals, width, label='Population (16+)', color='#B8B8B8', edgecolor='black')

# UoF bars for each dataset
dataset_colors = ['#2E86AB', '#A23B72', '#F18F01']
for idx, (dataset_name, uof_pcts) in enumerate(uof_pct_data.items()):
    uof_vals = [uof_pcts[race] for race in RACES]
    bars = ax1.bar(x + (idx - 0.5)*width, uof_vals, width, label=dataset_name,
                   color=dataset_colors[idx], edgecolor='black', linewidth=0.5)

ax1.set_xlabel('Race', fontsize=11, fontweight='bold')
ax1.set_ylabel('Percentage', fontsize=11, fontweight='bold')
ax1.set_title('UoF Incident % vs Population %', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([r.replace(' / ', '\n') for r in RACES], fontsize=9, rotation=0)
ax1.legend(fontsize=8, loc='upper right')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Plot 2: Disparity ratios
ax2 = axes[1]
x = np.arange(len(RACES))
width = 0.25

for idx, (dataset_name, disparities) in enumerate(disparity_data.items()):
    vals = [disparities[race] for race in RACES]
    bars = ax2.bar(x + (idx - 1)*width, vals, width, label=dataset_name,
                   color=dataset_colors[idx], edgecolor='black', linewidth=0.5)

    # Add value labels
    for bar, val in zip(bars, vals):
        ax2.annotate(f'{val:.2f}x',
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=7, fontweight='bold')

# Add reference line at 1.0
ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, label='Equal representation')

ax2.set_xlabel('Race', fontsize=11, fontweight='bold')
ax2.set_ylabel('Disparity Ratio (UoF % ÷ Population %)', fontsize=11, fontweight='bold')
ax2.set_title('Disparity Ratios by Dataset', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([r.replace(' / ', '\n') for r in RACES], fontsize=9, rotation=0)
ax2.legend(fontsize=8, loc='upper right')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

fig.suptitle('Population-Normalized Use of Force Analysis — Comparative View\n'
             'Louisiana State Police (2022-2024)',
             fontsize=14, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'compare_population_normalized.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {OUTPUT_DIR / 'compare_population_normalized.png'}")

# Print key findings
print("\n" + "=" * 100)
print("KEY FINDINGS")
print("=" * 100)
print(f"\nBlack citizens disparity ratio:")
print(f"  All incidents:           {disparity_data['All Incidents']['Black']:.2f}x")
print(f"  Pursuit-only excluded:   {disparity_data['Pursuit-Only Excluded']['Black']:.2f}x")
print(f"  All pursuits excluded:   {disparity_data['All Pursuits Excluded']['Black']:.2f}x")

black_change_partial = disparity_data['Pursuit-Only Excluded']['Black'] - disparity_data['All Incidents']['Black']
black_change_full = disparity_data['All Pursuits Excluded']['Black'] - disparity_data['All Incidents']['Black']
print(f"\nChange from baseline (All Incidents):")
print(f"  When excluding pursuit-only:   {black_change_partial:+.2f}x")
print(f"  When excluding all pursuits:   {black_change_full:+.2f}x")
