"""
Grouped bar chart showing Use of Force incidents by citizen race over time.
Years displayed side-by-side for each race to enable easy trend comparison.
Louisiana State Police (2022-2024)
FILTERED: All incidents containing Pursuit excluded
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the use of force data
uof_df = pd.read_csv('citizen_level_analysis_exclude_all_pursuits/input/uof_cit_louisiana_state_pd_2022_2024.csv')
uof_df['citizen_race'] = uof_df['citizen_race'].fillna('Unknown').str.title()

# Standardize race labels
race_mapping = {
    'Black': 'Black',
    'White': 'White',
    'Hispanic': 'Hispanic',
    'Unknown': 'Unknown',
    'Asian': 'Asian',
    'American Indian Or Alaska Native': 'Native American'
}
uof_df['citizen_race'] = uof_df['citizen_race'].map(
    lambda x: race_mapping.get(x, x)
)

# Count incidents by year and race
yearly_counts = uof_df.groupby(['incident_year', 'citizen_race']).size().unstack(fill_value=0)

# Reorder columns by total count (descending)
col_order = yearly_counts.sum().sort_values(ascending=False).index
yearly_counts = yearly_counts[col_order]

# Get years and races
years = yearly_counts.index.tolist()
races = yearly_counts.columns.tolist()

# Calculate totals per year for percentage annotations
year_totals = yearly_counts.sum(axis=1)

# Set up the figure
fig, ax = plt.subplots(figsize=(14, 8))

# Define positions
x = np.arange(len(races))
width = 0.25  # Width of each bar
offsets = [-width, 0, width]  # Offset for each year

# Colors for each year (professional palette)
year_colors = {
    2022: '#2E86AB',  # Blue
    2023: '#A23B72',  # Magenta
    2024: '#F18F01'   # Orange
}

# Plot bars for each year
bars_by_year = {}
for i, year in enumerate(years):
    counts = yearly_counts.loc[year].values
    bars = ax.bar(x + offsets[i], counts, width,
                  label=str(year), color=year_colors[year],
                  edgecolor='white', linewidth=0.5)
    bars_by_year[year] = bars

    # Add value labels on top of bars
    for bar, count in zip(bars, counts):
        if count > 0:
            height = bar.get_height()
            pct = count / year_totals[year] * 100
            ax.annotate(f'{count}\n({pct:.1f}%)',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=8, fontweight='bold')

# Customize the chart
ax.set_xlabel('Citizen Race', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
ax.set_title('Use of Force Incidents by Citizen Race (All Pursuit Excluded) — Louisiana State Police\n'
             'Year-over-Year Comparison (2022-2024)',
             fontsize=14, fontweight='bold', pad=20)

# Set x-axis
ax.set_xticks(x)
ax.set_xticklabels(races, fontsize=11)

# Add gridlines for readability
ax.yaxis.grid(True, linestyle='--', alpha=0.3)
ax.set_axisbelow(True)

# Set y-axis to start at 0 with some headroom
ax.set_ylim(0, ax.get_ylim()[1] * 1.15)

# Add trend annotations for major categories
def get_trend_arrow(values):
    """Return trend indicator based on year-over-year changes."""
    if len(values) < 2:
        return ''
    changes = [values[i+1] - values[i] for i in range(len(values)-1)]
    if all(c > 0 for c in changes):
        return '↑'
    elif all(c < 0 for c in changes):
        return '↓'
    elif all(c == 0 for c in changes):
        return '→'
    else:
        return '~'

# Build trend summary text
summary_lines = []
for race in races[:4]:  # Top 4 categories
    values = [yearly_counts.loc[year, race] for year in years]
    change = values[-1] - values[0]
    pct_change = ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0
    arrow = get_trend_arrow(values)
    summary_lines.append(f"  {race}: {arrow} {change:+d} ({pct_change:+.1f}%)")

summary_text = "Trend (2022→2024):\n" + "\n".join(summary_lines)

# Add legend with year totals, then trend summary below it
legend_labels = [f'{year} (n={year_totals[year]})' for year in years]
handles = [bars_by_year[year][0] for year in years]
legend = ax.legend(handles, legend_labels, loc='upper right', fontsize=11,
                   title='Year (Total Incidents)', title_fontsize=11)

# Position trend summary box directly below the legend
ax.text(0.98, 0.58, summary_text, transform=ax.transAxes,
        fontsize=9, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9),
        family='monospace')

plt.tight_layout()
plt.savefig('citizen_level_analysis_exclude_all_pursuits/output/citizen_race_by_year.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nChart saved to 'citizen_level_analysis_exclude_all_pursuits/output/citizen_race_by_year.png'")

# Print detailed summary
print("\n" + "=" * 70)
print("DETAILED YEAR-OVER-YEAR SUMMARY")
print("=" * 70)
print(f"\n{'Race':<25} {'2022':>8} {'2023':>8} {'2024':>8} {'Change':>10}")
print("-" * 70)
for race in races:
    vals = [yearly_counts.loc[year, race] for year in years]
    change = vals[-1] - vals[0]
    print(f"{race:<25} {vals[0]:>8} {vals[1]:>8} {vals[2]:>8} {change:>+10}")
print("-" * 70)
totals = [year_totals[year] for year in years]
print(f"{'TOTAL':<25} {totals[0]:>8} {totals[1]:>8} {totals[2]:>8} {totals[2]-totals[0]:>+10}")
print("=" * 70)
