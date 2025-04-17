import pandas as pd

def first_non_null(series):
    non_null = series.dropna()
    if not non_null.empty:
        return non_null.iloc[0]
    return None

# Read the combined CSV file
df = pd.read_csv("polysim\\combined_data.csv")

# Group by the 'Economy' column and aggregate all other columns by taking the first non-null value
grouped_df = df.groupby("Economy", as_index=False).agg(first_non_null)

# Save the formatted DataFrame to a new CSV file
grouped_df.to_csv("polysim\\combined_data_formatted.csv", index=False)

print("Formatted combined CSV saved as polysim/combined_data_formatted.csv")