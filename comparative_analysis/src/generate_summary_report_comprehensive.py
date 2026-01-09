"""
Generate a comprehensive summary visualization with ALL race categories.
Creates a dashboard showing metrics for every race across all three datasets.
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

# Load data
census_df = pd.read_csv(CENSUS_PATH)
total_pop = census_df['total_16plus'].sum()

# Population percentages
pop_pct = {
    'Black': census_df['black_16plus'].sum() / total_pop * 100,
    'White': census_df['white_16plus'].sum() / total_pop * 100,
    'Hispanic': census_df['hispanic_16plus'].sum() / total_pop * 100,
    'Asian/PI': census_df['asian_pacific_islander_16plus'].sum() / total_pop * 100,
    'Native American': census_df['native_american_16plus'].sum() / total_pop * 100,
}

dfs = {name: load_and_process(path) for name, path in DATASETS.items()}

# Calculate metrics for all races
def calc_all_metrics(df, pop_pcts):
    total = len(df)
    counts = df['citizen_race'].value_counts()

    results = {'total': total}
    for race in RACES + ['Unknown']:
        count = counts.get(race, 0)
        pct = count / total * 100 if total > 0 else 0
        if race in pop_pcts and pop_pcts[race] > 0:
            disparity = pct / pop_pcts[race]
        else:
            disparity = None
        results[race] = {
            'count': count,
            'pct': pct,
            'disparity': disparity
        }
    return results

all_metrics = {name: calc_all_metrics(df, pop_pct) for name, df in dfs.items()}

# Create dashboard figure
fig = plt.figure(figsize=(18, 16))

# Define grid: 4 rows
gs = fig.add_gridspec(4, 2, height_ratios=[0.8, 1.2, 1.2, 1.0], hspace=0.35, wspace=0.25)

# Colors
dataset_colors = ['#2E86AB', '#A23B72', '#F18F01']
dataset_names = list(DATASETS.keys())
dataset_labels = ['All Incidents', 'Pursuit-Only\nExcluded', 'All Pursuits\nExcluded']

# ============================================
# Panel 1: Total incidents (top left)
# ============================================
ax1 = fig.add_subplot(gs[0, 0])
totals = [all_metrics[name]['total'] for name in dataset_names]
bars1 = ax1.bar(dataset_labels, totals, color=dataset_colors, edgecolor='black', linewidth=1.2)
ax1.set_ylabel('Number of Incidents', fontsize=11, fontweight='bold')
ax1.set_title('Total Use of Force Incidents', fontsize=12, fontweight='bold')
for bar, val in zip(bars1, totals):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
             f'{val:,}', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax1.set_ylim(0, max(totals) * 1.15)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================
# Panel 2: Records removed info (top right)
# ============================================
ax2 = fig.add_subplot(gs[0, 1])
ax2.axis('off')

removed_pursuit_only = totals[0] - totals[1]
removed_all_pursuit = totals[0] - totals[2]

info_text = (
    f"Louisiana Population (16+): {total_pop:,}\n\n"
    f"Records Removed:\n"
    f"  Pursuit-only excluded: {removed_pursuit_only:,} ({removed_pursuit_only/totals[0]*100:.1f}%)\n"
    f"  All pursuits excluded: {removed_all_pursuit:,} ({removed_all_pursuit/totals[0]*100:.1f}%)\n\n"
    f"Population by Race:\n"
)
for race in RACES:
    info_text += f"  {race}: {pop_pct[race]:.1f}%\n"

ax2.text(0.1, 0.95, info_text, transform=ax2.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))

# ============================================
# Panel 3: UoF Percentage by Race (middle left)
# ============================================
ax3 = fig.add_subplot(gs[1, 0])
x = np.arange(len(RACES))
width = 0.22

# Population bars
pop_vals = [pop_pct[race] for race in RACES]
ax3.bar(x - 1.5*width, pop_vals, width, label='Population', color='#B8B8B8', edgecolor='black')

# UoF bars for each dataset
for idx, name in enumerate(dataset_names):
    uof_vals = [all_metrics[name][race]['pct'] for race in RACES]
    ax3.bar(x + (idx - 0.5)*width, uof_vals, width, label=dataset_labels[idx].replace('\n', ' '),
            color=dataset_colors[idx], edgecolor='black', linewidth=0.5)

ax3.set_xlabel('Race', fontsize=11, fontweight='bold')
ax3.set_ylabel('Percentage', fontsize=11, fontweight='bold')
ax3.set_title('UoF % vs Population % by Race', fontsize=12, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(RACES, fontsize=10)
ax3.legend(fontsize=8, loc='upper right')
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================
# Panel 4: Disparity Ratios by Race (middle right)
# ============================================
ax4 = fig.add_subplot(gs[1, 1])
x = np.arange(len(RACES))
width = 0.25

for idx, name in enumerate(dataset_names):
    disp_vals = [all_metrics[name][race]['disparity'] or 0 for race in RACES]
    bars = ax4.bar(x + (idx - 1)*width, disp_vals, width, label=dataset_labels[idx].replace('\n', ' '),
                   color=dataset_colors[idx], edgecolor='black', linewidth=0.5)

ax4.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='Equal representation')
ax4.set_xlabel('Race', fontsize=11, fontweight='bold')
ax4.set_ylabel('Disparity Ratio', fontsize=11, fontweight='bold')
ax4.set_title('Disparity Ratios by Race (UoF % ÷ Population %)', fontsize=12, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(RACES, fontsize=10)
ax4.legend(fontsize=8, loc='upper right')
ax4.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================
# Panel 5: Counts by Race (lower left)
# ============================================
ax5 = fig.add_subplot(gs[2, 0])
x = np.arange(len(RACES) + 1)  # Include Unknown
all_races = RACES + ['Unknown']
width = 0.25

for idx, name in enumerate(dataset_names):
    count_vals = [all_metrics[name][race]['count'] for race in all_races]
    ax5.bar(x + (idx - 1)*width, count_vals, width, label=dataset_labels[idx].replace('\n', ' '),
            color=dataset_colors[idx], edgecolor='black', linewidth=0.5)

ax5.set_xlabel('Race', fontsize=11, fontweight='bold')
ax5.set_ylabel('Number of Incidents', fontsize=11, fontweight='bold')
ax5.set_title('Incident Counts by Race', fontsize=12, fontweight='bold')
ax5.set_xticks(x)
ax5.set_xticklabels(all_races, fontsize=10, rotation=15, ha='right')
ax5.legend(fontsize=8, loc='upper right')
ax5.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================
# Panel 6: Unknown % comparison (lower right)
# ============================================
ax6 = fig.add_subplot(gs[2, 1])
unknown_pcts = [all_metrics[name]['Unknown']['pct'] for name in dataset_names]
bars6 = ax6.bar(dataset_labels, unknown_pcts, color=dataset_colors, edgecolor='black', linewidth=1.2)
ax6.set_ylabel('Percentage', fontsize=11, fontweight='bold')
ax6.set_title('Unknown Race % by Dataset', fontsize=12, fontweight='bold')
for bar, val in zip(bars6, unknown_pcts):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
ax6.set_ylim(0, max(unknown_pcts) * 1.3)
ax6.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================
# Panel 7: Full Summary Table (bottom)
# ============================================
ax7 = fig.add_subplot(gs[3, :])
ax7.axis('off')

# Build comprehensive table
col_labels = ['Race', 'Pop %',
              'All: Count', 'All: %', 'All: Disp',
              'No Pursuit-Only: Count', 'No Pursuit-Only: %', 'No Pursuit-Only: Disp',
              'No Pursuits: Count', 'No Pursuits: %', 'No Pursuits: Disp']

table_data = []
for race in RACES + ['Unknown']:
    pop = f"{pop_pct.get(race, 0):.1f}%" if race != 'Unknown' else 'N/A'
    row = [race, pop]

    for name in dataset_names:
        m = all_metrics[name][race]
        row.append(f"{m['count']:,}")
        row.append(f"{m['pct']:.1f}%")
        row.append(f"{m['disparity']:.2f}x" if m['disparity'] is not None else 'N/A')

    table_data.append(row)

# Add totals row
totals_row = ['TOTAL', '100%']
for name in dataset_names:
    totals_row.append(f"{all_metrics[name]['total']:,}")
    totals_row.append('100%')
    totals_row.append('-')
table_data.append(totals_row)

# Color cells based on disparity
cmap = plt.cm.RdBu_r
norm = mcolors.TwoSlopeNorm(vmin=0, vcenter=1.0, vmax=3.0)

cell_colors = []
for i, race in enumerate(RACES + ['Unknown', 'TOTAL']):
    row_colors = ['white', 'white']  # Race and Pop columns
    for name in dataset_names:
        row_colors.extend(['white', 'white'])  # Count and % columns
        if race in RACES:
            disp = all_metrics[name][race]['disparity']
            if disp is not None:
                rgba = cmap(norm(disp))
                row_colors.append(rgba)
            else:
                row_colors.append('#E8E8E8')
        else:
            row_colors.append('#E8E8E8')
    cell_colors.append(row_colors)

table = ax7.table(
    cellText=table_data,
    colLabels=col_labels,
    cellLoc='center',
    loc='center',
    cellColours=cell_colors,
    colColours=['#D0D0D0'] * len(col_labels)
)

table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.0, 1.8)

# Style header and first column
for j in range(len(col_labels)):
    table[(0, j)].set_text_props(fontweight='bold', fontsize=8)
for i in range(1, len(table_data) + 1):
    table[(i, 0)].set_text_props(fontweight='bold')

# Style totals row
for j in range(len(col_labels)):
    table[(len(table_data), j)].set_facecolor('#E0E0E0')
    table[(len(table_data), j)].set_text_props(fontweight='bold')

fig.suptitle('Louisiana State Police Use of Force Analysis\n'
             'Comprehensive Summary (2022-2024)',
             fontsize=16, fontweight='bold', y=0.98)

# Footer note
fig.text(0.5, 0.01,
         'Disparity = UoF % ÷ Population %  |  >1.0x = over-represented (red)  |  <1.0x = under-represented (blue)  |  Population based on LA Census 16+',
         ha='center', fontsize=9, style='italic')

plt.savefig(OUTPUT_DIR / 'summary_dashboard_comprehensive.png', dpi=300, bbox_inches='tight')
print(f"Summary dashboard saved to: {OUTPUT_DIR / 'summary_dashboard_comprehensive.png'}")

# Print text summary
print("\n" + "=" * 120)
print("COMPREHENSIVE SUMMARY — ALL RACES")
print("=" * 120)

for name in dataset_names:
    metrics = all_metrics[name]
    print(f"\n{name.upper()} (n={metrics['total']:,})")
    print("-" * 80)
    print(f"{'Race':<18} {'Count':>8} {'UoF %':>10} {'Pop %':>10} {'Disparity':>12}")
    print("-" * 80)
    for race in RACES + ['Unknown']:
        m = metrics[race]
        pop = f"{pop_pct.get(race, 0):.1f}%" if race != 'Unknown' else 'N/A'
        disp = f"{m['disparity']:.2f}x" if m['disparity'] is not None else 'N/A'
        print(f"{race:<18} {m['count']:>8} {m['pct']:>9.1f}% {pop:>10} {disp:>12}")
