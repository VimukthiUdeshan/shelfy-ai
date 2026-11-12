# src/main.py

import sys
import os

# Ensure the parent directory is in the system path so local imports work seamlessly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import initialize_assets
from src.gui import ShelfyGUI

def main():
    """
    Main execution function for the Smart Mart AI application.
    It prepares the environment and starts the CustomTkinter main loop.
    """
    print("Starting Shelfy AI...")
    
    # Step 1: Check and initialize necessary folders and placeholder assets
    initialize_assets()
    
    # Step 2: Initialize and run the graphical user interface
    try:
        app = ShelfyGUI()
        app.mainloop()
    except Exception as e:
        print(f"A critical error occurred while running the application: {e}")

if __name__ == "__main__":
    main()