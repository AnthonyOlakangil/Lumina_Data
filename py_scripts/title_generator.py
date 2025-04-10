# Inequality Story Title Generator (Local Version with GPT-4 API)

# Install required libraries (make sure to do this in your local environment)
# pip install openai pandas

import pandas as pd
import openai
import ast
import os

# 🔑 Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") 

# Load your dataset (replace with your actual file path)
filename = "stories_with_themes.csv"
df = pd.read_csv(filename)

# Function to generate a powerful 6-10 word title using GPT-4 (OpenAI >= 1.0.0)
def generate_title(row):
    themes = ', '.join(ast.literal_eval(row['Themes'])) if isinstance(row['Themes'], str) else row['Themes']
    story = row['Story']

    prompt = f"""You are an expert storyteller helping to summarize real-life stories about gender and social inequality.

Write a short, powerful, emotional title of about 6 to 10 words based on the story below.

Themes: {themes}
Story: {story}

Title:"""

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=30,
        n=1
    )
    return response.choices[0].message.content.strip()

# Apply the title generation to each row
df['Title'] = df.apply(generate_title, axis=1)

# Preview the results
print(df[['Country', 'Themes', 'Title']].head())

# Save to new CSV
output_filename = "inequality_stories_with_titles_gpt4.csv"
df.to_csv(output_filename, index=False)
print(f"Saved to {output_filename}")
