import pandas as pd

# List of file paths
file_paths = [
    "polysim\\processed_Mean age at first marriage.csv",
    "polysim\\processed_sexual violence in the last 12 months(% of ever-partnered women 15-49).csv",
    "polysim\\processed_There is legislation on sexual harassment in employment (1=yes; 0=no).csv",
    "polysim\\processed_Women and men have equal ownership rights to immovable property (1=yes; 0=no).csv",
    "polysim\\processed_Women making their own informed decisions regarding sexual relations, contraceptive use and reproductive health care  (% of women age 15-49).csv"
]

dfs = []
for path in file_paths:
    # Read each CSV file
    df = pd.read_csv(path)
    
    # Optionally, add a column to indicate the source file
    df['source_file'] = path
    dfs.append(df)

# Combine all dataframes, preserving all columns present in any file
combined_df = pd.concat(dfs, ignore_index=True, sort=False)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv("polysim\\combined_data.csv", index=False)

print("Combined CSV saved as polysim/combined_data.csv")