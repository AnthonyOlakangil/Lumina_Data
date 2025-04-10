import pandas as pd
import re
import spacy

# Load spaCy for text processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model isn't installed, download it
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_powerful_quote(story, max_words=7):
    """
    Extract a powerful quote from a story that captures its essence.
    Returns a string of maximum 7 words.
    """
    # Clean the text
    story = story.replace('\n', ' ')
    
    # Look for first-person statements first as they're often more impactful
    first_person_patterns = [
        r'I\s[^.!?]*(?:struggle|journey|experience|fight|face|endure)[^.!?]*[.!?]',
        r'My\s[^.!?]*(?:journey|struggle|experience|life)[^.!?]*[.!?]',
        r'I\s(?:was|am|felt|feel)[^.!?]*[.!?]',
        r'(?:We|I)\s(?:were|was)\s(?:never|always|constantly|rarely)[^.!?]*[.!?]',
        r'My\s(?:father|mother|neighbor|boss|teacher)[^.!?]*[.!?]'
    ]
    
    potential_quotes = []
    
    # Try to find first-person statements first
    for pattern in first_person_patterns:
        matches = re.findall(pattern, story)
        potential_quotes.extend(matches)
    
    # If no first-person statements found, look for other impactful sentences
    if not potential_quotes:
        # Look for sentences with emotional words
        emotional_pattern = r'[^.!?]*(?:discrimination|bias|struggle|fight|pain|hope|challenge|hardship|overcome|resist)[^.!?]*[.!?]'
        matches = re.findall(emotional_pattern, story)
        potential_quotes.extend(matches)
    
    # Look specifically for quotes with direct speech or powerful statements
    direct_speech = re.findall(r'[""][^""]*[""]', story)
    if direct_speech:
        potential_quotes.extend(direct_speech)
    
    # If still no quotes found, split into sentences and take short ones
    if not potential_quotes:
        sentences = re.split(r'[.!?]', story)
        sentences = [s.strip() for s in sentences if 3 <= len(s.split()) <= 15]
        potential_quotes.extend(sentences)
    
    # Score and rank the potential quotes
    scored_quotes = []
    for quote in potential_quotes:
        # Clean up the quote
        quote = quote.strip('"\'".!? ')
        if not quote or len(quote.split()) < 3:
            continue
            
        # Favor quotes with first person
        first_person_score = 3 if re.search(r'\b(I|my|we|our)\b', quote, re.IGNORECASE) else 0
        
        # Favor quotes with action verbs and emotional content
        doc = nlp(quote)
        verb_score = sum(1 for token in doc if token.pos_ == "VERB")
        emotional_score = sum(1 for word in ['never', 'always', 'refused', 'fight', 'struggle', 
                                             'journey', 'pain', 'hope', 'dream', 'isolated', 'overlooked',
                                             'endured', 'battled', 'forced'] 
                              if word in quote.lower())
        
        # Calculate total score
        total_score = first_person_score + verb_score + emotional_score
        scored_quotes.append((quote, total_score))
    
    # Sort by score (descending)
    scored_quotes.sort(key=lambda x: x[1], reverse=True)
    
    # Extract powerful phrases from top quotes
    best_phrases = []
    
    # Try to get impactful short segments first
    for quote, _ in scored_quotes[:5]:  # Consider top 5 quotes
        # Look for powerful phrases that are already the right length
        words = quote.split()
        
        # Try different segment lengths
        for segment_length in range(max_words, 3, -1):
            if len(words) >= segment_length:
                for i in range(len(words) - segment_length + 1):
                    phrase = ' '.join(words[i:i+segment_length])
                    
                    # Score this phrase for impact
                    doc = nlp(phrase)
                    has_subject = any(token.dep_ == "nsubj" for token in doc)
                    has_verb = any(token.pos_ == "VERB" for token in doc)
                    has_emotion = any(word in phrase.lower() for word in 
                                     ['fight', 'struggle', 'journey', 'pain', 'hope', 'dream', 
                                      'strength', 'fear', 'abuse', 'bias', 'ignored'])
                    
                    # Give higher priority to complete thoughts
                    if has_subject and has_verb:
                        best_phrases.append((phrase, 3 + (1 if has_emotion else 0)))
                    else:
                        best_phrases.append((phrase, 1 + (1 if has_emotion else 0)))
    
    # Sort phrases by impact score
    best_phrases.sort(key=lambda x: x[1], reverse=True)
    
    # If we found good phrases, return the best one
    if best_phrases:
        phrase = best_phrases[0][0]
        # Remove unnecessary starting words if needed
        for starter in ['and', 'but', 'so', 'that', 'because', 'the', 'a', 'an']:
            if phrase.lower().startswith(f"{starter} "):
                phrase = phrase[len(starter)+1:]
        return phrase
    
    # Fallback: If we don't have good phrases, use first segment of best quote
    if scored_quotes:
        words = scored_quotes[0][0].split()
        if len(words) > max_words:
            return ' '.join(words[:max_words])
        else:
            return scored_quotes[0][0]
    
    return "A story of inequality"  # Final fallback title

def process_dataset(df):
    """Process the entire dataset to extract quotes for each story."""
    titles = []
    total_stories = len(df)
    
    for i, story in enumerate(df['Story']):
        title = extract_powerful_quote(story)
        titles.append(title)
        
        # Print progress every 5% or at least every 10 stories
        if (i + 1) % max(1, total_stories // 20) == 0 or (i + 1) % 10 == 0:
            progress = (i + 1) / total_stories * 100
            print(f"Processing: {progress:.1f}% complete ({i + 1}/{total_stories} stories)")
    
    return titles

# Main execution
try:
    # Load the dataset
    df = pd.read_csv("stories_with_themes.csv")
    
    # Extract titles
    df['Title'] = process_dataset(df)
    
    # Save the updated dataset
    df.to_csv("stories_with_titles.csv", index=False)
    print(f"Successfully processed {len(df)} stories and saved to 'stories_with_titles.csv'")
    
    # Print sample of results
    print("\nSample of extracted titles:")
    for i in range(min(10, len(df))):
        print(f"{i+1}. {df['Title'].iloc[i]} (Country: {df['Country'].iloc[i]})")
        
except Exception as e:
    print(f"Error processing dataset: {e}")