# src/constants.py

import os

# ==========================================
# FILE PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

DATABASE_FILE = os.path.join(DATABASE_DIR, "products.json")
IGNORE_WORDS_FILE = os.path.join(DATABASE_DIR, "ignore_words.json") # NEW PATH

# ==========================================
# GUI THEME & COLORS
# ==========================================
# Dark futuristic theme colors
COLOR_BACKGROUND = "#10131A"
COLOR_CARD = "#1A1F29"
COLOR_ACCENT = "#00D9FF"  # Cyan/Blue
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_SECONDARY = "#A0AAB5"
COLOR_STATUS_OK = "#00FF00"  # Green
COLOR_STATUS_ERROR = "#FF4444"

# ==========================================
# FONTS
# ==========================================
FONT_FAMILY = "Helvetica"  # Modern standard font fallback
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 14, "italic")
FONT_NORMAL = (FONT_FAMILY, 14)
FONT_LARGE = (FONT_FAMILY, 18)
FONT_STATUS = (FONT_FAMILY, 12, "bold")

# ==========================================
# APPLICATION SETTINGS
# ==========================================
APP_TITLE = "Shelfy AI - Your Smart Shopping Assistant"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# src/constants.py (Add to existing file)

# --- Firebase Configuration ---
FIREBASE_CONFIG = {
  "apiKey": "AIzaSyBF_rqJxNhZ94W1C27IFgtUUqJZfKJWUCA",
  "authDomain": "shelfy-2e52e.firebaseapp.com",
  "databaseURL": "https://shelfy-2e52e-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "shelfy-2e52e",
  "storageBucket": "shelfy-2e52e.firebasestorage.app",
  "messagingSenderId": "293885570624",
  "appId": "1:293885570624:web:0c8f44a2276d8b861339a5",
  "measurementId": "G-R6P00HNFYH"
};