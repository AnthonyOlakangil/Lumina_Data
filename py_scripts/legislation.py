import pandas as pd

# Load the datasets
df1 = pd.read_csv('polysim\combined_data_formatted.csv')
df2 = pd.read_csv('polysim\list of laws - Data Table-export.csv')

# Identify the relevant columns in the laws dataset
description_col = df2.columns[4]  # 5th column: description
title_col = df2.columns[6]        # 7th column: title
country_col_laws = 'Country'      # Country column in the laws file

# Build a mapping from country to concatenated law entries
law_mapping = (
    df2.groupby(country_col_laws)
       .apply(lambda grp: ''.join(f"{row[title_col]}: {row[description_col]}\n\n"
                                  for _, row in grp.iterrows()))
       .to_dict()
)

# Create a new column 'legislation' in the first dataset
df1['legislation'] = df1['Economy'].map(law_mapping).fillna('')

# Save the updated DataFrame to a new CSV
output_path = 'polysim\combined_data_with_laws.csv'
df1.to_csv(output_path, index=False)


# Provide download link
print(f"[Download the updated CSV file here]({output_path})")
