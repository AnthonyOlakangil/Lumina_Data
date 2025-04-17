import pandas as pd

# Read CSV file (adjust the full path if necessary)
df = pd.read_csv("polysim\Women and men have equal ownership rights to immovable property (1=yes; 0=no).csv")

# Keep rows where the value in column 5 (zero-indexed column 4) is 2023; drop others
df = df[df[df.columns[4]] == 2023]

# Save the cleaned DataFrame to a new CSV file
df.to_csv("polysim\processed_Women and men have equal ownership rights to immovable property (1=yes; 0=no).csv", index=False)

print("Cleaned CSV saved as polysim/processed_There is legislation on sexual harassment in employment (1=yes; 0=no).csv")