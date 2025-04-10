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
df = pd.read_csv('csv-DBs\masterdb.csv')

# Standardize country names (rename "US" to "United States")
df['Country'] = df['Country'].replace('US', 'United States')

# Filter rows where:
# 1. Country is not empty (not NaN and not an empty string)
# 2. Story has more than 20 characters
filtered_df = df[
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