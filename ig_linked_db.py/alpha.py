import os
import csv
import time
import random
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import nltk
from nltk.tokenize import sent_tokenize
import traceback
import pandas as pd

# Download the Punkt tokenizer if needed.
nltk.download('punkt')

# === CONFIGURATION ===

# Input files and directory settings
IMAGE_FILE = "instagram_testing\orange_gradient.png"
CSV_FILE = "stories_final.csv"
OUTPUT_DIR = "instagram_testing\output_images"

# Instagram Credentials
INSTAGRAM_USERNAME = "lumina.for.change"
INSTAGRAM_PASSWORD = "lumina-edu"

# Font settings
FONT_PATH = "arial.ttf"
FONT_SIZE = 30
TEXT_COLOR = (255, 255, 255)  # White text

# Title slide settings
TITLE_FONT_SIZE = 40
COUNTRY_FONT_SIZE = 30
ARROW_TEXT_FONT_SIZE = 20
LEFT_MARGIN = 50  # Pixels from left edge for title slide text

# Call-to-action slide text
CTA_TEXT = "Read more on Lumina."

# Text wrapping configuration
LINE_SPACING = 10
MARGIN_PERCENTAGE = 10

# Batch processing settings
MIN_STORIES = 10
MAX_STORIES = 15
BUFFER_TIME = 30  # Seconds to wait between posting stories

def draw_wrapped_text(img, text, font, text_color, margin_percentage=10):
    """Draw text wrapped to fit the image width with margins."""
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    # Calculate usable width (with margins)
    margin = int(img_width * margin_percentage / 100)
    max_text_width = img_width - (2 * margin)
    
    # Split text into lines that fit within the width
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        # Add the word to the current line and check width
        test_line = ' '.join(current_line + [word])
        # getbbox() gets the bounding box (left, top, right, bottom)
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0] if bbox else 0
        
        if line_width <= max_text_width:
            current_line.append(word)
        else:
            # Line is full, append it and start a new line
            if current_line:  # Don't append empty lines
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Append the last line if it's not empty
    if current_line:
        lines.append(' '.join(current_line))
    
    # Calculate total text height
    line_height = font.getbbox("Aj")[3] + LINE_SPACING  # Height of text line plus spacing
    total_text_height = len(lines) * line_height
    
    # Calculate starting Y position to center the text block vertically
    start_y = (img_height - total_text_height) // 2
    
    # Draw each line centered horizontally
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        x = (img_width - line_width) // 2
        y = start_y + (i * line_height)
        draw.text((x, y), line, font=font, fill=text_color)

def draw_left_aligned_text(img, title_text, country_text, title_font, country_font, arrow_font, text_color, left_margin):
    """Draw left-aligned text for the title slide with an arrow pointing right."""
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    # Calculate text wrapping width
    max_text_width = img_width - (left_margin * 2)
    
    # Wrap title text
    title_lines = []
    words = title_text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = title_font.getbbox(test_line)
        line_width = bbox[2] - bbox[0] if bbox else 0
        
        if line_width <= max_text_width:
            current_line.append(word)
        else:
            if current_line:
                title_lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        title_lines.append(' '.join(current_line))
    
    # Calculate spacing
    title_line_height = title_font.getbbox("Aj")[3] + LINE_SPACING
    country_height = country_font.getbbox("Aj")[3]
    
    # Position text vertically (centered with some spacing)
    total_height = (len(title_lines) * title_line_height) + country_height + (LINE_SPACING * 3)
    start_y = (img_height - total_height) // 2
    
    # Draw title text (left-aligned)
    for i, line in enumerate(title_lines):
        y = start_y + (i * title_line_height)
        draw.text((left_margin, y), line, font=title_font, fill=text_color)
    
    # Draw country text (left-aligned)
    country_y = start_y + (len(title_lines) * title_line_height) + (LINE_SPACING * 2)
    draw.text((left_margin, country_y), country_text, font=country_font, fill=text_color)
    
    # Draw arrow and "read experience" text at bottom right
    arrow_text = "→"
    arrow_font_size = ARROW_TEXT_FONT_SIZE + 10  # Larger font for arrow
    arrow_font_obj = ImageFont.truetype(FONT_PATH, arrow_font_size)
    
    # Position arrow near right edge
    arrow_bbox = arrow_font_obj.getbbox(arrow_text)
    arrow_width = arrow_bbox[2] - arrow_bbox[0]
    arrow_height = arrow_bbox[3] - arrow_bbox[1]
    
    # Position read text
    read_text = "read experience"
    read_bbox = arrow_font.getbbox(read_text)
    read_width = read_bbox[2] - read_bbox[0]
    
    # Position at bottom right with some margin
    arrow_x = img_width - arrow_width - 50
    arrow_y = img_height - arrow_height - 80
    
    # Draw arrow and text
    draw.text((arrow_x, arrow_y), arrow_text, font=arrow_font_obj, fill=text_color)
    draw.text((arrow_x - (read_width // 2) + (arrow_width // 2), arrow_y + arrow_height + 5), 
              read_text, font=arrow_font, fill=text_color)

def create_and_post_story(country, story, title, caption, story_index):
    """Create and post a single story carousel to Instagram."""
    # Create a unique subdirectory for this story's images
    story_dir = os.path.join(OUTPUT_DIR, f"story_{story_index}")
    os.makedirs(story_dir, exist_ok=True)
    
    output_files = []
    
    print(f"\nProcessing story {story_index} from {country}...")
    
    # === STEP 1: Create the Title Slide ===
    try:
        title_img = Image.open(IMAGE_FILE).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

    try:
        title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
        country_font = ImageFont.truetype(FONT_PATH, COUNTRY_FONT_SIZE)
        arrow_text_font = ImageFont.truetype(FONT_PATH, ARROW_TEXT_FONT_SIZE)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

    # Use the title from CSV, or default if empty
    title_text = title if title and not pd.isna(title) else "I am more than stereotypes and assumptions..."
    
    # Create the title slide
    draw_left_aligned_text(
        title_img, 
        title_text, 
        country, 
        title_font, 
        country_font, 
        arrow_text_font,
        TEXT_COLOR, 
        LEFT_MARGIN
    )

    # Save the title slide
    title_output_path = os.path.join(story_dir, "output_title.jpg")
    title_img.convert("RGB").save(title_output_path, format="JPEG")
    output_files.append(title_output_path)
    print(f"Saved title image for story {story_index}")

    # === STEP 2: Tokenize story text into sentences ===
    sentences = sent_tokenize(story)
    if not sentences:
        print(f"Warning: No sentences found in story {story_index}, skipping.")
        return False
    
    print(f"Found {len(sentences)} sentence(s) to overlay for story {story_index}")

    # === STEP 3: Create content slides ===
    for idx, sentence in enumerate(sentences, start=1):
        try:
            img = Image.open(IMAGE_FILE).convert("RGBA")
        except IOError:
            raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except IOError:
            raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

        # Draw wrapped text on the image
        draw_wrapped_text(img, sentence, font, TEXT_COLOR, MARGIN_PERCENTAGE)

        # Save the image
        output_path = os.path.join(story_dir, f"output_{idx}.jpg")
        img.convert("RGB").save(output_path, format="JPEG")
        output_files.append(output_path)

    # === STEP 4: Create the CTA slide ===
    try:
        cta_img = Image.open(IMAGE_FILE).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

    try:
        cta_font = ImageFont.truetype(FONT_PATH, FONT_SIZE + 5)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

    # Draw the CTA text
    draw_wrapped_text(cta_img, CTA_TEXT, cta_font, TEXT_COLOR, MARGIN_PERCENTAGE)

    # Save the CTA slide
    cta_output_path = os.path.join(story_dir, f"output_cta.jpg")
    cta_img.convert("RGB").save(cta_output_path, format="JPEG")
    output_files.append(cta_output_path)
    
    # === STEP 5: Post to Instagram ===
    # Use caption from CSV, or default if empty
    post_caption = caption if caption and not pd.isna(caption) else f"Story from {country}\n\n{CTA_TEXT}"
    
    try:
        insta_client = Client()
        insta_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print(f"Logged in to Instagram to post story {story_index}")
        
        if len(output_files) == 1:
            media = insta_client.photo_upload(output_files[0], caption=post_caption)
            print(f"Posted single image for story {story_index}: media ID {media.pk}")
        else:
            media = insta_client.album_upload(output_files, caption=post_caption)
            print(f"Posted carousel for story {story_index}: media ID {media.pk}")
            
        insta_client.logout()
        print(f"Successfully posted story {story_index} from {country}")
        return True
    except Exception as e:
        print(f"Failed to post story {story_index}:")
        traceback.print_exc()
        return False

# === MAIN PROGRAM ===

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Read data from CSV
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Successfully loaded CSV with {len(df)} stories")
    except Exception as e:
        print(f"Failed to load CSV file: {e}")
        return
    
    # Verify required columns exist
    required_columns = ['Country', 'Story', 'Title', 'Caption']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"CSV file missing required columns: {missing_columns}")
        return
    
    # Select random stories to post
    num_stories = min(len(df), random.randint(MIN_STORIES, MAX_STORIES))
    selected_indices = random.sample(range(len(df)), num_stories)
    
    print(f"Selected {num_stories} stories to post")
    
    # Process each selected story
    successful_posts = 0
    for i, idx in enumerate(selected_indices):
        row = df.iloc[idx]
        country = row['Country']
        story = row['Story']
        title = row['Title']
        caption = row['Caption']
        
        print(f"\nPosting story {i+1} of {num_stories} (index {idx})...")
        
        if create_and_post_story(country, story, title, caption, idx):
            successful_posts += 1
            
            # Add buffer time between posts to avoid overloading servers
            if i < len(selected_indices) - 1:  # Don't wait after the last post
                print(f"Waiting {BUFFER_TIME} seconds before processing next story...")
                time.sleep(BUFFER_TIME)
    
    print(f"\nCompleted posting {successful_posts} out of {num_stories} selected stories")

if __name__ == "__main__":
    main()