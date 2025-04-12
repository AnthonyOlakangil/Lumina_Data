import os
from PIL import Image, ImageDraw, ImageFont
import nltk
from nltk.tokenize import sent_tokenize
import traceback

# Download the Punkt tokenizer if needed.
nltk.download('punkt')

# === CONFIGURATION ===

# Input files and directory settings
ORANGE_SLIDE_FILE = "ig_linked_db.py\orange_slide.png"
ORANGE_TITLE_FILE = "ig_linked_db.py\orange_title.png"
PURPLE_SLIDE_FILE = "ig_linked_db.py\purple_slide.png"
PURPLE_TITLE_FILE = "ig_linked_db.py\purple_title.png"
OUTPUT_DIR = "instagram_testing/output_images"

# Font settings
FONT_PATH = "ig_linked_db.py\Baloo_2\Baloo2-VariableFont_wght.ttf"
FONT_SIZE = 30
TEXT_COLOR = (0, 0, 0)  # Black text

# Title slide settings
TITLE_FONT_SIZE = 40
COUNTRY_FONT_SIZE = 30
CAPTION_FONT_SIZE = 25

# Content slide settings - MAXIMUM compression margins
CONTENT_MARGIN_LEFT = 200    # Extreme left margin increase
CONTENT_MARGIN_RIGHT = 200   # Extreme right margin increase
CONTENT_MARGIN_TOP = 200     # Extreme top margin increase
CONTENT_MARGIN_BOTTOM = 200  # Extreme bottom margin increase

# Title slide position adjustments
TITLE_X = 150       # Horizontal position for title
TITLE_Y = 250       # Vertical position for title
CAPTION_X = 150     # Horizontal position for caption
CAPTION_Y = 180     # Vertical position for caption

# Country position - moved down 26px and right 12px as requested
COUNTRY_X = 540     # Moved 12px further right (from 360)
COUNTRY_Y = 680     # Moved 26px down (from 460)

# Call-to-action slide text
CTA_TEXT = "Read more on Lumina."

# Text wrapping configuration
LINE_SPACING = 8    # Reduced line spacing to compress text vertically
MARGIN_PERCENTAGE = 30  # Extremely aggressive text compression

def draw_wrapped_text(img, text, font, text_color, margin_percentage=30, 
                        custom_margins=None, align="center"):
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
    
    # Calculate usable width (with margins)
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

def draw_title_slide(img, title_text, country_text, caption_text, title_font, country_font, caption_font, text_color):
    """Draw text on the title slide according to the template."""
    draw = ImageDraw.Draw(img)
    
    # Draw the title
    draw.text((TITLE_X, TITLE_Y), f'"{title_text}"', font=title_font, fill=text_color)
    
    # Load a bold version of the caption font (fallback to caption_font if bold version not found)
    try:
        caption_bold_font = ImageFont.truetype("Baloo2-Bold.ttf", CAPTION_FONT_SIZE)
    except IOError:
        caption_bold_font = caption_font
    
    # Set custom margins for the caption:
    # left margin now aligns with the title (TITLE_X) and right margin lets the text wrap naturally.
    caption_margins = {
        'left': TITLE_X,
        'right': 100,        # You may adjust this value as needed
        'top': CAPTION_Y,
        'bottom': 150        # Retained from your previous setting
    }
    draw_wrapped_text(img, caption_text, caption_bold_font, text_color, 
                      custom_margins=caption_margins, align="left")
    
    # Draw the country name at the adjusted position
    draw.text((COUNTRY_X, COUNTRY_Y), country_text, font=country_font, fill=text_color)

def create_test_post(color_scheme="orange"):
    """Create a single test post without actually posting to Instagram."""
    # Select appropriate image files based on color scheme
    if color_scheme == "orange":
        slide_file = ORANGE_SLIDE_FILE
        title_file = ORANGE_TITLE_FILE
    else:  # purple
        slide_file = PURPLE_SLIDE_FILE
        title_file = PURPLE_TITLE_FILE
    
    # Test data
    country = "United States"
    title = "Breaking Barriers"
    caption = "A story about overcoming challenges and finding strength"
    story = "I was always told that I couldn't succeed in this field. People made assumptions about my abilities based on where I came from. Despite the doubts and stereotypes, I persevered. Each obstacle became an opportunity to prove myself. Now I'm helping others overcome similar barriers."
    
    # Create a unique subdirectory for this test
    story_dir = os.path.join(OUTPUT_DIR, f"test_{color_scheme}")
    os.makedirs(story_dir, exist_ok=True)
    
    output_files = []
    
    print(f"\nCreating test post with {color_scheme} color scheme...")
    
    # === STEP 1: Create the Title Slide ===
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
    
    # Create the title slide
    draw_title_slide(
        title_img, 
        title, 
        country, 
        caption,
        title_font, 
        country_font, 
        caption_font,
        TEXT_COLOR
    )

    # Save the title slide
    title_output_path = os.path.join(story_dir, "output_title.jpg")
    title_img.convert("RGB").save(title_output_path, format="JPEG")
    output_files.append(title_output_path)
    print(f"Saved title image for test post")

    # === STEP 2: Tokenize story text into sentences ===
    sentences = sent_tokenize(story)
    if not sentences:
        print(f"Warning: No sentences found in test story, skipping.")
        return False
    
    print(f"Found {len(sentences)} sentence(s) to overlay for test post")

    # === STEP 3: Create content slides ===
    for idx, sentence in enumerate(sentences, start=1):
        try:
            img = Image.open(slide_file).convert("RGBA")
        except IOError:
            raise FileNotFoundError(f"Unable to open image file {slide_file}")

        try:
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except IOError:
            raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

        # Define custom margins to contain text within quote marks - maximum compression
        content_margins = {
            'left': CONTENT_MARGIN_LEFT,
            'right': CONTENT_MARGIN_RIGHT,
            'top': CONTENT_MARGIN_TOP,
            'bottom': CONTENT_MARGIN_BOTTOM
        }
        
        # Draw wrapped text on the image with custom margins
        draw_wrapped_text(img, sentence, font, TEXT_COLOR, custom_margins=content_margins)

        # Save the image
        output_path = os.path.join(story_dir, f"output_{idx}.jpg")
        img.convert("RGB").save(output_path, format="JPEG")
        output_files.append(output_path)
        print(f"Saved content slide {idx}")

    # === STEP 4: Create the CTA slide ===
    try:
        cta_img = Image.open(slide_file).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {slide_file}")

    try:
        cta_font = ImageFont.truetype(FONT_PATH, FONT_SIZE + 5)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

    # Draw the CTA text with custom margins - maximum compression
    cta_margins = {
        'left': CONTENT_MARGIN_LEFT,
        'right': CONTENT_MARGIN_RIGHT,
        'top': CONTENT_MARGIN_TOP,
        'bottom': CONTENT_MARGIN_BOTTOM
    }
    draw_wrapped_text(cta_img, CTA_TEXT, cta_font, TEXT_COLOR, custom_margins=cta_margins)

    # Save the CTA slide
    cta_output_path = os.path.join(story_dir, f"output_cta.jpg")
    cta_img.convert("RGB").save(cta_output_path, format="JPEG")
    output_files.append(cta_output_path)
    print(f"Saved CTA slide")
    
    print(f"\nTest post creation complete. Images saved to {story_dir}")
    print(f"Generated {len(output_files)} images in total")
    print(f"To actually post this to Instagram, you would use these files with caption: \"{caption}\"")
    
    return output_files

# Test both color schemes
def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=== TESTING ORANGE COLOR SCHEME ===")
    create_test_post("orange")
    
    print("\n=== TESTING PURPLE COLOR SCHEME ===")
    create_test_post("purple")
    
    print("\nTest complete! Check the output directories for the generated images.")

if __name__ == "__main__":
    main()