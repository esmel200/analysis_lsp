# Louisiana State Police Use of Force Analysis

Analysis of use-of-force incidents by the Louisiana State Police (2022-2024), examining racial disparities relative to driving-age population demographics.

## Project Structure

```
analysis_lsp/
├── census/                    # Census demographic data collection
│   ├── src/                   # Scripts to pull Census API data
│   ├── input/                 # (empty - data pulled from API)
│   └── output/                # Troop-level demographics
│
├── interaction_analysis/      # Data preprocessing
│   ├── src/                   # Scripts to create analysis-ready datasets
│   ├── input/                 # Raw LSP use-of-force data
│   └── output/                # Processed citizen-level data
│
├── citizen_level_analysis/    # Analysis and visualization
│   ├── src/                   # Analysis and visualization scripts
│   ├── input/                 # Census + processed UoF data
│   └── output/                # Charts and figures
│
└── requirements.txt           # Python dependencies
```

## Data Pipeline

1. **Census Data** (`census/`): Pulls driving-age (16+) population by race for each LSP troop coverage area using the Census API.

2. **Preprocessing** (`interaction_analysis/`): Transforms raw incident data into citizen-level records, expanding multi-subject incidents.

3. **Analysis** (`citizen_level_analysis/`): Generates visualizations comparing use-of-force racial distributions against population demographics.

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Census API key (optional, only needed to regenerate census data)

Get a free API key at: https://api.census.gov/data/key_signup.html

```bash
export CENSUS_API_KEY=your_key_here
```

## Running the Analysis

Scripts should be run from the repository root directory.

### Generate census demographics (optional - output already included)

```bash
python census/src/lsp_census_demographics.py
```

### Create citizen-level dataset (optional - output already included)

```bash
python interaction_analysis/src/create_citizen_level_data.py
python interaction_analysis/src/create_citizen_officer_level_data.py
```

### Generate visualizations

```bash
python citizen_level_analysis/src/analyze_race_distribution_overall.py
python citizen_level_analysis/src/analyze_race_distribution_by_year.py
python citizen_level_analysis/src/analyze_race_population_normalized.py
python citizen_level_analysis/src/visualize_disparity_table.py
```

## Outputs

The analysis generates the following visualizations in `citizen_level_analysis/output/`:

- `citizen_race_distribution.png` - Overall race distribution of citizens in UoF incidents
- `citizen_race_by_year.png` - Race distribution by year (2022-2024)
- `citizen_race_population_normalized.png` - UoF rates normalized by population demographics
- `disparity_table.png` - Disparity ratios comparing UoF rates to population shares

## Data Sources

- **Use of Force Data**: Louisiana State Police public records (2022-2024)
- **Population Demographics**: U.S. Census Bureau American Community Survey 5-Year Estimates (2018-2022)
