import pandas as pd

# Read the CSV file (adjust the path as needed)
df = pd.read_csv("polysim\Mean age at first marriage.csv")

# Drop rows that do not have a value in the fourth column.
# Assuming the CSV has a header row, column 4 corresponds to df.columns[3]
df = df.dropna(subset=[df.columns[3]])

# Drop columns 2, 3, and 5 (assuming one-based numbering; these correspond to df.columns[1], df.columns[2], df.columns[4])
df = df.drop(columns=[df.columns[1], df.columns[2], df.columns[4]])

# Save the processed DataFrame to a new CSV file.
df.to_csv("polysim/processed_Mean age at first marriage.csv", index=False)

print("Data processing complete. Processed file saved as polysim/processed_Mean age at first marriage.csv")