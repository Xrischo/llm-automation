from PIL import Image, ImageDraw, ImageFont

def draw_text(draw, text, position, font, max_width):
    # Initialize variables
    lines = []
    words = text.split()
    current_line = []
    current_line_width = 0

    # Iterate over words to split text into lines
    for word in words:
        # Calculate the width of the current line with the new word
        word_size = draw.textbbox((0, 0), word, font=font)
        word_width = word_size[2] - word_size[0]
        word_height = word_size[3] - word_size[1]
        space_size = draw.textbbox((0, 0), ' ', font=font)
        space_width = space_size[2] - space_size[0]

        new_line_width = current_line_width + word_width + (space_width if current_line else 0)

        # If the current line + word is within the max width, add the word to the line
        if new_line_width <= max_width:
            current_line.append(word)
            current_line_width = new_line_width
        else:
            # Otherwise, finalize the current line and start a new one
            lines.append(' '.join(current_line))
            current_line = [word]
            current_line_width = word_width

    # Append the last line
    if current_line:
        lines.append(' '.join(current_line))

    # Draw the lines on the image
    y = position[1]
    for line in lines:
        draw.text((position[0], y), line, font=font, fill=(0, 0, 0))
        y += word_height + 10

# Load the original image
base_image = Image.open('input.png')

# Load the overlay image
overlay_image = Image.open('avatar.png')

# Resize the overlay image if necessary
overlay_size = (80, 80)  # Resize to 100x100 pixels
overlay_image = overlay_image.resize(overlay_size)

# Create a circular mask
mask = Image.new('L', overlay_size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, overlay_size[0], overlay_size[1]), fill=255)

# Apply the circular mask to the overlay image
overlay_image.putalpha(mask)

# Initialize the drawing context for the base image
draw = ImageDraw.Draw(base_image)

# Define the font and size
font = ImageFont.truetype('Outfit-Bold.ttf', 36)

# Define text and positions
text_top = "Top Text"
position_top = (120, 20)

text_bottom = "Bottom Text this is where the title will go hm maybe a bit longer then"
position_bottom = (30, base_image.height - 180)

# Add text to the image with black color
draw.text(position_top, text_top, (0, 0, 0), font=font)
draw_text(draw, text_bottom, position_bottom, font, base_image.width - 20)

# Define the position for the overlay image
overlay_position = (30, 20)  # You can change this to the desired position

# Paste the circular overlay image on top of the base image
base_image.paste(overlay_image, overlay_position, overlay_image)

# Save the modified image
base_image.save('output.png')
