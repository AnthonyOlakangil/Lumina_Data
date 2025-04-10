import pandas as pd
import openai
import os

# ----- CONFIGURATION -----
INPUT_FILENAME = 'masterdb_updated.csv'
OUTPUT_FILENAME = 'masterdb_updated_with_headlines.csv'
USE_AI_FOR_HEADLINE = True
NUM_ROWS_TO_PROCESS = 330  # Number of rows to process

openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set

# ----- HELPER FUNCTION -----
def generate_headline(narrative):
    if not narrative or narrative.strip() == "":
        return ""
    
    prompt = (
        "You are provided with a personal narrative. "
        "Craft a concise, first-person sentence (about 5 to 7 words) that the narrator might say, "
        "reflecting the core theme or experience of the narrative. "
        "Ensure the sentence is in first-person perspective and encapsulates the main point.\n\n"
        f"Narrative: {narrative}\nPreview:"
    )
    
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=15,
            temperature=0.7,
            top_p=1.0,
            n=1,
            stop=["\n"]
        )
        headline = response.choices[0].text.strip()
        return headline
    except Exception as e:
        print(f"Error generating headline: {e}")
        return ""

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
