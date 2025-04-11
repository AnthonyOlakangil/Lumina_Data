import os
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
import nltk
from nltk.tokenize import sent_tokenize

# Download the Punkt tokenizer if needed.
nltk.download('punkt')

# === CONFIGURATION ===

# Input files and directory settings
IMAGE_FILE = "ig/orange_gradient.png"
TEXT_FILE = "ig/text.txt"
OUTPUT_DIR = "ig/output_images"

# Instagram Credentials (update these with your credentials)
INSTAGRAM_USERNAME = "lumina.for.change"
INSTAGRAM_PASSWORD = "lumina-edu"
# This extra string will be appended to the final caption.
INSTAGRAM_CAPTION_EXTRA = "Posted via automated Python script."

# Font settings for text overlay
FONT_PATH = "arial.ttf"   # Ensure this file exists; update path if needed.
FONT_SIZE = 40            # Adjust as required.
TEXT_COLOR = (255, 255, 255)  # White text

# Choose whether to center the text on each image.
def get_centered_position(draw, text, font, img_width, img_height):
    text_width, text_height = draw.textsize(text, font=font)
    x = (img_width - text_width) / 2
    y = (img_height - text_height) / 2
    return (x, y)

# === STEP 1: Read and Tokenize Text ===

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    full_text = f.read()

# Use nltk to split the text into sentences.
sentences = sent_tokenize(full_text)
if not sentences:
    raise ValueError("No sentences found in the text file.")

print(f"Found {len(sentences)} sentence(s) to overlay.")

# === STEP 2: Overlay Each Sentence on a Copy of the Image ===

os.makedirs(OUTPUT_DIR, exist_ok=True)
output_files = []  # List of file paths to the generated images

for idx, sentence in enumerate(sentences, start=1):
    try:
        # Open the base image (convert to RGBA for transparency support)
        img = Image.open(IMAGE_FILE).convert("RGBA")
    except IOError:
        raise FileNotFoundError(f"Unable to open image file {IMAGE_FILE}")

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except IOError:
        raise FileNotFoundError(f"Font file {FONT_PATH} not found.")

    # Determine centered position (or use a fixed offset if desired)
    img_width, img_height = img.size
    position = get_centered_position(draw, sentence, font, img_width, img_height)

    # Draw the text (you may add stroke or shadow if needed)
    draw.text(position, sentence, fill=TEXT_COLOR, font=font)

    # Save the image to the output directory.
    output_path = os.path.join(OUTPUT_DIR, f"output_{idx}.png")
    img.save(output_path)
    output_files.append(output_path)
    print(f"Saved image {idx} with text overlay to {output_path}")

# === STEP 3: Combine Images into a Carousel (Singular Post) and Publish to Instagram ===

# Create a combined caption.
# For example, you might join all overlaid texts.
# Alternatively, you could provide one overarching caption.
carousel_caption = "\n\n".join(sentences) + "\n\n" + INSTAGRAM_CAPTION_EXTRA

insta_client = Client()
try:
    insta_client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    print("Logged in to Instagram successfully.")
except Exception as e:
    raise RuntimeError(f"Instagram login failed: {e}")

try:
    if len(output_files) == 1:
        # If only one image is generated, post it as a single photo.
        media = insta_client.photo_upload(output_files[0], caption=carousel_caption)
        print(f"Posted single image successfully: media ID {media.get('id', 'N/A')}")
    else:
        # If multiple images exist, upload them as a carousel (album) post.
        media = insta_client.album_upload(output_files, caption=carousel_caption)
        print(f"Posted carousel successfully: media ID {media.get('id', 'N/A')}")
except Exception as e:
    print(f"Failed to post to Instagram: {e}")

insta_client.logout()
print("Logged out from Instagram.")
