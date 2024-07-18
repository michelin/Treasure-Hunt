#!/bin/bash

# Retrieve the flag from the first script argument
FLAG=$1

# Check if the flag has been provided
if [ -z "$FLAG" ]; then
    FLAG='Final Flag : Flag{Raph is the best}'
fi

SCRIPT_DIR=$(dirname "$BASH_SOURCE")
# Create a temporary directory for the python file
TEMP_DIR=$(mktemp -d "python.XXXXXX")
PYTHON_FILE="$TEMP_DIR/createimg.py"

# Create the Java file with the class content
cat <<EOF > "$PYTHON_FILE"
#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageFont
import sys
import os

def create_text_image(text, output_path):
    # Définir la taille de l'image et la couleur de fond
    img_width, img_height = 400, 400
    background_color = (255, 0, 0)  # Rouge
    text_color = (255, 255, 255)  # Blanc
    
    # Créer une nouvelle image
    image = Image.new('RGB', (img_width, img_height), color=background_color)
    
    # Initialiser le dessin sur l'image
    draw = ImageDraw.Draw(image)
    
    # Charger une police (vous pouvez spécifier un chemin vers une police spécifique)
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (img_width - text_width) / 2
    text_y = (img_height - text_height) / 2

    # Ajouter le texte à l'image
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Enregistrer l'image
    image.save(output_path)


image_path=os.path.join("..","$SCRIPT_DIR",'static','image.png')
create_text_image("$FLAG",image_path)
EOF

# Execute the python file in the temporary directory
(cd "$TEMP_DIR" && python createimg.py)

# Clean up: Remove the temporary directory
rm -r "$TEMP_DIR"
