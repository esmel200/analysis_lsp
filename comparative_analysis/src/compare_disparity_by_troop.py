"""
Heatmap tables showing disparity ratios (UoF% / Population%) by troop and race.
Generates three separate heatmaps - one for each dataset.
Louisiana State Police (2022-2024)
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
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
RACES = ['Black', 'White', 'Hispanic', 'Asian/PI', 'Native']

# Race mapping for UoF data
race_mapping = {
    'Black': 'Black',
    'White': 'White',
    'Hispanic': 'Hispanic',
    'Asian': 'Asian/PI',
    'American Indian Or Alaska Native': 'Native',
}

def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df['citizen_race'] = df['citizen_race'].fillna('Unknown').str.title()
    return df

# Load census data
census_df = pd.read_csv(CENSUS_PATH)
census_df['troop'] = census_df['troop'].str.lower()
troops = sorted(census_df['troop'].unique())

# Load all UoF datasets
dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

def calc_troop_disparity(uof_df, census_df, troops):
    """Calculate disparity ratios by troop and race."""
    results = []

    for troop in troops:
        troop_census = census_df[census_df['troop'] == troop].iloc[0]
        troop_uof = uof_df[uof_df['department_desc'] == troop]

        total_pop = troop_census['total_16plus']
        total_uof = len(troop_uof)

        if total_uof == 0:
            # Add zeros for troops with no data
            for race in RACES:
                results.append({
                    'troop': troop.replace('troop ', '').upper(),
                    'race': race,
                    'disparity': np.nan,
                    'n': 0
                })
            continue

        troop_uof_race = troop_uof['citizen_race'].map(lambda x: race_mapping.get(x, x))
        uof_counts = troop_uof_race.value_counts()

        census_pop = {
            'Black': troop_census['black_16plus'],
            'White': troop_census['white_16plus'],
            'Hispanic': troop_census['hispanic_16plus'],
            'Asian/PI': troop_census['asian_pacific_islander_16plus'],
            'Native': troop_census['native_american_16plus'],
        }

        for race in RACES:
            pop = census_pop[race]
            uof = uof_counts.get(race, 0)

            pop_pct = (pop / total_pop * 100) if total_pop > 0 else 0
            uof_pct = (uof / total_uof * 100) if total_uof > 0 else 0
            disparity = (uof_pct / pop_pct) if pop_pct > 0 else 0

            results.append({
                'troop': troop.replace('troop ', '').upper(),
                'race': race,
                'disparity': disparity,
                'n': total_uof
            })

    return pd.DataFrame(results)

# Calculate disparities for each dataset
all_disparities = {name: calc_troop_disparity(df, census_df, troops) for name, df in dfs.items()}

# Print summary tables
print("=" * 120)
print("DISPARITY BY TROOP AND RACE — COMPARATIVE ANALYSIS")
print("Louisiana State Police (2022-2024)")
print("=" * 120)

for name, disp_df in all_disparities.items():
    pivot = disp_df.pivot(index='troop', columns='race', values='disparity')
    pivot = pivot[RACES]

    # Get n values
    n_by_troop = disp_df.groupby('troop')['n'].first()

    print(f"\n{name.upper()}")
    print("-" * 100)
    print(f"{'Troop':<12} {'n':>6} {'Black':>10} {'White':>10} {'Hispanic':>10} {'Asian/PI':>10} {'Native':>10}")
    print("-" * 100)

    for troop in pivot.index:
        n = n_by_troop[troop]
        vals = [f"{pivot.loc[troop, race]:.2f}x" if not np.isnan(pivot.loc[troop, race]) else 'N/A'
                for race in RACES]
        print(f"Troop {troop:<6} {n:>6} {vals[0]:>10} {vals[1]:>10} {vals[2]:>10} {vals[3]:>10} {vals[4]:>10}")

# Create visualization - Three heatmaps stacked vertically
fig, axes = plt.subplots(3, 1, figsize=(12, 16))

cmap = plt.cm.RdBu_r
norm = mcolors.TwoSlopeNorm(vmin=0, vcenter=1.0, vmax=3.0)

dataset_names = list(DATASETS.keys())
short_names = ['All Incidents', 'Pursuit-Only Excluded', 'All Pursuits Excluded']

for idx, (name, short_name) in enumerate(zip(dataset_names, short_names)):
    ax = axes[idx]
    disp_df = all_disparities[name]

    # Create pivot table
    pivot = disp_df.pivot(index='troop', columns='race', values='disparity')
    pivot = pivot[RACES]

    # Sort by Black disparity (descending) for consistent ordering
    pivot = pivot.sort_values('Black', ascending=False)

    # Get n values
    n_by_troop = disp_df.groupby('troop')['n'].first()

    # Get total n for this dataset
    total_n = dfs[name].shape[0]

    im = ax.imshow(pivot.values, cmap=cmap, norm=norm, aspect='auto')

    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.values[i, j]
            if np.isnan(value):
                ax.text(j, i, 'N/A', ha='center', va='center',
                       fontsize=9, fontweight='bold', color='gray')
            else:
                text_color = 'white' if value > 2.0 or value < 0.4 else 'black'
                ax.text(j, i, f'{value:.2f}x', ha='center', va='center',
                       fontsize=9, fontweight='bold', color=text_color)

    # Labels
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=10)
    ax.set_yticks(range(len(pivot.index)))

    # Include n in troop labels
    troop_labels = [f"Troop {t} (n={n_by_troop[t]})" for t in pivot.index]
    ax.set_yticklabels(troop_labels, fontsize=9)

    ax.set_xlabel('Citizen Race', fontsize=10, fontweight='bold', labelpad=8)
    ax.set_title(f'{short_name} (Total n={total_n:,})', fontsize=12, fontweight='bold', pad=10)

# Add shared colorbar
fig.subplots_adjust(right=0.88, hspace=0.25)
cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
cbar = fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=norm), cax=cbar_ax)
cbar.set_label('Disparity Ratio', fontsize=10)
cbar.ax.axhline(y=1.0, color='black', linewidth=1.5)
cbar.set_ticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
cbar.set_ticklabels(['0x', '0.5x', '1.0x', '1.5x', '2.0x', '2.5x', '3.0x'])

fig.suptitle('Disparity Ratio by Troop and Race — Comparative Analysis\n'
             'Louisiana State Police (2022-2024)',
             fontsize=14, fontweight='bold', y=0.98)

# Note
fig.text(0.5, 0.02,
         'Red = over-represented | Blue = under-represented | White = equal representation\n'
         'Disparity = UoF % ÷ Population %',
         ha='center', fontsize=9, style='italic')

plt.savefig(OUTPUT_DIR / 'compare_disparity_by_troop.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {OUTPUT_DIR / 'compare_disparity_by_troop.png'}")

# Also export CSV
csv_rows = []
for name in dataset_names:
    disp_df = all_disparities[name]
    pivot = disp_df.pivot(index='troop', columns='race', values='disparity')
    n_by_troop = disp_df.groupby('troop')['n'].first()

    for troop in pivot.index:
        row = {
            'Dataset': name,
            'Troop': f'Troop {troop}',
            'n': n_by_troop[troop]
        }
        for race in RACES:
            val = pivot.loc[troop, race]
            row[f'{race} Disparity'] = f"{val:.2f}" if not np.isnan(val) else 'N/A'
        csv_rows.append(row)

csv_df = pd.DataFrame(csv_rows)
csv_df.to_csv(OUTPUT_DIR / 'disparity_by_troop_comparison.csv', index=False)
print(f"CSV saved to: {OUTPUT_DIR / 'disparity_by_troop_comparison.csv'}")
