import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
from collections import Counter
from nltk.tokenize import sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
import os

# Create nltk_data directory in user home if it doesn't exist
nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)

# Download required NLTK resources with better error handling
def download_nltk_resource(resource_name):
    try:
        nltk.download(resource_name, quiet=True, download_dir=nltk_data_dir)
        print(f"Successfully downloaded {resource_name}")
    except Exception as e:
        print(f"Error downloading {resource_name}: {str(e)}")
        
# Download required resources
download_nltk_resource('punkt_tab')
download_nltk_resource('stopwords')
download_nltk_resource('vader_lexicon')

# Initialize sentiment analyzer
try:
    sia = SentimentIntensityAnalyzer()
except Exception as e:
    print(f"Error initializing SentimentIntensityAnalyzer: {str(e)}")
    sia = None

# Read the CSV file
df = pd.read_csv('masterdb_updated.csv')

# Standardize country names (rename "US" to "United States")
df['Country'] = df['Country'].replace('US', 'United States')

# Filter rows where:
# 1. Country is not empty (not NaN and not an empty string)
# 2. Story has more than 20 characters
filtered_df = df[
    (~df['Country'].isna() & (df['Country'] != "")) & 
    (df['Story'].str.len() > 20)
]

# Print number of rows that meet the criteria
print(f"Number of rows with non-empty Country and Story longer than 20 characters: {len(filtered_df)}")

# Define theme keywords
theme_keywords = {
    'Workplace': ['job', 'work', 'career', 'office', 'boss', 'colleague', 'workplace', 'company', 'salary', 'pay', 'manager', 'employee'],
    'Education': ['school', 'college', 'university', 'class', 'student', 'teacher', 'professor', 'education', 'learn', 'study', 'academic'],
    'Domestic': ['home', 'family', 'husband', 'wife', 'child', 'children', 'household', 'domestic', 'marriage', 'parent', 'father', 'mother'],
    'Healthcare': ['doctor', 'nurse', 'hospital', 'medical', 'health', 'patient', 'care', 'treatment', 'clinic'],
    'Public Space': ['street', 'public', 'restaurant', 'store', 'shop', 'mall', 'transit', 'bus', 'train', 'car', 'driving'],
    'Cultural': ['tradition', 'culture', 'religion', 'community', 'society', 'norm', 'belief', 'custom', 'expectation'],
    'Identity': ['transgender', 'gender', 'identity', 'lgbtq', 'woman', 'man', 'girl', 'boy', 'feminine', 'masculine']
}

# Function to identify the best 1-2 themes in a story
def identify_themes(story_text):
    story_text = story_text.lower()
    theme_scores = {}
    
    for theme, keywords in theme_keywords.items():
        # Count how many keywords from each theme appear in the story
        matches = sum(1 for keyword in keywords if keyword in story_text)
        if matches > 0:
            theme_scores[theme] = matches
    
    # If no themes found, return 'Other'
    if not theme_scores:
        return ['Other']
    
    # Sort themes by number of keyword matches (descending)
    sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Take top 1-2 themes, depending on how many we found and their scores
    if len(sorted_themes) == 1:
        return [sorted_themes[0][0]]  # Return the only theme
    else:
        # If the second theme has at least half the score of the first theme, include it
        if sorted_themes[1][1] >= sorted_themes[0][1] * 0.5:
            return [sorted_themes[0][0], sorted_themes[1][0]]  # Return top 2
        else:
            return [sorted_themes[0][0]]  # Return only top theme

# Apply theme identification to each story
filtered_df['Themes'] = filtered_df['Story'].apply(identify_themes)

# Flatten the themes for counting
all_themes = [theme for themes_list in filtered_df['Themes'] for theme in themes_list]
theme_counts = Counter(all_themes)

# Print theme distribution
print("\nTheme Distribution:")
for theme, count in theme_counts.most_common():
    print(f"{theme}: {count} stories")

# Optional: Use AI clustering to find additional themes
# Extract features with TF-IDF
vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
X = vectorizer.fit_transform(filtered_df['Story'].fillna(''))

# Cluster the stories
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
filtered_df['Cluster'] = kmeans.fit_predict(X)

# Print most common words in each cluster
print("\nAI-discovered themes (clusters):")
feature_names = vectorizer.get_feature_names_out()
for i in range(num_clusters):
    cluster_stories = filtered_df[filtered_df['Cluster'] == i]
    print(f"\nCluster {i} ({len(cluster_stories)} stories):")
    
    # Get the top words for this cluster
    if len(cluster_stories) > 0:
        centroid = kmeans.cluster_centers_[i]
        top_indices = centroid.argsort()[-10:][::-1]  # Get indices of top 10 words
        top_words = [feature_names[ind] for ind in top_indices]
        print(f"Top words: {', '.join(top_words)}")
        
        # Sample story from this cluster
        print(f"Sample story: {cluster_stories['Story'].iloc[0][:100]}...")

# Save the results
filtered_df.to_csv('stories_with_themes.csv', index=False)

# Print detailed theme tallies with percentages
total_stories = len(filtered_df)
print("\n" + "="*50)
print(f"STORY TALLIES BY THEME (Total Stories: {total_stories})")
print("="*50)

# Get theme counts by country
theme_by_country = {}
for theme in set(all_themes):
    theme_by_country[theme] = {}
    for country in filtered_df['Country'].unique():
        country_df = filtered_df[filtered_df['Country'] == country]
        count = sum(1 for themes in country_df['Themes'] if theme in themes)
        if count:
            theme_by_country[theme][country] = count

# Print theme tallies by country
for theme, countries in theme_by_country.items():
    print(f"\nTheme: {theme}")
    for country, count in sorted(countries.items()):
        percentage = (count / total_stories) * 100
        print(f"{country}: {count} stories ({percentage:.2f}%)")

# Define powerful/emotive words related to inequality
powerful_words = [
    'discrimination', 'inequality', 'unfair', 'struggle', 'fight', 'challenge', 
    'overcome', 'ignored', 'excluded', 'bias', 'sexist', 'racist', 'marginalized',
    'denied', 'refused', 'dismissed', 'rejected', 'stereotype', 'barrier', 'glass ceiling',
    'undervalued', 'overlooked', 'invisible', 'silence', 'oppression', 'privilege',
    'wrong', 'pain', 'fear', 'anger', 'strength', 'power', 'resilience', 'brave'
]

# Function to extract the essence of a powerful quote
def extract_powerful_quote(story):
    # Handle empty or very short stories
    if not story or len(story) < 50:
        return story
    
    # Split the story into sentences
    try:
        sentences = sent_tokenize(story)
    except:
        # Fallback if tokenization fails
        sentences = story.split('. ')
    
    # Skip stories with only one sentence
    if len(sentences) <= 1:
        return distill_core_message(sentences[0])
    
    # Score each sentence based on multiple criteria
    candidates = []
    
    for sentence in sentences:
        # Skip very short or very long sentences
        if len(sentence) < 15 or len(sentence) > 150:
            continue
            
        # Calculate base score
        score = 0
        
        # Presence of first-person pronouns (indicates personal experience)
        if any(pronoun in sentence.lower() for pronoun in ['i ', 'my ', 'me ', 'we ', 'our ']):
            score += 2
            
        # Presence of powerful words
        for word in powerful_words:
            if word in sentence.lower():
                score += 2  # Increased weight for powerful words
                
        # Sentiment intensity (the more emotional, the better)
        if sia:
            sentiment = sia.polarity_scores(sentence)
            score += abs(sentiment['compound']) * 3
        
        # Quotation marks often indicate important statements
        if '"' in sentence or "'" in sentence:
            score += 2
            
        # Add to candidates with score
        candidates.append((sentence, score))
    
    # If no suitable candidates found, use the first sentence
    if not candidates:
        return distill_core_message(sentences[0])
    
    # Sort candidates by score (descending)
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Get the highest scoring sentence and extract its core message
    best_sentence = candidates[0][0]
    return distill_core_message(best_sentence)

# Function to distill the core message from a sentence
def distill_core_message(sentence):
    # Remove common phrases that don't add meaning
    filler_phrases = [
        "I learned that", "I realized that", "I found that", "I discovered that",
        "it was clear that", "it became apparent that", "I understood that",
        "it was obvious that", "I noticed that", "I think that", "I believe that",
        "it seems that", "it appeared that", "it turns out that", "it is true that",
        "the fact is that", "the truth is that", "it is important to note that",
        "I would say that", "one might say that", "you could say that",
        "it was interesting that", "interestingly,", "surprisingly,", "remarkably,"
    ]
    
    working_sentence = sentence
    for phrase in filler_phrases:
        working_sentence = working_sentence.replace(phrase, "")
    
    # Split into words
    words = working_sentence.split()
    
    # Define words to remove (expanded stop words list)
    stop_words = [
        'and', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 
        'that', 'this', 'was', 'were', 'is', 'are', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'but', 'if', 'or', 'because',
        'as', 'until', 'while', 'of', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up',
        'down', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
        't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o',
        're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn',
        'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn',
        'weren', 'won', 'wouldn', 'also', 'however', 'therefore', 'thus', 'hence',
        'meanwhile', 'nevertheless', 'nonetheless', 'instead', 'moreover', 'furthermore'
    ]
    
    # Identify key phrases that should be preserved intact
    key_phrases = [
        "gender inequality", "gender bias", "gender stereotypes", "glass ceiling",
        "gender roles", "equal pay", "sexual harassment", "gender discrimination",
        "equal opportunity", "gender gap", "sexist attitudes", "hidden inequalities"
    ]
    
    # Check if any key phrases exist in the sentence, preserve them if found
    preserved_phrases = []
    working_sentence_lower = working_sentence.lower()
    for phrase in key_phrases:
        if phrase in working_sentence_lower:
            preserved_phrases.append(phrase)
    
    # Extract words with meaning (focus on nouns, verbs, adjectives)
    meaningful_words = []
    for i, word in enumerate(words):
        # Keep first word to maintain flow
        if i == 0 and word.lower() not in stop_words:
            meaningful_words.append(word)
        # Keep powerful words regardless of position
        elif any(pw in word.lower() for pw in powerful_words):
            meaningful_words.append(word)
        # Keep words that aren't stop words
        elif word.lower() not in stop_words:
            # Prioritize longer words (often more meaningful)
            if len(word) > 4:
                meaningful_words.append(word)
            # Also keep shorter words if we don't have many yet
            elif len(meaningful_words) < 3:
                meaningful_words.append(word)
    
    # Construct final title
    if preserved_phrases:
        # Use the most relevant preserved phrase as the core
        core = preserved_phrases[0]
        # Add 1-3 meaningful words if they add value
        extra_words = [w for w in meaningful_words if w.lower() not in core.lower()]
        if extra_words:
            title = f"{core} {' '.join(extra_words[:2])}"
        else:
            title = core
    else:
        # Use the most meaningful words (5-7 max)
        title = ' '.join(meaningful_words[:7])
    
    # Ensure first letter is capitalized
    if title:
        title = title[0].upper() + title[1:]
        
    # Add ellipsis if it's a truncated thought
    if len(title.split()) < len(words) and len(title.split()) > 2:
        title += "..."
        
    return title

# Apply function to create a new Title column
filtered_df['Title'] = filtered_df['Story'].apply(extract_powerful_quote)

# Preview the results
print("\nSample titles extracted from stories:")
for i, (title, story) in enumerate(zip(filtered_df['Title'].head(5), filtered_df['Story'].head(5))):
    print(f"\nStory {i+1}:")
    print(f"Title: \"{title}\"")
    print(f"Story beginning: {story[:100]}...")

# Save the results with the new column
filtered_df.to_csv('stories_final.csv', index=False)
print("\nResults saved to 'stories_final.csv'")