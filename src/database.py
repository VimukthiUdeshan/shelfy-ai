# src/database.py

import json
import os
import difflib
from src.constants import DATABASE_FILE

class ProductDatabase:
    """
    Manages the loading and searching of the supermarket products database.
    """
    
    def __init__(self):
        """
        Initializes the database object and loads the data into memory.
        """
        self.products_data = []
        self.load_database()

    def load_database(self):
        """
        Loads the products from the JSON file. 
        If the file is missing or corrupted, it initializes an empty list 
        to prevent application crashes.
        """
        if not os.path.exists(DATABASE_FILE):
            print(f"Error: Database file not found at {DATABASE_FILE}")
            self.products_data = []
            return

        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.products_data = data.get("products", [])
        except json.JSONDecodeError:
            print("Error: Database file is corrupted or invalid JSON.")
            self.products_data = []
        except Exception as e:
            print(f"Unexpected error loading database: {e}")
            self.products_data = []

    def get_all_product_names(self) -> list[str]:
        """
        Extracts a list of all product names currently in the database.
        
        Returns:
            list[str]: A list of product names.
        """
        return [product["name"].lower() for product in self.products_data]

    def search_product(self, item_name: str) -> dict:
        """
        Searches for a product in the database. 
        If an exact match is not found, attempts to find the closest match using difflib.
        
        Args:
            item_name (str): The name of the product to search for.
            
        Returns:
            dict: A dictionary containing the search result status and relevant data.
                  Format for found: {"status": "found", "name": "...", "shelf": "..."}
                  Format for suggestion: {"status": "suggested", "suggestion": "...", "original": "..."}
                  Format for not found: {"status": "not_found", "original": "..."}
        """
        item_name_lower = item_name.lower().strip()
        
        # 1. Check for exact match
        for product in self.products_data:
            if product["name"].lower() == item_name_lower:
                return {
                    "status": "found",
                    "name": product["name"].capitalize(),
                    "shelf": product["shelf"]
                }
                
        # 2. Check for close matches (spelling mistakes)
        all_names = self.get_all_product_names()
        close_matches = difflib.get_close_matches(item_name_lower, all_names, n=1, cutoff=0.6)
        
        if close_matches:
            return {
                "status": "suggested",
                "suggestion": close_matches[0].capitalize(),
                "original": item_name
            }
            
        # 3. Completely unknown product
        return {
            "status": "not_found",
            "original": item_name
        }

# Example usage for testing standalone
if __name__ == "__main__":
    db = ProductDatabase()
    print(db.search_product("milk"))
    print(db.search_product("milkk"))
    print(db.search_product("spaceship"))