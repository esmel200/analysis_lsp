
"""
Louisiana State Police Troop Demographics Analysis
Pull Census data for driving-age population (16+) by race for each LSP troop coverage area
"""

import pandas as pd
import requests
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

# Census API Key - get yours free at: https://api.census.gov/data/key_signup.html
# Set as environment variable: export CENSUS_API_KEY=your_key_here
import os
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "YOUR_API_KEY_HERE")

# Louisiana FIPS code
STATE_FIPS = "22"

# ACS 5-year estimates (2018-2022) - most recent available
DATASET_YEAR = "2022"
DATASET = "acs/acs5"

# =============================================================================
# PARISH FIPS CODES (Louisiana parishes)
# =============================================================================

# Dictionary mapping parish names to their FIPS codes
PARISH_FIPS = {
    'Acadia': '001',
    'Allen': '003',
    'Ascension': '005',
    'Assumption': '007',
    'Avoyelles': '009',
    'Beauregard': '011',
    'Bienville': '013',
    'Bossier': '015',
    'Caddo': '017',
    'Calcasieu': '019',
    'Caldwell': '021',
    'Cameron': '023',
    'Catahoula': '025',
    'Claiborne': '027',
    'Concordia': '029',
    'De Soto': '031',
    'East Baton Rouge': '033',
    'East Carroll': '035',
    'East Feliciana': '037',
    'Evangeline': '039',
    'Franklin': '041',
    'Grant': '043',
    'Iberia': '045',
    'Iberville': '047',
    'Jackson': '049',
    'Jefferson': '051',
    'Jefferson Davis': '053',
    'Lafayette': '055',
    'Lafourche': '057',
    'LaSalle': '059',
    'Lincoln': '061',
    'Livingston': '063',
    'Madison': '065',
    'Morehouse': '067',
    'Natchitoches': '069',
    'Orleans': '071',
    'Ouachita': '073',
    'Plaquemines': '075',
    'Pointe Coupee': '077',
    'Rapides': '079',
    'Red River': '081',
    'Richland': '083',
    'Sabine': '085',
    'St. Bernard': '087',
    'St. Charles': '089',
    'St. Helena': '091',
    'St. James': '093',
    'St. John the Baptist': '095',
    'St. Landry': '097',
    'St. Martin': '099',
    'St. Mary': '101',
    'St. Tammany': '103',
    'Tangipahoa': '105',
    'Tensas': '107',
    'Terrebonne': '109',
    'Union': '111',
    'Vermilion': '113',
    'Vernon': '115',
    'Washington': '117',
    'Webster': '119',
    'West Baton Rouge': '121',
    'West Carroll': '123',
    'West Feliciana': '125',
    'Winn': '127'
}

# =============================================================================
# TROOP COVERAGE AREAS
# =============================================================================

TROOP_COVERAGE = {
    'Troop A': ['Ascension', 'East Baton Rouge', 'East Feliciana', 'Iberville', 
                'Livingston', 'Pointe Coupee', 'West Baton Rouge', 'West Feliciana',
                'St. James'],  # St. James split 50/50
    'Troop B': ['St. Charles', 'Plaquemines', 'St. Bernard', 'Jefferson',
                'St. John the Baptist'],  # St. John split 50/50
    'Troop C': ['Assumption', 'Lafourche', 'Terrebonne',
                'St. James', 'St. John the Baptist'],  # Both split 50/50
    'Troop D': ['Allen', 'Beauregard', 'Calcasieu', 'Cameron', 'Jefferson Davis'],
    'Troop E': ['Avoyelles', 'Catahoula', 'Concordia', 'Grant', 'LaSalle', 
                'Natchitoches', 'Rapides', 'Sabine', 'Vernon', 'Winn'],
    'Troop F': ['Union', 'West Carroll', 'East Carroll', 'Morehouse', 'Lincoln', 
                'Ouachita', 'Richland', 'Madison', 'Jackson', 'Caldwell', 'Tensas', 
                'Franklin'],
    'Troop G': ['Caddo', 'Bossier', 'De Soto', 'Webster', 'Claiborne', 'Bienville', 
                'Red River'],
    'Troop I': ['Evangeline', 'St. Landry', 'Acadia', 'Lafayette', 'St. Martin', 
                'Vermilion', 'Iberia', 'St. Mary'],
    'Troop L': ['St. Helena', 'St. Tammany', 'Tangipahoa', 'Washington'],
    'Troop NOLA': ['Orleans']
}

# Split parishes (50/50 allocation between troops)
SPLIT_PARISHES = ['St. James', 'St. John the Baptist']

# =============================================================================
# CENSUS TABLE DEFINITIONS
# =============================================================================

# We need age 16+ by race
# Using race-specific population tables with age breakdowns
# These tables give us detailed age ranges by race

# We need age 16+ by race
# Using race-specific population tables with age breakdowns
# These tables give us detailed age ranges by race

CENSUS_VARIABLES = {
    # For each race, we'll pull age groups and sum 16+
    # Format: B01001X_YYY where X is race code, YYY is age group
    
    # Race codes:
    # B (Black alone)
    # H (White alone, not Hispanic or Latino)
    # I (Hispanic or Latino)
    # C (American Indian and Alaska Native alone)
    # D (Asian alone)
    # E (Native Hawaiian and Pacific Islander alone)
    
    'black': [
        'B01001B_007E', 'B01001B_008E', 'B01001B_009E', 'B01001B_010E',
        'B01001B_011E', 'B01001B_012E', 'B01001B_013E', 'B01001B_014E',
        'B01001B_015E', 'B01001B_016E',  # Males 16+
        'B01001B_022E', 'B01001B_023E', 'B01001B_024E', 'B01001B_025E',
        'B01001B_026E', 'B01001B_027E', 'B01001B_028E', 'B01001B_029E',
        'B01001B_030E', 'B01001B_031E'   # Females 16+
    ],
    'white': [
        'B01001H_007E', 'B01001H_008E', 'B01001H_009E', 'B01001H_010E',
        'B01001H_011E', 'B01001H_012E', 'B01001H_013E', 'B01001H_014E',
        'B01001H_015E', 'B01001H_016E',  # Males 16+
        'B01001H_022E', 'B01001H_023E', 'B01001H_024E', 'B01001H_025E',
        'B01001H_026E', 'B01001H_027E', 'B01001H_028E', 'B01001H_029E',
        'B01001H_030E', 'B01001H_031E'   # Females 16+
    ],
    'hispanic': [
        'B01001I_007E', 'B01001I_008E', 'B01001I_009E', 'B01001I_010E',
        'B01001I_011E', 'B01001I_012E', 'B01001I_013E', 'B01001I_014E',
        'B01001I_015E', 'B01001I_016E',  # Males 16+
        'B01001I_022E', 'B01001I_023E', 'B01001I_024E', 'B01001I_025E',
        'B01001I_026E', 'B01001I_027E', 'B01001I_028E', 'B01001I_029E',
        'B01001I_030E', 'B01001I_031E'   # Females 16+
    ],
    'native_american': [
        'B01001C_007E', 'B01001C_008E', 'B01001C_009E', 'B01001C_010E',
        'B01001C_011E', 'B01001C_012E', 'B01001C_013E', 'B01001C_014E',
        'B01001C_015E', 'B01001C_016E',  # Males 16+
        'B01001C_022E', 'B01001C_023E', 'B01001C_024E', 'B01001C_025E',
        'B01001C_026E', 'B01001C_027E', 'B01001C_028E', 'B01001C_029E',
        'B01001C_030E', 'B01001C_031E'   # Females 16+
    ],
    'asian': [
        'B01001D_007E', 'B01001D_008E', 'B01001D_009E', 'B01001D_010E',
        'B01001D_011E', 'B01001D_012E', 'B01001D_013E', 'B01001D_014E',
        'B01001D_015E', 'B01001D_016E',  # Males 16+
        'B01001D_022E', 'B01001D_023E', 'B01001D_024E', 'B01001D_025E',
        'B01001D_026E', 'B01001D_027E', 'B01001D_028E', 'B01001D_029E',
        'B01001D_030E', 'B01001D_031E'   # Females 16+
    ],
    'pacific_islander': [
        'B01001E_007E', 'B01001E_008E', 'B01001E_009E', 'B01001E_010E',
        'B01001E_011E', 'B01001E_012E', 'B01001E_013E', 'B01001E_014E',
        'B01001E_015E', 'B01001E_016E',  # Males 16+
        'B01001E_022E', 'B01001E_023E', 'B01001E_024E', 'B01001E_025E',
        'B01001E_026E', 'B01001E_027E', 'B01001E_028E', 'B01001E_029E',
        'B01001E_030E', 'B01001E_031E'   # Females 16+
    ]
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def get_parish_demographics(api_key):
    """
    Pull demographics for all Louisiana parishes from Census API
    Returns DataFrame with parish-level data
    
    Note: Census API limits requests to 50 variables, so we make separate calls for each race
    """
    
    base_url = f"https://api.census.gov/data/{DATASET_YEAR}/{DATASET}"
    
    all_data = []
    
    print("Fetching data from Census API (one call per race category)...")
    
    # Make a separate API call for each race to stay under 50 variable limit
    for race_name, var_list in CENSUS_VARIABLES.items():
        print(f"  Fetching {race_name}...")
        
        variables = ','.join(['NAME'] + var_list)
        
        params = {
            'get': variables,
            'for': 'county:*',
            'in': f'state:{STATE_FIPS}',
            'key': api_key
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Census API error for {race_name}: {response.status_code}\n{response.text}")
        
        data = response.json()
        df_race = pd.DataFrame(data[1:], columns=data[0])
        
        # Calculate total for this race (sum all age group columns)
        # The API returns NAME, state, county automatically, plus our requested variables
        numeric_cols = [col for col in df_race.columns if col.startswith('B01001')]
        for col in numeric_cols:
            df_race[col] = pd.to_numeric(df_race[col], errors='coerce').fillna(0).astype(int)
        
        df_race[f'{race_name}_16plus'] = df_race[numeric_cols].sum(axis=1)
        
        # Keep only the essential columns
        df_race = df_race[['NAME', 'state', 'county', f'{race_name}_16plus']]
        
        all_data.append(df_race)
    
    # Merge all race dataframes
    print("  Combining race data...")
    result = all_data[0]
    for df in all_data[1:]:
        result = result.merge(df, on=['NAME', 'state', 'county'], how='outer')
    
    print(f"Successfully retrieved data for {len(result)} parishes")
    
    return result


def calculate_race_totals(df):
    """
    Prepare race totals data (already calculated during API fetch)
    Combine Asian and Pacific Islander categories
    """
    
    # Combine Asian and Pacific Islander to match your use of force categories
    df['asian_pacific_islander_16plus'] = (
        df['asian_16plus'] + df['pacific_islander_16plus']
    )
    
    # Extract clean parish name
    df['parish_name'] = df['NAME'].str.replace(' Parish, Louisiana', '').str.strip()
    
    # Keep only relevant columns
    result_cols = ['NAME', 'state', 'county', 'parish_name',
                   'black_16plus', 'white_16plus', 'hispanic_16plus', 
                   'native_american_16plus', 'asian_pacific_islander_16plus']
    
    return df[result_cols]


def aggregate_troop_demographics(parish_df):
    """
    Aggregate parish demographics to troop level
    Handles 50/50 split for St. James and St. John the Baptist
    """
    
    troop_demographics = []
    
    for troop, parishes in TROOP_COVERAGE.items():
        troop_data = {
            'troop': troop,
            'black_16plus': 0,
            'white_16plus': 0,
            'hispanic_16plus': 0,
            'native_american_16plus': 0,
            'asian_pacific_islander_16plus': 0
        }
        
        for parish in parishes:
            parish_row = parish_df[parish_df['parish_name'] == parish]
            
            if len(parish_row) == 0:
                print(f"WARNING: No data found for {parish}")
                continue
            
            # If split parish, use 50% of population
            multiplier = 0.5 if parish in SPLIT_PARISHES else 1.0
            
            troop_data['black_16plus'] += int(parish_row['black_16plus'].values[0] * multiplier)
            troop_data['white_16plus'] += int(parish_row['white_16plus'].values[0] * multiplier)
            troop_data['hispanic_16plus'] += int(parish_row['hispanic_16plus'].values[0] * multiplier)
            troop_data['native_american_16plus'] += int(parish_row['native_american_16plus'].values[0] * multiplier)
            troop_data['asian_pacific_islander_16plus'] += int(parish_row['asian_pacific_islander_16plus'].values[0] * multiplier)
        
        troop_demographics.append(troop_data)
    
    return pd.DataFrame(troop_demographics)


def calculate_percentages(troop_df):
    """
    Calculate percentage distribution of each race within each troop
    """
    
    # Calculate total 16+ population for each troop
    troop_df['total_16plus'] = (
        troop_df['black_16plus'] + 
        troop_df['white_16plus'] + 
        troop_df['hispanic_16plus'] + 
        troop_df['native_american_16plus'] + 
        troop_df['asian_pacific_islander_16plus']
    )
    
    # Calculate percentages
    troop_df['black_pct'] = (troop_df['black_16plus'] / troop_df['total_16plus'] * 100).round(1)
    troop_df['white_pct'] = (troop_df['white_16plus'] / troop_df['total_16plus'] * 100).round(1)
    troop_df['hispanic_pct'] = (troop_df['hispanic_16plus'] / troop_df['total_16plus'] * 100).round(1)
    troop_df['native_american_pct'] = (troop_df['native_american_16plus'] / troop_df['total_16plus'] * 100).round(1)
    troop_df['asian_pacific_islander_pct'] = (troop_df['asian_pacific_islander_16plus'] / troop_df['total_16plus'] * 100).round(1)
    
    return troop_df


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function to run the analysis
    """
    
    if CENSUS_API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace 'YOUR_API_KEY_HERE' with your actual Census API key")
        return
    
    # Step 1: Get parish-level data
    parish_df = get_parish_demographics(CENSUS_API_KEY)
    
    # Step 2: Calculate race totals from age groups
    parish_df = calculate_race_totals(parish_df)
    
    # Step 3: Aggregate to troop level
    troop_df = aggregate_troop_demographics(parish_df)
    
    # Step 4: Calculate percentages
    troop_df = calculate_percentages(troop_df)
    
    # Step 5: Display results
    print("\n" + "="*80)
    print("LSP TROOP DEMOGRAPHICS - DRIVING AGE POPULATION (16+) BY RACE")
    print("="*80 + "\n")
    
    # Show percentage distribution
    pct_cols = ['troop', 'black_pct', 'white_pct', 'hispanic_pct', 
                'native_american_pct', 'asian_pacific_islander_pct', 'total_16plus']
    
    display_df = troop_df[pct_cols].copy()
    display_df.columns = ['Troop', 'Black %', 'White %', 'Hispanic %', 
                          'Native American %', 'Asian/PI %', 'Total Pop 16+']
    
    print(display_df.to_string(index=False))
    
    # Save to CSV
    output_file = 'lsp_troop_demographics_16plus.csv'
    troop_df.to_csv(output_file, index=False)
    print(f"\n\nFull results saved to: {output_file}")
    
    return troop_df


if __name__ == "__main__":
    results = main()