# Cleaning the json file as part of MRI-UP TDA (Tau) Project
# Goal: CSV file
import json
import csv
import pandas as pd
import re

# Load and initial processing

df = pd.read_json('fqhc_data.json')
df = df.applymap(lambda x: str(x).replace('\n', '').strip() if pd.notna(x) else x)
df.to_csv('fqhc_data.csv', index=False)

#print(df.info())

# Clean column names
#df = df.apply(lambda x: x.str.replace('"', '', regex=False) if x.dtype == "object" else x)
df.columns = df.columns.str.lower().str.replace('. sort ascending','').str.replace('. sort descending','').str.replace(' ', '_').str.replace('"','')
# Remove quotes from all columns
df = df.apply(lambda x: x.str.replace('"', '', regex=False).str.strip())
# renaming for sake of consistency
df = df.rename(columns={
    'health_center_site_population_type': 'population_type',
    'description_of_practice_site': 'site_type'
})

print(f"Total entries: {len(df)}")

# Drop the suite column as it doesn't have the same importance as street address, smae with site_name
df = df.drop(columns=['suite', 'site_name', 'population_type'])


#changing site_type to FQHC
fqhc_names = ['Federally Qualified Health Center (FQHC)', 'Federally Qualified Health Centers (FQHC)']
df['site_type'] = df['site_type'].apply(
    lambda x: next(('FQHC' for val in fqhc_names if val in x), x)
)

# Apply the pattern to the street_address column
print("Cleaning street addresses...")
'''df['street_address'] = df['street_address'].str.extract(
    r'^(.*?\b(?:St|Ave|Blvd|Rd|Ln|Dr|Ct|Pl|Cir|Way|Hwy)\b)', expand=False
)'''
df['street_address'] = df['street_address'].str.extract(
    r'^(.*?\b(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|(?:Dr(?!\s+[A-Z]))|Drive|Court|Ct|Place|Pl|Circle|Cir|Way|Highway|Hwy)(?=\s|$|,|\.|\d))', expand=False
)
#print(df['street_address'])
df['street_address'] = df['street_address'].str.replace(
    r'["\']|,\s*(?:Patient\s+Tower|Tower|Building\s+\w+|\d+(?:st|nd|rd|th)\s+Floor|First\s+Floor|Second\s+Floor)(?:\s*,\s*(?:Patient\s+Tower|Tower|Building\s+\w+|\d+(?:st|nd|rd|th)\s+Floor|First\s+Floor|Second\s+Floor))*',
    '', regex=True, flags=re.IGNORECASE
)

# Then continue with your address cleaning
df['street_address'] = df['street_address'].str.replace(
    r'^.*?(?:County\s+of\s+\w+\s+.*?Division\s+)',
    '', regex=True, flags=re.IGNORECASE
)
# Remove building/floor/room/suite info from street address
df['street_address'] = df['street_address'].str.replace(
    r',\s*(?:Patient\s+Tower|Tower|Building\s+\w+|\d+(?:st|nd|rd|th)\s+Floor|First\s+Floor|Second\s+Floor|Room\s+\w+|MS\s+\d+|Ward\s+\d+|[A-Z]\d+(?:\s*,\s*[A-Z]\d+)*|\d+(?:\s*,\s*\d+)*)(?:\s*,\s*(?:Patient\s+Tower|Tower|Building\s+\w+|\d+(?:st|nd|rd|th)\s+Floor|First\s+Floor|Second\s+Floor|Room\s+\w+|MS\s+\d+|Ward\s+\d+|[A-Z]\d+(?:\s*,\s*[A-Z]\d+)*|\d+(?:\s*,\s*\d+)*))*',
    '', regex=True, flags=re.IGNORECASE
)

# Standardize multiple unit numbers with consistent comma separation
df['street_address'] = df['street_address'].str.replace(
    r'([A-Z]\d+)\s+([A-Z]\d+)', 
    r'\1, \2', regex=True
)
#removing addresses with PO Box info, since most likely mailing address
po_box_pattern = r'(?:PO\s+Box|P\.O\.\s+Box|Post\s+Office\s+Box|POB)\s+\d+'
df = df[~df['street_address'].str.contains(po_box_pattern, case=False, na=False)]
directional = {
    r'\b(North|N)\b\.?': 'N',
    r'\b(South|S)\b\.?': 'S',
    r'\b(East|E)\b\.?': 'E',
    r'\b(West|W)\b\.?': 'W'
}
for pattern, replacement in directional.items():
    df['street_address'] = df['street_address'].str.replace(pattern, replacement, regex=True, flags=re.IGNORECASE)

street_types = {
    r'\b(?:Street|St)\b\.?\s*': 'St',
    r'\b(?:Boulevard|Blvd)\b\.?\s*(?!\s*\w)': 'Blvd',
    r'\b(?:Avenue|Ave)\b\.?\s*(?!\d)': 'Ave',
    r'\b(?:Road|Rd)\b\.?(?=\s+\d)': 'Rd',  
    r'\b(?:Road|Rd)\b\.?(?!\s+\d)': 'Rd',
    r'\b(?:Drive|Dr)\b\.?(?!\s*\w)': 'Dr',
    r'\b(?:Lane|Ln\.?)\s*\b': 'Ln',
    r'\b(?:Circle|Cir\.?)\b(?=\s*$|,|\d)': 'Cir',
    r'\b(?:Court|Ct\.?)\s*\b': 'Ct',
    r'\b(?:Place|Pl\.?)\s*\b': 'Pl',
    #r'\b(?:Highway|Hwy)\b\.?(?=\s*\d)': lambda m: f'Hwy {m.group(1)}',
    r'\b(?:Highway|Hwy)\b\.?(?!\s*\d)': 'Hwy',
    r'\b(?:First)\b\.?(?!\s*\d)': '1st',
    '\b(?:Jr\.?)\b': 'Jr'
}
df['street_address'] = df['street_address'].str.replace(
    r'\b(?:Highway|Hwy)\b\.?\s*(\d+)', 
    lambda m: f'Hwy {m.group(1)}', 
    regex=True, 
    flags=re.IGNORECASE
)
for pattern, replacement in street_types.items():
    df['street_address'] = df['street_address'].str.replace(pattern, replacement, regex=True, flags=re.IGNORECASE)

floor_pattern = r'(?:,\s*)?\d+(?:st|nd|rd|th)\s+Floor'
df['street_address'] = df['street_address'].str.replace(floor_pattern, '', regex=True)

# removing quotation marks from street_address
quote_pattern = r'^["\']|["\']$'
df['street_address'] = df['street_address'].str.replace(quote_pattern, '', regex=True)

# regex patterns of suite formats to remove from street_address
suite_pattern = r'(?:,\s*)?(?:Suite|Sutie|Ste|Unit|Apt|Bldg|Building|#)\.?\s*[\w\d\s&-]+(?=\s*(?:,|$)|\s*$)'
df['street_address'] = df['street_address'].apply(lambda x: re.sub(suite_pattern, '', str(x), flags=re.IGNORECASE) if pd.notna(x) else x)

# Show some examples of the cleaning
#print("\nSample of cleaned addresses:")

# Check for any remaining suite information (quality control)
print("\nChecking for remaining suite information...")
suite_check_patterns = [r'suite', r'ste', r'unit', r'apt', r'bldg', r'building', r'#\w+']
remaining_suites = []

for idx, address in df['street_address'].items():
    if pd.notna(address):
        for pattern in suite_check_patterns:
            if re.search(pattern, str(address), re.IGNORECASE):
                remaining_suites.append((idx, address))
                break

if remaining_suites:
    print(f"Found {len(remaining_suites)} addresses that may still contain suite information:")
    for idx, address in remaining_suites[:5]:  # Show first 5 examples
        print(f"Row {idx}: {address}")
else:
    print("No remaining suite information detected!")

# Handle smart deduplication - cases where records are identical except for population_type
print(f"\nBefore deduplication: {len(df)} entries")

# Define key columns that should be identical for true duplicates
key_columns = ['street_address', 'city', 'county', 'site_type']
# Check for potential duplicates based on key columns
potential_duplicates = df.groupby(key_columns).size()
duplicate_groups = potential_duplicates[potential_duplicates > 1]

# dropping the population type column

# de duplicate
if len(duplicate_groups) > 0:
    print(f"Found {len(duplicate_groups)} groups of potential duplicates")
    
    # Show examples of duplicate groups
    print("\nExamples of duplicate groups:")
    for group_keys, count in duplicate_groups.head(3).items():
        print(f"\nGroup with {count} records:")
        group_df = df[df[key_columns].apply(tuple, axis=1) == group_keys]
        print(group_df[key_columns].to_string(index=False))
    
    # Simple deduplication strategy
    def simple_deduplicate(group):
        """
        For duplicate groups, keep the first record
        """
        return group.iloc[[0]]
    
    # Apply simple deduplication
    df_deduplicated = df.groupby(key_columns, as_index=False).apply(simple_deduplicate).reset_index(drop=True)

else:
    print("No potential duplicates found based on key columns")
    df_deduplicated = df.drop_duplicates()

print(f"After smart deduplication: {len(df_deduplicated)} entries")
print(f"Removed {len(df) - len(df_deduplicated)} duplicate records")

# Save the cleaned data
df_deduplicated.to_csv('fqhc_data_cleaned.csv', index=False)
df_deduplicated.to_json('fqhc_data_cleaned.json', orient='records', indent=2)

print("\nCleaning complete! Files saved:")
print("- fqhc_data_cleaned.csv")
print("- fqhc_data_cleaned.json")

# Show final statistics
print(f"\nFinal dataset statistics:")
print(f"Total entries: {len(df_deduplicated)}")
print(f"Unique cities: {df_deduplicated['city'].nunique()}")
print(f"Unique counties: {df_deduplicated['county'].nunique()}")