import pandas as pd
import re

def remove_non_ascii(text):
    """Remove non-ASCII characters from a text string."""
    if isinstance(text, str):
        # This regex removes any character that is not in the ASCII range
        return re.sub(r'[^\x00-\x7F]+', '', text)
    return text

CSV_FILENAME = 'masterdb - Copy.csv'
OUTPUT_FILENAME = 'masterdb_cleaned.csv'

try:
    # Read the file with an encoding that can handle non-UTF8 characters (e.g., cp1252)
    df = pd.read_csv(CSV_FILENAME, encoding='cp1252')
except Exception as e:
    print(f"Error reading the CSV file: {e}")
    exit()

# Clean all string columns to remove non-ASCII characters
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].apply(remove_non_ascii)

try:
    # Write the cleaned DataFrame to a CSV using UTF-8 encoding.
    df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8')
    print(f"Cleaned CSV file written to {OUTPUT_FILENAME}")
except Exception as e:
    print(f"Error writing CSV file: {e}")
