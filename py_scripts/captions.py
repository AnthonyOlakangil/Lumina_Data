import csv
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env
OPENAI_API_KEY = os.getenv('API_KEY')
openai.api_key = OPENAI_API_KEY

def generate_nyt_style_summary(text):
    """Generate a New York Times style summary using OpenAI API."""
    messages = [
        {"role": "system", "content": "You are a skilled editor for The New York Times. Create a concise, engaging summary of the following text in the style of a NYT subheading. The summary should be 1-2 sentences that give readers a peek into the story without revealing everything, similar to how many news outlets do on their instagram/social media posts. *Ensure that the caption results in a full sentence, and ends cohesively*"},
        {"role": "user", "content": text}
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=30,
            temperature=0.6,
            top_p=1.0,
            n=1
        )
        headline = response.choices[0].message.content.strip()
        return headline
    except Exception as e:
        print(f"Error generating summary with OpenAI: {e}")
        # Fallback: return a simple truncated version of the text
        return text[:100] + "..." if len(text) > 100 else text

def main():
    input_csv = "ig_linked_db.py\\stories_final.csv"
    output_csv = "ig_linked_db.py\\stories_final_updated.csv"
    
    rows = []
    with open(input_csv, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames.copy()
        # Ensure the "Caption" column exists (column 6)
        if "Caption" not in fieldnames:
            fieldnames.append("Caption")
        
        row_count = 0
        for row in reader:
            row_count += 1
            # Assume that the text to summarize is in a column named "Story".
            text_to_summarize = row.get("Story", "")
            if text_to_summarize:
                caption = generate_nyt_style_summary(text_to_summarize)
            else:
                caption = ""
            row["Caption"] = caption
            rows.append(row)
            print(f"Processed row {row_count}: Caption -> {caption}")
    
    with open(output_csv, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Updated captions written to {output_csv}")

if __name__ == "__main__":
    main()