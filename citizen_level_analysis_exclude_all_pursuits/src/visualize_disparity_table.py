"""
Simple heatmap table showing disparity ratios (UoF% / Population%) by troop and race.
Louisiana State Police (2022-2024)
FILTERED: All incidents containing Pursuit excluded
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Read the use of force data
uof_df = pd.read_csv('citizen_level_analysis_exclude_all_pursuits/input/uof_cit_louisiana_state_pd_2022_2024.csv')
uof_df['citizen_race'] = uof_df['citizen_race'].fillna('Unknown').str.title()

# Read the census demographics data
census_df = pd.read_csv('citizen_level_analysis_exclude_all_pursuits/input/lsp_troop_demographics_16plus.csv')
census_df['troop'] = census_df['troop'].str.lower()

# Race mapping
race_mapping = {
    'Black': 'Black',
    'White': 'White',
    'Hispanic': 'Hispanic',
    'Asian': 'Asian/PI',
    'American Indian Or Alaska Native': 'Native',
}

# Calculate disparity ratios for each troop
results = []
troops = sorted(census_df['troop'].unique())

for troop in troops:
    troop_census = census_df[census_df['troop'] == troop].iloc[0]
    troop_uof = uof_df[uof_df['department_desc'] == troop]

    total_pop = troop_census['total_16plus']
    total_uof = len(troop_uof)

    if total_uof == 0:
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

    for race in ['Black', 'White', 'Hispanic', 'Asian/PI', 'Native']:
        pop = census_pop[race]
        uof = uof_counts.get(race, 0)

        pop_pct = (pop / total_pop * 100) if total_pop > 0 else 0
        uof_pct = (uof / total_uof * 100) if total_uof > 0 else 0
        disparity = (uof_pct / pop_pct) if pop_pct > 0 else 0

        results.append({
            'troop': troop.replace('troop ', '').upper(),
            'race': race,
            'disparity': disparity,
        })

results_df = pd.DataFrame(results)

# Create pivot table
pivot = results_df.pivot(index='troop', columns='race', values='disparity')
pivot = pivot[['Black', 'White', 'Hispanic', 'Asian/PI', 'Native']]
pivot = pivot.sort_values('Black', ascending=False)

# Create figure (compact size)
fig, ax = plt.subplots(figsize=(8, 6))

# Diverging colormap centered at 1.0
cmap = plt.cm.RdBu_r
norm = mcolors.TwoSlopeNorm(vmin=0, vcenter=1.0, vmax=3.0)

im = ax.imshow(pivot.values, cmap=cmap, norm=norm, aspect='auto')

# Add text annotations
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        value = pivot.values[i, j]
        text_color = 'white' if value > 2.0 or value < 0.4 else 'black'
        ax.text(j, i, f'{value:.1f}x', ha='center', va='center',
                fontsize=9, fontweight='bold', color=text_color)

# Labels
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns, fontsize=10)
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels([f'Troop {t}' for t in pivot.index], fontsize=9)

ax.set_xlabel('Citizen Race', fontsize=10, fontweight='bold', labelpad=8)
ax.set_title('Disparity Ratio by Troop and Race (All Pursuit Excluded)\nUoF % ÷ Population % — Louisiana State Police 2022-2024',
             fontsize=11, fontweight='bold', pad=10)

# Colorbar
cbar = plt.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
cbar.set_label('Disparity Ratio', fontsize=9)
cbar.ax.axhline(y=1.0, color='black', linewidth=1.5)
cbar.set_ticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
cbar.set_ticklabels(['0x', '0.5x', '1.0x', '1.5x', '2.0x', '2.5x', '3.0x'], fontsize=8)

# Interpretation note
note = "Red = over-represented | Blue = under-represented | White = equal"
ax.text(0.5, -0.06, note, transform=ax.transAxes, ha='center', fontsize=8, style='italic')

plt.tight_layout()
plt.savefig('citizen_level_analysis_exclude_all_pursuits/output/disparity_table.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nChart saved to 'citizen_level_analysis_exclude_all_pursuits/output/disparity_table.png'")
