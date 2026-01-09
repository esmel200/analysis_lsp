"""
Create a comprehensive summary table comparing disparity metrics across all three datasets.
Shows disparity ratios for ALL race categories for each dataset.
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

# All race categories
RACES = ['Black', 'White', 'Hispanic', 'Asian/PI', 'Native American']

def load_and_process(filepath):
    df = pd.read_csv(filepath)
    df['citizen_race'] = df['citizen_race'].fillna('Unknown').str.title()
    race_mapping = {
        'American Indian Or Alaska Native': 'Native American',
        'Asian': 'Asian/PI',
    }
    df['citizen_race'] = df['citizen_race'].replace(race_mapping)
    return df

# Load census data
census_df = pd.read_csv(CENSUS_PATH)
total_pop = census_df['total_16plus'].sum()

# Population percentages for each race
pop_pct = {
    'Black': census_df['black_16plus'].sum() / total_pop * 100,
    'White': census_df['white_16plus'].sum() / total_pop * 100,
    'Hispanic': census_df['hispanic_16plus'].sum() / total_pop * 100,
    'Asian/PI': census_df['asian_pacific_islander_16plus'].sum() / total_pop * 100,
    'Native American': census_df['native_american_16plus'].sum() / total_pop * 100,
}

# Load all datasets
dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

# Calculate metrics for each dataset and race
def calc_metrics(df, total_pop_pct):
    total = len(df)
    counts = df['citizen_race'].value_counts()

    results = {}
    for race in RACES:
        count = counts.get(race, 0)
        uof_pct = count / total * 100 if total > 0 else 0
        disparity = uof_pct / total_pop_pct[race] if total_pop_pct[race] > 0 else 0
        results[race] = {
            'count': count,
            'pct': uof_pct,
            'disparity': disparity
        }

    # Add Unknown
    unknown_count = counts.get('Unknown', 0)
    results['Unknown'] = {
        'count': unknown_count,
        'pct': unknown_count / total * 100 if total > 0 else 0,
        'disparity': None  # No population comparison for Unknown
    }

    results['total'] = total
    return results

# Calculate for all datasets
all_metrics = {name: calc_metrics(df, pop_pct) for name, df in dfs.items()}

# Print detailed tables
print("=" * 120)
print("COMPREHENSIVE DISPARITY ANALYSIS — ALL RACE CATEGORIES")
print("Louisiana State Police (2022-2024)")
print("=" * 120)

print(f"\nLouisiana Population (16+): {total_pop:,}")
print("\nPopulation Distribution:")
for race in RACES:
    print(f"  {race}: {pop_pct[race]:.1f}%")

# Print table for each dataset
for dataset_name, metrics in all_metrics.items():
    print("\n" + "=" * 120)
    print(f"{dataset_name.upper()} (n={metrics['total']:,})")
    print("=" * 120)
    print(f"{'Race':<20} {'Count':>10} {'UoF %':>12} {'Population %':>15} {'Disparity':>12}")
    print("-" * 70)

    for race in RACES + ['Unknown']:
        m = metrics[race]
        pop = f"{pop_pct.get(race, 0):.1f}%" if race != 'Unknown' else 'N/A'
        disp = f"{m['disparity']:.2f}x" if m['disparity'] is not None else 'N/A'
        print(f"{race:<20} {m['count']:>10} {m['pct']:>11.1f}% {pop:>15} {disp:>12}")

# Create visualization - Three separate tables (one per dataset) showing all races
fig, axes = plt.subplots(3, 1, figsize=(12, 14))

dataset_names = list(DATASETS.keys())
short_names = ['All Incidents', 'Pursuit-Only Excluded', 'All Pursuits Excluded']

cmap = plt.cm.RdBu_r
norm = mcolors.TwoSlopeNorm(vmin=0, vcenter=1.0, vmax=3.0)

for idx, (name, short_name) in enumerate(zip(dataset_names, short_names)):
    ax = axes[idx]
    metrics = all_metrics[name]

    # Build table data
    col_labels = ['Race', 'Count', 'UoF %', 'Pop %', 'Disparity']
    table_data = []
    cell_colors = []

    # Use shorter race labels
    race_labels = {
        'Black': 'Black',
        'White': 'White',
        'Hispanic': 'Hispanic',
        'Asian/PI': 'Asian/PI',
        'Native American': 'Native Amer.',
        'Unknown': 'Unknown'
    }

    for race in RACES + ['Unknown']:
        m = metrics[race]
        pop = f"{pop_pct.get(race, 0):.1f}%" if race != 'Unknown' else 'N/A'
        disp = f"{m['disparity']:.2f}x" if m['disparity'] is not None else 'N/A'

        table_data.append([race_labels[race], f"{m['count']:,}", f"{m['pct']:.1f}%", pop, disp])

        # Color based on disparity
        if m['disparity'] is not None:
            # Normalize disparity to color
            color_val = norm(m['disparity'])
            rgba = cmap(color_val)
            cell_colors.append(['white', 'white', 'white', 'white', rgba])
        else:
            cell_colors.append(['white', 'white', 'white', 'white', '#E8E8E8'])

    ax.axis('off')

    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
        cellColours=cell_colors,
        colColours=['#D0D0D0'] * 5
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.4, 2.2)

    # Set column widths
    for j, width in enumerate([0.18, 0.12, 0.12, 0.12, 0.14]):
        for i in range(len(table_data) + 1):
            table[(i, j)].set_width(width)

    # Style header
    for j in range(5):
        table[(0, j)].set_text_props(fontweight='bold')

    # Style race column
    for i in range(1, len(table_data) + 1):
        table[(i, 0)].set_text_props(fontweight='bold')

    ax.set_title(f'{short_name} (n={metrics["total"]:,})', fontsize=14, fontweight='bold', pad=15)

fig.suptitle('Disparity Ratios by Race — Comparative Analysis\n'
             'Louisiana State Police (2022-2024)',
             fontsize=16, fontweight='bold', y=0.97)

# Add colorbar legend on the right
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('Disparity Ratio', fontsize=11)
cbar.ax.axhline(y=1.0, color='black', linewidth=1.5)
cbar.set_ticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
cbar.set_ticklabels(['0x', '0.5x', '1.0x', '1.5x', '2.0x', '2.5x', '3.0x'])

# Note
fig.text(0.44, 0.02,
         'Disparity = UoF % ÷ Population %  |  Red = over-represented  |  Blue = under-represented  |  White = equal',
         ha='center', fontsize=10, style='italic')

plt.subplots_adjust(left=0.1, right=0.85, top=0.90, bottom=0.06, hspace=0.35)

plt.savefig(OUTPUT_DIR / 'compare_disparity_table.png', dpi=300, bbox_inches='tight')
print(f"\nVisualization saved to: {OUTPUT_DIR / 'compare_disparity_table.png'}")

# Also export as CSV for easy doc formatting
csv_data = []
for race in RACES + ['Unknown']:
    row = {'Race': race, 'Population %': f"{pop_pct.get(race, 0):.1f}" if race != 'Unknown' else 'N/A'}
    for name in dataset_names:
        m = all_metrics[name][race]
        row[f'{name} Count'] = m['count']
        row[f'{name} %'] = f"{m['pct']:.1f}"
        row[f'{name} Disparity'] = f"{m['disparity']:.2f}" if m['disparity'] is not None else 'N/A'
    csv_data.append(row)

csv_df = pd.DataFrame(csv_data)
csv_df.to_csv(OUTPUT_DIR / 'disparity_comparison_all_races.csv', index=False)
print(f"CSV table saved to: {OUTPUT_DIR / 'disparity_comparison_all_races.csv'}")
