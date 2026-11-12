# src/chatbot.py

import random
from src.nlp_processor import NLPProcessor
from src.database import ProductDatabase

class ChatbotManager:
    """
    Acts as the core controller linking natural language processing
    and the product database to generate intelligent responses.
    """

    def __init__(self):
        """
        Initializes the NLP processor and product database.
        """
        self.nlp = NLPProcessor()
        self.db = ProductDatabase()

    def get_greeting(self) -> str:
        """
        Returns a natural greeting message to display on startup or clear.
        
        Returns:
            str: A randomized welcoming string.
        """
        greetings = [
            "Hello! What would you like today?",
            "Welcome to Smart Mart! How can I help you?",
            "Hi there! Type your shopping list below."
        ]
        return random.choice(greetings)

    def process_input(self, user_input: str) -> dict:
        """
        Processes the user's raw input string, extracts products, 
        and determines their shelf locations.

        Args:
            user_input (str): The raw sentence from the user.

        Returns:
            dict: A dictionary containing the conversational response and structured item lists.
                  Keys: 'message', 'found_items', 'suggestions', 'not_found'
        """
        if not user_input.strip():
            return {
                "message": "Please enter some items so I can help you find them.",
                "found_items": [],
                "suggestions": [],
                "not_found": []
            }

        # Extract nouns using the NLTK pipeline
        extracted_nouns = self.nlp.extract_nouns(user_input)

        if not extracted_nouns:
            return {
                "message": "I couldn't identify any products in your request. Please try again.",
                "found_items": [],
                "suggestions": [],
                "not_found": []
            }

        found_items = []
        suggestions = []
        not_found = []

        # Search the database for each extracted noun
        for noun in extracted_nouns:
            result = self.db.search_product(noun)
            
            if result["status"] == "found":
                # Prevent duplicate items if the user repeats a noun
                if not any(item['name'] == result['name'] for item in found_items):
                    found_items.append(result)
            elif result["status"] == "suggested":
                suggestions.append(result)
            else:
                not_found.append(result)

        # Formulate a natural AI response
        if found_items:
            msg = f"Found {len(found_items)} products. Good luck with your shopping!"
        elif suggestions:
            msg = "I couldn't find exactly what you asked for, but I have some suggestions."
        else:
            msg = "I'm sorry, I couldn't find any of those items in our store."

        return {
            "message": msg,
            "found_items": found_items,
            "suggestions": suggestions,
            "not_found": not_found
        }