import pandas as pd

# Read the scraped data and the formatted combined data
naps_df = pd.read_csv("polysim\\cleaned_scraped_naps.xlsx - Sheet1.csv")
formatted_df = pd.read_csv("polysim\\combined_data_formatted.csv")

# Merge the two DataFrames based on country (Economy from formatted_df and Country from naps_df)
merged_df = pd.merge(formatted_df, naps_df, left_on="Economy", right_on="Country", how="left")

# Optional: Remove duplicate country column if present
if "Country" in merged_df.columns:
    merged_df.drop("Country", axis=1, inplace=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv("polysim\\final_combined_data.csv", index=False)

print("Final merged CSV saved as polysim/final_combined_data.csv")