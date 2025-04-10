import pandas as pd
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

API_KEY = os.getenv('API_KEY')

# ----- CONFIGURATION -----
INPUT_FILENAME = 'stories_final.csv'
OUTPUT_FILENAME = 'stories_with_titles.csv'
USE_AI_FOR_HEADLINE = True
NUM_ROWS_TO_PROCESS = 1000  # Set to None to process all rows

openai.api_key = API_KEY # Ensure your API key is set

# ----- HELPER FUNCTION -----
def generate_headline(narrative):
    if not narrative or narrative.strip() == "":
        return ""
    
    messages = [
        {"role": "system", "content": (
            "You are provided with a personal narrative. "
            "Craft a concise, first-person sentence (about 5 to 6 words) that the narrator might say, "
            "reflecting the core theme or experience of the narrative. "
            "Ensure the sentence is in first-person perspective and encapsulates the main point."
            "Add '...' at the end of each preview."
            "'I am a teacher, not a waitress...' is a very good example of a preview."
            "Each preview must be enclosed by double quotes."
            "Each preview must be unique, so no repeats or idential previews should be present upon completion."
            
        )},
        {"role": "user", "content": f"Narrative: {narrative}\nPreview:"}
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Updated to a valid model name
        messages=messages,
        max_tokens=15,
        temperature=0.7,
        top_p=1.0,
        n=1
    )
    headline = response.choices[0].message.content.strip()
    return headline

# ----- MAIN PROCESSING FUNCTION -----
def add_headline_column(input_file, output_file, num_rows):
    try:
        # Read only the first 'num_rows' rows from the CSV file
        df = pd.read_csv(input_file, encoding='utf-8', encoding_errors='ignore', nrows=num_rows)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return
    
    if len(df.columns) < 2:
        print("The input CSV file must have at least two columns.")
        return

    df.insert(2, "Headline", "")

    for index, row in df.iterrows():
        narrative_text = str(row[df.columns[1]])
        if USE_AI_FOR_HEADLINE and openai.api_key:
            headline = generate_headline(narrative_text)
        else:
            headline = ""
        df.at[index, "Headline"] = headline
        print(f"Row {index}: Headline set to: {headline}")

    try:
        df.to_csv(output_file, index=False)
        print(f"Updated CSV file with headlines written to {output_file}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

# ----- EXECUTION -----
if __name__ == "__main__":
    add_headline_column(INPUT_FILENAME, OUTPUT_FILENAME, NUM_ROWS_TO_PROCESS)