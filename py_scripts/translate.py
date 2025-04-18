import csv
from googletrans import Translator
from langdetect import detect, LangDetectException

input_file = 'polysim/combined_data_with_laws.csv'
output_file = 'polysim/combined_data_with_laws_translated.csv'

translator = Translator()

def is_english(text):
    try:
        return detect(text) == 'en'
    except (LangDetectException, TypeError):
        return True  # Treat as English if detection fails

translated_count = 0

with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile, \
     open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    for row in reader:
        try:
            value = row[7]  # Column 8 (0-indexed)
            if isinstance(value, str) and value.strip():
                try:
                    translated = translator.translate(value, dest='en').text
                    row[7] = translated
                    translated_count += 1
                except Exception:
                    pass  # Skip translation errors
        except Exception:
            pass  # Skip rows with issues
        writer.writerow(row)

print(f"Rows successfully translated: {translated_count}")