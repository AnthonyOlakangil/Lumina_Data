import pandas as pd
import re
import pycountry
import openai
import os

# -----CONFIGURATION -----
CSV_FILENAME = 'masterdb - Copy.csv'
OUTPUT_FILENAME = 'masterdb_updated.csv'
# Set to True if you want to use the AI fallback method (requires your OpenAI API key)
USE_AI_FALLBACK = True
# Set your OpenAI API key if you plan to use the AI model:
openai.api_key = os.getenv("API-KEY")  # or directly set: "your-key-here"

# ----- PREPARE COUNTRY DATA -----
# Build a list of all country names using pycountry
countries = [country.name for country in pycountry.countries]

# Define synonyms or alternate names (all keys in lower-case for easy matching)
synonyms = {
    "usa": "United States",
    "us": "United States",
    "america": "United States",
    "u.s.a": "United States",
    "uk": "United Kingdom",
    "england": "United Kingdom",
    "scotland": "United Kingdom",
    "wales": "United Kingdom",
    "nepal": "Nepal",
    "india": "India",
    "australia": "Australia",
    "canada": "Canada",
    # Add more synonyms as needed
}

# ----- HELPER FUNCTIONS -----
def find_country_in_text(text):
    """
    Try to detect a country name from the narrative text using simple substring search.
    Returns the detected country or None.
    """
    text_lower = text.lower()
    # Check for synonyms first
    for key, country in synonyms.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
            return country

    # Check for full country names
    for country in countries:
        if re.search(r'\b' + re.escape(country.lower()) + r'\b', text_lower):
            return country
    return None

def find_country_with_ai(text):
    """
    Uses the OpenAI API to infer the country based on narrative context.
    Expects the response to be a country name or 'Unknown' if insufficient data.
    """
    prompt = (
        "You are given a personal narrative. Based on the clues within the narrative, "
        "determine the country the narrator is based in. If there is insufficient evidence, "
        "simply return 'Unknown'.\n\n"
        f"Narrative: {text}\n\nCountry:"
    )
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=10,
            temperature=0.0,
            top_p=1.0,
            n=1,
            stop=["\n"]
        )
        country = response.choices[0].text.strip()
        # Normalize common responses
        if country.lower() == 'unknown' or not country:
            return None
        return country
    except Exception as e:
        print("AI fallback error:", e)
        return None

def determine_country(narrative):
    """
    Determine the country from the narrative text using heuristic first,
    and then (optionally) an AI model if enabled.
    """
    result = find_country_in_text(narrative)
    if result:
        return result
    if USE_AI_FALLBACK and openai.api_key:
        result_ai = find_country_with_ai(narrative)
        return result_ai
    return None

# ----- MAIN PROCESSING -----
def update_country_in_csv(input_file, output_file):
    # Read the CSV file.
    # If the CSV file does not have headers, you might need to set header=None and use column indices.
    try:
        df = pd.read_csv(input_file, encoding='utf-8', encoding_errors='ignore')
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Determine the column names for country and narrative.
    # Here we assume the first column is 'Country' and the second is 'Narrative'.
    # Adjust these if your CSV file uses different headers.
    country_col = df.columns[0]
    narrative_col = df.columns[1]

    # Process each row where the country is missing or blank.
    for index, row in df.iterrows():
        # Check if country is missing or empty (you can adjust condition as needed)
        if pd.isnull(row[country_col]) or str(row[country_col]).strip() == "":
            narrative_text = str(row[narrative_col])
            detected_country = determine_country(narrative_text)
            if detected_country:
                df.at[index, country_col] = detected_country
                print(f"Row {index}: Set country to {detected_country}")
            else:
                print(f"Row {index}: Could not determine country.")

    # Write the updated DataFrame back to a CSV file.
    try:
        df.to_csv(output_file, index=False)
        print(f"Updated CSV file written to {output_file}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")

if __name__ == "__main__":
    update_country_in_csv(CSV_FILENAME, OUTPUT_FILENAME)
