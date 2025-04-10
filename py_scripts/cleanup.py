import pandas as pd
import re

# Read the CSV file
df = pd.read_csv('csv-DBs\masterdb_updated.csv')

# Print original number of rows
original_count = len(df)
print(f"Original dataset contains {original_count} stories")

# Function to replace ending punctuation with ellipses
def replace_ending_punctuation(title):
    if pd.isna(title):
        return title
    
    # If title already ends with ellipses, keep it as is
    if title.endswith('...'):
        return title
    
    # Remove any existing punctuation at the end (.?!,;:) and add ellipses
    title = re.sub(r'[.?!,;:]$', '', title.strip())
    
    # If title doesn't already end with ellipses, add them
    if not title.endswith('...'):
        title = title + '...'
    
    return title

# # Apply the function to the Title column
# df['Title'] = df['Title'].apply(replace_ending_punctuation)

# Remove duplicates based on Story content
df_no_duplicates = df.drop_duplicates(subset=['Story'])

# Count removed duplicates
removed_count = original_count - len(df_no_duplicates)
print(f"Removed {removed_count} duplicate stories")

# Save to new file
df_no_duplicates.to_csv('stories_final.csv', index=False)

print(f"Successfully processed {len(df_no_duplicates)} stories and saved to 'stories_final.csv'")