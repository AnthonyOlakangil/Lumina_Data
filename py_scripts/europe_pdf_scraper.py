from pypdf import PdfReader
import re
import pandas as pd

# Path to your PDF file
pdf_path = "europe.pdf"

# Hard-coded table of contents mapping: (start_page, country)
# (Page numbers are as in the PDF, starting at 1)
toc_mapping = [
    (7, "Austria"),
    (31, "Belgium"),
    (44, "Bulgaria"),
    (60, "Cyprus"),
    (78, "Czech Republic"),
    (95, "Germany"),
    (109, "Denmark"),
    (127, "Estonia"),
    (140, "Spain"),
    (154, "Finland"),
    (169, "France"),
    (192, "Greece"),
    (207, "Croatia"),
    (224, "Hungary"),
    (239, "Ireland"),
    (259, "Iceland"),
    (275, "Italy"),
    (294, "Lithuania"),
    (307, "Luxembourg"),
    (323, "Latvia"),
    (339, "Netherlands"),
    (353, "Poland"),
    (375, "Portugal"),
    (386, "Romania"),
    (402, "Serbia"),
    (416, "Sweden"),
    (432, "Slovenia"),
    (450, "Slovakia"),
    (466, "United Kingdom")
]
toc_mapping.sort(key=lambda x: x[0])

# Extract text from each page using pypdf
reader = PdfReader(pdf_path)
pages_text = []  # list index 0 corresponds to page 1
for page in reader.pages:
    text = page.extract_text() or ""
    pages_text.append(text)

all_text = "\n".join(pages_text).replace("\r\n", "\n")

# Regex pattern to extract narrative blocks.
narrative_pattern = re.compile(
    r'(?P<id>[A-Z]{2}\d{2})\s+Title:\s*(?P<title>.*?)\s+Narrative:\s*(?P<narrative>.*?)\s+Specifically telling quotes:\s*(?P<quotes>.*?)\s+Keywords:\s*(?P<keywords>.*?)(?=\n[A-Z]{2}\d{2}\s+Title:|\Z)',
    re.DOTALL
)

def extract_name(narrative, title):
    """
    Extract the storyteller's name using only two cases:
    1. Look for 'My name is <Name>' in the narrative text.
    2. If not found, return the first word of the title.
    """
    match = re.search(r'My name is ([A-Za-z]+)', narrative)
    if match:
        return match.group(1)
    else:
        # Get the first word from the title (strip any punctuation)
        first_word = title.split()[0] if title.split() else ""
        first_word = re.sub(r'[^\w]', '', first_word)
        return first_word

def extract_age(narrative):
    """
    Extract the age of the storyteller from the narrative.
    Looks for patterns like 'I am 43 years old' (case-insensitive).
    Returns the first occurrence found, or an empty string if not found.
    """
    age_match = re.search(r'(?i)\b(\d{1,3})\s*(?:years?\s*old|year\s*-\s*old)\b', narrative)
    if age_match:
        return age_match.group(1)
    return ""

results = []

# For each narrative block, assign a country using the TOC mapping and extract fields.
for match in narrative_pattern.finditer(all_text):
    narrative_id = match.group("id").strip()
    title = match.group("title").strip()
    narrative = match.group("narrative").strip()
    quotes = match.group("quotes").strip()
    keywords = match.group("keywords").strip()
    
    # Determine the starting page for this narrative by checking each page for the narrative ID.
    narrative_page = None
    for i, page_text in enumerate(pages_text):
        if narrative_id in page_text:
            narrative_page = i + 1  # page numbers start at 1
            break
    if narrative_page is None:
        narrative_page = 0  # fallback
    
    # Use the TOC mapping to assign a country:
    # The narrative belongs to the country whose starting page is the highest that is <= narrative_page.
    assigned_country = ""
    for start_page, country in toc_mapping:
        if narrative_page >= start_page:
            assigned_country = country
        else:
            break

    # Extract the storyteller's name and age.
    name = extract_name(narrative, title)
    age = extract_age(narrative)
    
    results.append({
        "country": assigned_country,
        "page": narrative_page,
        "name": name,
        "age": age,
        "title": title,
        "narrative": narrative,
        "quotes": quotes,
        "keywords": keywords
    })

# Export the results to CSV.
df = pd.DataFrame(results, columns=["country", "page", "name", "age", "title", "narrative", "quotes", "keywords"])
df.to_csv("narratives_extracted1.csv", index=False)

print("Extraction complete. Data saved to narratives_extracted.csv")
