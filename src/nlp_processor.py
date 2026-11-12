# src/nlp_processor.py

import json
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem import WordNetLemmatizer

# Import the new JSON path from constants
from src.constants import IGNORE_WORDS_FILE

class NLPProcessor:
    """
    Handles all Natural Language Processing tasks using NLTK.
    Specifically tokenization, POS tagging, noun extraction, and lemmatization.
    """
    
    def __init__(self):
        """
        Initializes the NLP Processor, downloads required datasets, 
        sets up the Lemmatizer, and dynamically loads the ignore list from JSON.
        """
        self._ensure_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        
        # Initialize an empty set, then load words from JSON
        self.ignore_nouns = set()
        self._load_ignore_words()

    def _ensure_nltk_data(self):
        """
        Downloads the required NLTK datasets silently if they are missing.
        """
        for dataset in ['punkt', 'averaged_perceptron_tagger', 'wordnet', 'omw-1.4']:
            try:
                if dataset in ['wordnet', 'omw-1.4']:
                    nltk.data.find(f'corpora/{dataset}')
                elif dataset == 'punkt':
                    nltk.data.find(f'tokenizers/{dataset}')
                else:
                    nltk.data.find(f'taggers/{dataset}')
            except LookupError:
                nltk.download(dataset, quiet=True)

    def _load_ignore_words(self):
        """
        Reads the ignore_words.json file and populates the ignore_nouns set.
        """
        if os.path.exists(IGNORE_WORDS_FILE):
            try:
                with open(IGNORE_WORDS_FILE, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Convert list to a set for O(1) lightning-fast lookup speeds
                    self.ignore_nouns = set(data.get("ignore_words", []))
                    print(f"Loaded {len(self.ignore_nouns)} ignore words from database.")
            except Exception as e:
                print(f"Error loading ignore words JSON: {e}")
        else:
            print(f"Warning: {IGNORE_WORDS_FILE} not found. Ignore filter will be empty.")

    def extract_nouns(self, sentence: str) -> list[str]:
        """
        Processes a sentence, extracts singular nouns, and filters out conversational filler
        based on the external JSON database.
        """
        if not sentence or not isinstance(sentence, str):
            return []

        tokens = word_tokenize(sentence)
        tagged_words = pos_tag(tokens)

        extracted_nouns = []
        for word, tag in tagged_words:
            # Check if the word is tagged as a noun
            if tag.startswith('NN'):
                clean_word = word.lower().strip(".,!?")
                
                if clean_word:
                    # Lemmatize first (convert to singular)
                    singular_word = self.lemmatizer.lemmatize(clean_word)
                    
                    # Only add to the list if it's NOT in our JSON ignore list
                    if singular_word not in self.ignore_nouns and clean_word not in self.ignore_nouns:
                        extracted_nouns.append(singular_word)

        return extracted_nouns

# Example usage for testing standalone
if __name__ == "__main__":
    processor = NLPProcessor()
    test_sentence = "Hello! Today I need to buy items for my house. Please find apples, milk, and detergent."
    nouns = processor.extract_nouns(test_sentence)
    print(f"Extracted Groceries: {nouns}")