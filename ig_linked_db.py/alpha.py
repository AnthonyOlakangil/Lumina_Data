import os
import csv
import time
import random
import traceback
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import sent_tokenize
import nltk
from instagrapi import Client

# Download the Punkt tokenizer if needed.
nltk.download('punkt')

# === CONFIGURATION ===

# Input files and directory settings
ORANGE_SLIDE_FILE = "ig_linked_db.py\\orange_slide.png"
ORANGE_TITLE_FILE = "ig_linked_db.py\\orange_title.png"
PURPLE_SLIDE_FILE = "ig_linked_db.py\\purple_slide.png"
PURPLE_TITLE_FILE = "ig_linked_db.py\\purple_title.png"
CSV_FILE = "ig_linked_db.py\\stories_final_updated.csv"
OUTPUT_DIR = "instagram_testing\\output_images"

# Instagram Credentials
INSTAGRAM_USERNAME = "lumina.for.change"
INSTAGRAM_PASSWORD = "lumina-edu"

# Font settings (using Baloo 2)
FONT_PATH = "ig_linked_db.py\\Baloo_2\\Baloo2-VariableFont_wght.ttf"
FONT_SIZE = 30
TEXT_COLOR = (0, 0, 0)  # Black text for title slide; use separate colors for caption/country

# Title slide settings
TITLE_FONT_SIZE = 40
COUNTRY_FONT_SIZE = 30
CAPTION_FONT_SIZE = 25

# Additional aesthetics used in the title slide
# (coordinates and margins from test_new_script.py)
TITLE_X = 150       # Horizontal position for title
TITLE_Y = 250       # Vertical position for title
CAPTION_X = 150     # Horizontal position for caption (used for left margin)
CAPTION_Y = 180     # Vertical position for caption
COUNTRY_X = 540     # Position for country text (modified per aesthetic)
COUNTRY_Y = 680

# Call-to-action slide text
CTA_TEXT = "Read more on Lumina."

# Text wrapping configuration
LINE_SPACING = 8    # Reduced line spacing to compress text vertically
MARGIN_PERCENTAGE = 30  # Extremely aggressive text compression

# CSV and posting settings
MIN_STORIES = 10
MAX_STORIES = 15

# === AESTHETIC FUNCTIONS ===

def draw_wrapped_text(img, text, font, text_color, margin_percentage=MARGIN_PERCENTAGE, custom_margins=None, align="center"):
    """
    Draw text wrapped to fit within custom margins or using percentage-based margins.
    
    Args:
        img: PIL Image object
        text: Text to draw
        font: PIL Font object
        text_color: Color tuple (R,G,B)
        margin_percentage: Percentage of image width to use as margin if custom_margins not provided
        custom_margins: Dict with 'left', 'right', 'top', 'bottom' values in pixels
        align: "center" or "left"
    """
    draw = ImageDraw.Draw(img)
    img_width, img_height = img.size
    
    if custom_margins:
        left_margin = custom_margins['left']
        right_margin = custom_margins['right']
        max_text_width = img_width - (left_margin + right_margin)
    else:
        margin = int(img_width * margin_percentage / 100)
        max_text_width = img_width - (2 * margin)
        left_margin = margin

    # Split text into lines that fit within the width
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0] if bbox else 0
        
        if line_width <= max_text_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    line_height = font.getbbox("Aj")[3] + LINE_SPACING
    total_text_height = len(lines) * line_height
    
    if custom_margins:
        available_height = img_height - (custom_margins['top'] + custom_margins['bottom'])
        start_y = custom_margins['top'] + (available_height - total_text_height) // 2
    else:
        start_y = (img_height - total_text_height) // 2
    
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        if custom_margins:
            if align == "center":
                available_width = img_width - (custom_margins['left'] + custom_margins['right'])
                x = custom_margins['left'] + (available_width - line_width) // 2
            elif align == "left":
                x = custom_margins['left']
        else:
            if align == "center":
                x = (img_width - line_width) // 2
            elif align == "left":
                x = 0
        y = start_y + (i * line_height)
        draw.text((x, y), line, font=font, fill=text_color)

def draw_title_slide(img, title_text, country_text, caption_text, title_font, country_font, caption_font, text_color, color_scheme="orange"):
    """
    Draw text on the title slide.
    Uses bold face for title and country text with stroke widths adjusting boldness,
    and draws caption in gray. Country text color is based on the slide's color scheme.
    """
    draw = ImageDraw.Draw(img)
    
    # Load bold font for title (using Baloo2-Bold.ttf) with adjusted size for longer titles
    if len(title_text.split()) >= 5:
        try:
            title_bold_font = ImageFont.truetype(FONT_PATH,  25)
        except IOError:
            title_bold_font = title_font
    else:
        try:
            title_bold_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
        except IOError:
            title_bold_font = title_font
             
    # Draw title with a milder stroke for a slightly bold appearance
    draw.text((TITLE_X, TITLE_Y), f'"{title_text}"', font=title_bold_font, fill=text_color, stroke_width=1, stroke_fill=text_color)
    
    # Load bold version for caption
    try:
        caption_bold_font = ImageFont.truetype("ig_linked_db.py\\Baloo_2\\Baloo2-Bold.ttf", CAPTION_FONT_SIZE)
    except IOError:
        caption_bold_font = caption_font
    caption_color = (128, 128, 128)  # gray for caption
    caption_margins = {
        'left': TITLE_X,
        'right': 100,         # adjust as needed
        'top': CAPTION_Y,
        'bottom': 150         # retained from previous setting
    }
    draw_wrapped_text(img, caption_text, caption_bold_font, caption_color, custom_margins=caption_margins, align="left")
    
    # Load bold version for country text
    try:
        country_bold_font = ImageFont.truetype("ig_linked_db.py\\Baloo_2\\Baloo2-Bold.ttf", COUNTRY_FONT_SIZE)
    except IOError:
        country_bold_font = country_font
    
    # Set country color based on slide color scheme
    if color_scheme.lower() == "orange":
        country_color = (255, 165, 0)   # Orange
    elif color_scheme.lower() == "purple":
        country_color = (128, 0, 128)     # Purple
    else:
        country_color = text_color

    # Draw country text with a mild stroke (reduced stroke width from 2 to 1)
    draw.text((COUNTRY_X, COUNTRY_Y), country_text, font=country_bold_font, fill=country_color, stroke_width=1, stroke_fill=country_color)

# === STORY CREATION AND POSTING FUNCTIONS ===

def create_and_post_story(row, story_index):
    """
    Create and post a single story carousel to Instagram using CSV row data.
    The row should contain 'Country', 'Story', 'Title', and 'Caption'.
    """
    country = row['Country'] if not pd.isna(row['Country']) else "Unknown Country"
    story = row['Story'] if not pd.isna(row['Story']) else "No story provided."
    title = row['Title'] if not pd.isna(row['Title']) else "Default Title"
    caption = row['Caption'] if not pd.isna(row['Caption']) else "Default Caption"
    
    # Explicitly alternate the color scheme based on the story_index
    if story_index % 2 == 0:
        color_scheme = "orange"
        slide_file = ORANGE_SLIDE_FILE
        title_file = ORANGE_TITLE_FILE
    else:
        color_scheme = "purple"
        slide_file = PURPLE_SLIDE_FILE
        title_file = PURPLE_TITLE_FILE

    # Create a unique subdirectory for this story
    story_dir = os.path.join(OUTPUT_DIR, f"story_{story_index}")
    os.makedirs(story_dir, exist_ok=True)
    output_files = []
    
    print(f"\nProcessing story {story_index} from {country} with {color_scheme} theme...")
    
    # --- STEP 1: Create Title Slide ---
    try:
        title_img = Image.open(title_file).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {title_file}")
    try:
        title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
        country_font = ImageFont.truetype(FONT_PATH, COUNTRY_FONT_SIZE)
        caption_font = ImageFont.truetype(FONT_PATH, CAPTION_FONT_SIZE)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")
    
    draw_title_slide(title_img, title, country, caption, title_font, country_font, caption_font, TEXT_COLOR, color_scheme)
    
    # Save title slide
    title_output_path = os.path.join(story_dir, "output_title.jpg")
    title_img.convert("RGB").save(title_output_path, format="JPEG")
    output_files.append(title_output_path)
    print(f"Saved title image for story {story_index}")
    
    # --- STEP 2: Create Content Slides ---
    sentences = sent_tokenize(story)
    if not sentences:
        print(f"Warning: No sentences found for story {story_index}; skipping.")
        return False

    # If there are more than 10 sentences, only use the first 10 and set a flag to add an ellipsis slide.
    add_ellipsis_slide = False
    if len(sentences) > 10:
        sentences = sentences[:10]
        add_ellipsis_slide = True

    for idx, sentence in enumerate(sentences, start=1):
        try:
            content_img = Image.open(slide_file).convert("RGBA")
        except IOError:
            raise FileNotFoundError(f"Unable to open image file {slide_file}")
        try:
            content_font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except IOError:
            raise FileNotFoundError(f"Font file {FONT_PATH} not found.")
        
        draw_wrapped_text(content_img, sentence, content_font, TEXT_COLOR, MARGIN_PERCENTAGE)
        content_output_path = os.path.join(story_dir, f"output_{idx}.jpg")
        content_img.convert("RGB").save(content_output_path, format="JPEG")
        output_files.append(content_output_path)

    # If more than 10 sentences, add an extra slide with a large, bold ellipsis ("...")
    if add_ellipsis_slide:
        try:
            ellipsis_img = Image.open(slide_file).convert("RGBA")
        except IOError:
            raise FileNotFoundError(f"Unable to open image file {slide_file}")
        try:
            ellipsis_font = ImageFont.truetype(FONT_PATH, 100)
        except IOError:
            ellipsis_font = content_font

        draw = ImageDraw.Draw(ellipsis_img)
        # Get text size for centering
        bbox = draw.textbbox((0, 0), "...", font=ellipsis_font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        img_width, img_height = ellipsis_img.size
        x = (img_width - w) / 2
        y = (img_height - h) / 2
        draw.text((x, y), "...", font=ellipsis_font, fill=TEXT_COLOR)

        ellipsis_output_path = os.path.join(story_dir, f"output_{len(sentences)+1}.jpg")
        ellipsis_img.convert("RGB").save(ellipsis_output_path, format="JPEG")
        output_files.append(ellipsis_output_path)
    
    # --- STEP 3: Create CTA Slide ---
    try:
        cta_img = Image.open(slide_file).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {slide_file}")
    try:
        cta_font = ImageFont.truetype(FONT_PATH, FONT_SIZE + 5)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")
    
    draw_wrapped_text(cta_img, CTA_TEXT, cta_font, TEXT_COLOR, MARGIN_PERCENTAGE)
    cta_output_path = os.path.join(story_dir, "output_cta.jpg")
    cta_img.convert("RGB").save(cta_output_path, format="JPEG")
    output_files.append(cta_output_path)
    
    # --- STEP 4: Post to Instagram ---
    # Use caption from CSV if provided; otherwise compose a default caption.
    post_caption = caption if caption.strip() else f"Story from {country}\n\n{CTA_TEXT}"
    
    try:
        insta_client = Client()
        insta_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print(f"Logged in to Instagram for story {story_index}")
        
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
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Read CSV data
    try:
        df = pd.read_csv(CSV_FILE)
        print(f"Successfully loaded CSV with {len(df)} stories")
    except Exception as e:
        print(f"Failed to load CSV file: {e}")
        return
    
    # Verify required columns
    required_columns = ['Country', 'Story', 'Title', 'Caption']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"CSV file missing required columns: {missing_columns}")
        return
    
    # Select random number of stories (between MIN_STORIES and MAX_STORIES)
    num_stories = min(len(df), random.randint(MIN_STORIES, MAX_STORIES))
    selected_indices = random.sample(range(len(df)), num_stories)
    print(f"Selected {num_stories} stories to process")
    
    successful_posts = 0
    for i, idx in enumerate(selected_indices):
        row = df.iloc[idx]
        print(f"\nPosting story {i+1} of {num_stories} (CSV index {idx})...")
        if create_and_post_story(row, idx):
            successful_posts += 1
            # Add a short delay between posts if not the last one
            if i < len(selected_indices) - 1:
                time.sleep(15)
    
    print(f"\nCompleted posting {successful_posts} out of {num_stories} selected stories")

if __name__ == "__main__":
    main()