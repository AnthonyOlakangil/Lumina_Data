import pandas as pd

# Read CSV file (adjust the full path if necessary)
df = pd.read_csv("polysim/sexual violence in the last 12 months (% of ever-partnered women ages 15-49).csv")

# Drop rows that do not have a value in the fourth column (zero-indexed column 3)
df = df.dropna(subset=[df.columns[3]])

# Drop the fifth column entirely (zero-indexed column 4)
df = df.drop(columns=[df.columns[4]])

# Save the cleaned DataFrame to a new CSV file
df.to_csv("polysim/processed_sexual violence in the last 12 months(% of ever-partnered women 15-49).csv", index=False)

print("Cleaned CSV saved as polysim/cleaned_sexual_violence.csv")