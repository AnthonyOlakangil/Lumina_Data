import pandas as pd

# Read CSV file (adjust the full path if necessary)
df = pd.read_csv("polysim\Women making their own informed decisions regarding sexual relations, contraceptive use and reproductive health care  (% of women age 15-49).csv")

# Drop rows that do not have a value in the fourth column (zero-indexed column 3)
df = df.dropna(subset=[df.columns[3]])

# Save the cleaned DataFrame to a new CSV file
df.to_csv("polysim\processed_Women making their own informed decisions regarding sexual relations, contraceptive use and reproductive health care  (% of women age 15-49).csv", index=False)

print("Cleaned CSV saved as polysim/cleaned_sexual_violence.csv")

