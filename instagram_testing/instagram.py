from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import nltk
from nltk.tokenize import sent_tokenize
import traceback
import openai

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

API_KEY = os.getenv('API_KEY')


# Download the Punkt tokenizer if needed.
nltk.download('punkt')

# === CONFIGURATION ===

# Input files and directory settings
IMAGE_FILE = "instagram_testing\orange_gradient.png"
TEXT_FILE = "instagram_testing\\text.txt"
OUTPUT_DIR = "instagram_testing\output_images"

# Instagram Credentials (update these with your credentials)
INSTAGRAM_USERNAME = "lumina.for.change"
INSTAGRAM_PASSWORD = "lumina-edu"

# OpenAI API credentials
OPENAI_API_KEY = API_KEY

# Font settings for text overlay
FONT_PATH = "arial.ttf"
FONT_SIZE = 30
TEXT_COLOR = (255, 255, 255)  # White text

# Title slide settings
TITLE_TEXT = "I am more than stereotypes and assumptions..."
COUNTRY_TEXT = "The United States"
READ_ARROW_TEXT = "read experience"
TITLE_FONT_SIZE = 40
COUNTRY_FONT_SIZE = 30
ARROW_TEXT_FONT_SIZE = 20
LEFT_MARGIN = 50  # Pixels from left edge for title slide text

# Call-to-action slide text
CTA_TEXT = "Read more on Lumina."

# Text wrapping configuration
LINE_SPACING = 10  # Spacing between lines in pixels
MARGIN_PERCENTAGE = 10  # Percentage of image width to keep as margin on each side

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

def generate_nyt_style_summary(text):
    """Generate a New York Times style summary using OpenAI API."""
    openai.api_key = OPENAI_API_KEY
    messages=[
                {"role": "system", "content": "You are a skilled editor for The New York Times. Create a concise, engaging summary of the following text in the style of a NYT subheading. The summary should be 1-2 sentences that give readers a peek into the story without revealing everything, similar to how many news outlets do on their instagram/social media posts."},
                {"role": "user", "content": text}
            ]
    try:
        response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=15,
        temperature=0.7,
        top_p=1.0,
        n=1
        )
        headline = response.choices[0].message.content.strip()
        return headline
    except Exception as e:
        print(f"Error generating summary with OpenAI: {e}")
        # Fallback: return a simple truncated version of the text
        return text[:100] + "..." if len(text) > 100 else text

# === STEP 1: Read and Tokenize Text ===

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    full_text = f.read()

# Use nltk to split the text into sentences.
sentences = sent_tokenize(full_text)
if not sentences:
    raise ValueError("No sentences found in the text file.")

print(f"Found {len(sentences)} sentence(s) to overlay.")

# === STEP 2: Create the Title Slide ===

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

# Create the title slide
draw_left_aligned_text(
    title_img, 
    TITLE_TEXT, 
    COUNTRY_TEXT, 
    title_font, 
    country_font, 
    arrow_text_font,
    TEXT_COLOR, 
    LEFT_MARGIN
)

# Save the title slide
os.makedirs(OUTPUT_DIR, exist_ok=True)
title_output_path = os.path.join(OUTPUT_DIR, "output_title.jpg")
title_img.convert("RGB").save(title_output_path, format="JPEG")
output_files = [title_output_path]  # Start with title slide
print(f"Saved title image with text overlay to {title_output_path}")

# === STEP 3: Overlay Each Sentence on a Copy of the Image ===

for idx, sentence in enumerate(sentences, start=1):
    try:
        # Open the base image and convert to RGBA for transparency support.
        img = Image.open(IMAGE_FILE).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

    # Draw wrapped text on the image
    draw_wrapped_text(img, sentence, font, TEXT_COLOR, MARGIN_PERCENTAGE)

    # Convert to RGB (Instagram requires JPEG format) and save as JPEG.
    rgb_img = img.convert("RGB")
    output_path = os.path.join(OUTPUT_DIR, f"output_{idx}.jpg")
    rgb_img.save(output_path, format="JPEG")
    output_files.append(output_path)
    print(f"Saved image {idx} with text overlay to {output_path}")

# === STEP 4: Create the CTA slide ===

try:
    # Open the base image for CTA slide
    cta_img = Image.open(IMAGE_FILE).convert("RGBA")
except IOError:
    raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

try:
    # Use a slightly larger font for the CTA
    cta_font = ImageFont.truetype(FONT_PATH, FONT_SIZE + 5)
except IOError:
    raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

# Draw the CTA text
draw_wrapped_text(cta_img, CTA_TEXT, cta_font, TEXT_COLOR, MARGIN_PERCENTAGE)

# Save the CTA slide
cta_output_path = os.path.join(OUTPUT_DIR, f"output_cta.jpg")
cta_img.convert("RGB").save(cta_output_path, format="JPEG")
output_files.append(cta_output_path)
print(f"Saved CTA image with text overlay to {cta_output_path}")

# === STEP 5: Generate NYT-style summary for caption ===

nyt_summary = generate_nyt_style_summary(full_text)
carousel_caption = f"{nyt_summary}\n\n{CTA_TEXT}"
print(f"Generated caption: {carousel_caption}")

# === STEP 6: Combine Images into a Carousel and Publish to Instagram ===

insta_client = Client()
try:
    insta_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    print("Logged in to Instagram successfully.")
except Exception as e:
    traceback.print_exc()
    raise RuntimeError(f"Instagram login failed: {e}")

try:
    if len(output_files) == 1:
        media = insta_client.photo_upload(output_files[0], caption=carousel_caption)
        print(f"Posted single image successfully: media ID {media.pk}")
    else:
        media = insta_client.album_upload(output_files, caption=carousel_caption)
        print(f"Posted carousel successfully: media ID {media.pk}")
except Exception as e:
    traceback.print_exc()
    print("Failed to post to Instagram:", e)

insta_client.logout()
print("Logged out from Instagram.")