# src/utils.py

import os
from PIL import Image, ImageDraw
from src.constants import ASSETS_DIR, DATABASE_DIR, REPORTS_DIR

def ensure_directories_exist():
    """
    Ensures that all required directories exist on application startup.
    Creates them if they are missing.
    """
    directories = [ASSETS_DIR, DATABASE_DIR, REPORTS_DIR]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created missing directory: {directory}")

def create_placeholder_image(filename: str, text: str, size: tuple = (100, 100)):
    """
    Generates a placeholder image using Pillow if the required asset is missing.
    
    Args:
        filename (str): The name of the file to save (e.g., 'robot_icon.png')
        text (str): The text to display on the placeholder.
        size (tuple): Width and height of the image.
    """
    filepath = os.path.join(ASSETS_DIR, filename)
    
    if not os.path.exists(filepath):
        # Create a blank image with a dark background matching the theme
        image = Image.new('RGB', size, color="#1A1F29")
        draw = ImageDraw.Draw(image)
        
        # Add a cyan border
        draw.rectangle([(0, 0), (size[0]-1, size[1]-1)], outline="#00D9FF", width=2)
        
        # Simple text placement (centered roughly)
        # For a professional project, we'd use a font, but default is safe to prevent crashes.
        draw.text((10, size[1]//2 - 5), text, fill="#00D9FF")
        
        image.save(filepath)
        print(f"Created placeholder image: {filepath}")

def initialize_assets():
    """
    Initializes required assets by creating placeholders if they don't exist.
    """
    ensure_directories_exist()
    create_placeholder_image("robot_icon.png", " AI Robot ", size=(120, 120))