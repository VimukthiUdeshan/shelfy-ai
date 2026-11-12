# src/gui.py

import os
import uuid
import tkinter as tk
from datetime import datetime
import customtkinter as ctk
from PIL import Image

from src.constants import *
from src.chatbot import ChatbotManager
from src.printer import PDFPrinter
from src.animation import TypingAnimator
from src.firebase_manager import FirebaseManager


class ShelfyGUI(ctk.CTk):
    """
    Main Graphical User Interface for the Smart Mart AI application.
    Features a modern ChatGPT/Claude-style conversational UI with sidebars,
    auth screens, session history, and interactive product cards focused on shelf location.
    """

    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.configure(fg_color=COLOR_BACKGROUND)
        self.minsize(1024, 720)

        # --- System Managers ---
        self.chatbot = ChatbotManager()
        self.printer = PDFPrinter()
        self.db = FirebaseManager()

        # --- State Variables ---
        self.current_found_items = []
        self.current_session_id = str(uuid.uuid4())
        self.auth_mode = "login"  # "login" or "register"
        self.sidebar_expanded = True
        
        # Local fallback for history in case Firebase fails
        self._local_chats = {} 

        # --- Setup UI & Fonts ---
        self.setup_fonts()
        self.build_login_screen()
        self.build_app_screen()

        # Start at Login View (Or guest fallback if user skips)
        self.app_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    def setup_fonts(self):
        """Initializes CustomTkinter font objects for consistent hierarchy."""
        self.title_font = ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold")
        self.subtitle_font = ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
        self.normal_font = ctk.CTkFont(family=FONT_FAMILY, size=12)
        self.large_font = ctk.CTkFont(family=FONT_FAMILY, size=15)
        self.small_font = ctk.CTkFont(family=FONT_FAMILY, size=11)

    # =========================================================================
    # 1. AUTHENTICATION SCREEN (LOGIN / REGISTER)
    # =========================================================================
    def build_login_screen(self):
        """Builds a centered, high-tech login and registration card."""
        self.login_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)

        # Centered Auth Card Container
        card = ctk.CTkFrame(
            self.login_frame,
            fg_color=COLOR_CARD,
            corner_radius=16,
            border_width=1,
            border_color="#2B2D31",
            width=420,
            height=560,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Logo / Header
        try:
            logo_path = os.path.join(ASSETS_DIR, "shelfy.png")
            pil_img = Image.open(logo_path)
            self.auth_icon = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(70, 70))
            ctk.CTkLabel(card, image=self.auth_icon, text="").pack(pady=(25, 5))
        except Exception:
            ctk.CTkLabel(card, text="🤖", font=ctk.CTkFont(size=48)).pack(pady=(20, 5))

        self.auth_header_label = ctk.CTkLabel(
            card, text="Welcome to Shelfy AI", font=self.title_font, text_color=COLOR_TEXT_PRIMARY
        )
        self.auth_header_label.pack(pady=(0, 2))

        self.auth_sub_label = ctk.CTkLabel(
            card, text="Your Intelligent In-Store Shopping Assistant", font=self.normal_font, text_color=COLOR_TEXT_SECONDARY
        )
        self.auth_sub_label.pack(pady=(0, 20))

        # Inputs
        self.email_entry = ctk.CTkEntry(
            card, width=320, height=42, placeholder_text="Email Address", corner_radius=8
        )
        self.email_entry.pack(pady=6)

        self.password_entry = ctk.CTkEntry(
            card, width=320, height=42, placeholder_text="Password", show="*", corner_radius=8
        )
        self.password_entry.pack(pady=6)

        self.login_error_label = ctk.CTkLabel(
            card, text="", text_color=COLOR_STATUS_ERROR, font=self.small_font, wraplength=310
        )
        self.login_error_label.pack(pady=2)

        # Action Buttons
        self.primary_auth_btn = ctk.CTkButton(
            card,
            text="Log In",
            width=320,
            height=42,
            fg_color=COLOR_ACCENT,
            hover_color="#1290AF",
            font=self.subtitle_font,
            corner_radius=8,
            command=self.handle_auth,
        )
        self.primary_auth_btn.pack(pady=(10, 6))

        self.google_btn = ctk.CTkButton(
            card,
            text="Continue with Google",
            width=320,
            height=40,
            fg_color="#2B2D31",
            hover_color="#36393E",
            text_color=COLOR_TEXT_PRIMARY,
            corner_radius=8,
            command=self.handle_google_login,
        )
        self.google_btn.pack(pady=4)

        # Guest Bypass Link
        self.guest_btn = ctk.CTkButton(
            card,
            text="Continue as Guest →",
            fg_color="transparent",
            text_color=COLOR_TEXT_SECONDARY,
            hover_color=COLOR_CARD,
            font=self.small_font,
            command=self.continue_as_guest,
        )
        self.guest_btn.pack(pady=(5, 0))

        # Mode Switcher
        self.toggle_auth_btn = ctk.CTkButton(
            card,
            text="Don't have an account? Sign Up",
            fg_color="transparent",
            text_color=COLOR_ACCENT,
            hover_color=COLOR_CARD,
            font=self.normal_font,
            command=self.toggle_auth_mode,
        )
        self.toggle_auth_btn.pack(side="bottom", pady=15)

    def toggle_auth_mode(self):
        """Switches between Login and Sign-Up screens."""
        self.login_error_label.configure(text="")
        if self.auth_mode == "login":
            self.auth_mode = "register"
            self.auth_header_label.configure(text="Create Account")
            self.auth_sub_label.configure(text="Sign up to save shopping trips")
            self.primary_auth_btn.configure(text="Sign Up")
            self.toggle_auth_btn.configure(text="Already have an account? Log In")
        else:
            self.auth_mode = "login"
            self.auth_header_label.configure(text="Welcome to Shelfy AI")
            self.auth_sub_label.configure(text="Your Intelligent In-Store Shopping Assistant")
            self.primary_auth_btn.configure(text="Log In")
            self.toggle_auth_btn.configure(text="Don't have an account? Sign Up")

    def handle_auth(self):
        """Handles authentication submission."""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            self.login_error_label.configure(text="Please fill in both email and password.", text_color=COLOR_STATUS_ERROR)
            return

        if self.auth_mode == "login":
            success, msg = self.db.login(email, password)
        else:
            success, msg = self.db.register(email, password)

        if success:
            self.login_error_label.configure(text="")
            self.enter_app_view()
        else:
            self.login_error_label.configure(text=msg, text_color=COLOR_STATUS_ERROR)

    def handle_google_login(self):
        """Simulates or invokes Google OAuth login."""
        self.login_error_label.configure(text="Connecting to Google Sign-In...", text_color=COLOR_ACCENT)
        self.update()

        success, msg = self.db.login_with_google()
        if success:
            self.enter_app_view()
        else:
            self.login_error_label.configure(text=msg, text_color=COLOR_STATUS_ERROR)

    def continue_as_guest(self):
        """Allows users to enter application without authenticating."""
        self.db.current_user = {"email": "guest@smartmart.ai", "name": "Guest User"}
        self.enter_app_view()

    def enter_app_view(self):
        """Transition into main app view."""
        self.login_frame.pack_forget()
        self.app_frame.pack(fill="both", expand=True)

        user = getattr(self.db, "current_user", None)
        email = user.get("email", "Guest") if isinstance(user, dict) else "Guest User"
        self.user_email_lbl.configure(text=email)

        self.start_new_chat()
        self.load_sidebar_history()

    # =========================================================================
    # 2. MAIN APPLICATION INTERFACE (SIDEBAR + CHAT WORKSPACE)
    # =========================================================================
    def build_app_screen(self):
        """Constructs modern ChatGPT layout: Sidebar on left, Chat window on right."""
        self.app_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)

        # --- A. SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self.app_frame, width=260, fg_color="#18191C", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Header / New Chat
        sidebar_top = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_top.pack(fill="x", padx=15, pady=(15, 10))

        app_brand = ctk.CTkLabel(
            sidebar_top, text="⚡ Shelfy AI", font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"), text_color=COLOR_TEXT_PRIMARY
        )
        app_brand.pack(side="left")

        # New Chat Button
        new_chat_btn = ctk.CTkButton(
            self.sidebar,
            text="+ New Shopping Trip",
            fg_color=COLOR_ACCENT,
            hover_color="#0051CA",
            text_color=COLOR_BACKGROUND,
            font=self.subtitle_font,
            corner_radius=8,
            height=38,
            command=self.start_new_chat,
        )
        new_chat_btn.pack(fill="x", padx=15, pady=(5, 10))

        # Search Filter for History
        self.history_search_entry = ctk.CTkEntry(
            self.sidebar,
            placeholder_text="🔍 Filter trips...",
            height=30,
            font=self.small_font,
            fg_color="#202225",
            border_width=0,
            text_color="white",
        )
        self.history_search_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.history_search_entry.bind("<KeyRelease>", self.filter_sidebar_history)

        # Scrollable Trip List
        ctk.CTkLabel(
            self.sidebar, text="TRIP HISTORY", font=self.small_font, text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.history_scroll = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True, padx=8, pady=0)

        # User Profile Footer Bar
        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="#111214", height=60, corner_radius=0)
        sidebar_footer.pack(side="bottom", fill="x")

        self.user_avatar = ctk.CTkLabel(
            sidebar_footer, text="👤", font=ctk.CTkFont(size=20), width=35
        )
        self.user_avatar.pack(side="left", padx=(10, 5), pady=10)

        self.user_email_lbl = ctk.CTkLabel(
            sidebar_footer, text="user@smartmart.ai", font=self.small_font, text_color=COLOR_TEXT_PRIMARY
        )
        self.user_email_lbl.pack(side="left", anchor="w", padx=5)

        logout_btn = ctk.CTkButton(
            sidebar_footer,
            text="🚪",
            width=30,
            fg_color="transparent",
            hover_color="#2B2D31",
            command=self.logout,
        )
        logout_btn.pack(side="right", padx=10)

        # --- B. MAIN CONTENT CHAT WORKSPACE ---
        self.main_content = ctk.CTkFrame(self.app_frame, fg_color=COLOR_BACKGROUND)
        self.main_content.pack(side="right", fill="both", expand=True)

        self.build_chat_header()
        self.build_chat_area()
        self.build_input_bar()

    def build_chat_header(self):
        """Top action bar for session options and cart metrics."""
        self.header_frame = ctk.CTkFrame(self.main_content, height=55, fg_color="#1E1F23", corner_radius=0)
        self.header_frame.pack(fill="x", side="top")

        # Session Indicator
        self.session_title_lbl = ctk.CTkLabel(
            self.header_frame, text="Current Trip: New Shopping List", font=self.subtitle_font, text_color=COLOR_TEXT_PRIMARY
        )
        self.session_title_lbl.pack(side="left", padx=20, pady=12)

        # Right Action Widgets
        actions_sub = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        actions_sub.pack(side="right", padx=15)

        # Cart Badge - NO PRICE
        self.cart_badge = ctk.CTkLabel(
            actions_sub, text="🛒 Cart: 0 items", font=self.subtitle_font, text_color=COLOR_STATUS_OK
        )
        self.cart_badge.pack(side="left", padx=15)

        export_btn = ctk.CTkButton(
            actions_sub,
            text="📄 Export PDF",
            width=100,
            height=32,
            fg_color="#27AE60",
            hover_color="#219150",
            font=self.small_font,
            command=self.export_pdf,
        )
        export_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            actions_sub,
            text="🧹 Clear Chat",
            width=90,
            height=32,
            fg_color="#36393E",
            hover_color="#4F545C",
            font=self.small_font,
            command=self.clear_current_chat_view,
        )
        clear_btn.pack(side="left", padx=5)

    def build_chat_area(self):
        """Main scrollable container for conversational chat bubbles."""
        self.chat_scroll = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.chat_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Empty State Container (Quick Prompt Chips)
        self.empty_state_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        self.empty_state_frame.pack(expand=True, fill="both", pady=40)

        welcome_lbl = ctk.CTkLabel(
            self.empty_state_frame,
            text="Hi there! What's on your shopping list today?",
            font=self.title_font,
            text_color=COLOR_TEXT_PRIMARY,
        )
        welcome_lbl.pack(pady=(20, 10))

        # UPDATED SUBTITLE: Focusing strictly on finding locations
        sub_welcome = ctk.CTkLabel(
            self.empty_state_frame,
            text="Just tell me what you need, and I will find its exact shelf location for you.",
            font=self.normal_font,
            text_color=COLOR_TEXT_SECONDARY,
        )
        sub_welcome.pack(pady=(0, 25))

        # Prompt Suggestion Chips Grid - UPDATED TO "FINDING" MESSAGES
        chips_frame = ctk.CTkFrame(self.empty_state_frame, fg_color="transparent")
        chips_frame.pack()

        prompts = [
            "🥛 Where is the organic milk?",
            "🍝 Find the pasta",
            "🧼 Locate laundry detergent",
            "🍎 Which shelf has fresh apples?",
        ]

        for p_text in prompts:
            chip = ctk.CTkButton(
                chips_frame,
                text=p_text,
                fg_color=COLOR_CARD,
                hover_color="#2B2D31",
                text_color=COLOR_TEXT_PRIMARY,
                border_width=1,
                border_color="#36393E",
                corner_radius=20,
                height=38,
                font=self.small_font,
                command=lambda txt=p_text: self.send_suggested_prompt(txt),
            )
            chip.pack(pady=6, fill="x")

    def build_input_bar(self):
        """Floating rounded input bar at the bottom."""
        self.input_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.input_container.pack(fill="x", side="bottom", padx=20, pady=(0, 15))

        input_card = ctk.CTkFrame(
            self.input_container, fg_color=COLOR_CARD, corner_radius=20, border_width=1, border_color="#36393E"
        )
        input_card.pack(fill="x")

        # Fixed Visibility - Added text_color="white"
        self.user_input_entry = ctk.CTkEntry(
            input_card,
            placeholder_text="Let's find your groceries! What are we looking for?",
            font=self.large_font,
            fg_color="transparent",
            text_color="white",  
            border_width=0,
            height=45,
        )
        self.user_input_entry.pack(side="left", fill="x", expand=True, padx=(15, 5))
        self.user_input_entry.bind("<Return>", lambda event: self.on_send_message())

        self.send_btn = ctk.CTkButton(
            input_card,
            text="Send ➔",
            width=80,
            height=34,
            fg_color=COLOR_ACCENT,
            hover_color="#00A3CC",
            text_color=COLOR_BACKGROUND,
            font=self.subtitle_font,
            corner_radius=15,
            command=self.on_send_message,
        )
        self.send_btn.pack(side="right", padx=8, pady=5)

    # =========================================================================
    # 3. CHAT LOGIC & MESSAGE BUBBLES
    # =========================================================================
    def send_suggested_prompt(self, text: str):
        """Handles clicking one of the welcome state suggestion chips."""
        # Clean text removing emoji
        clean_text = text.split(" ", 1)[-1] if " " in text else text
        self.user_input_entry.delete(0, "end")
        self.user_input_entry.insert(0, clean_text)
        self.on_send_message()

    def on_send_message(self):
        """Processes user message send event."""
        text = self.user_input_entry.get().strip()
        if not text:
            return

        # Hide empty welcome state if present
        if self.empty_state_frame.winfo_viewable():
            self.empty_state_frame.pack_forget()

        # Clear entry
        self.user_input_entry.delete(0, "end")

        # 1. Render User Speech Bubble
        self.append_user_bubble(text)

        # 2. Render Assistant Bubble placeholder with Typing Indicator
        typing_card, typing_label = self.append_assistant_placeholder()

        self.animator = TypingAnimator(typing_label, "Shelfy is scanning store inventory")
        self.animator.start(delay=300)

        # 3. Delay simulated response processing
        self.after(1200, lambda: self.process_assistant_response(text, typing_card))

    def append_user_bubble(self, message: str):
        """Appends a right-aligned user speech bubble."""
        row_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=8)

        bubble = ctk.CTkFrame(row_frame, fg_color="#2B2D31", corner_radius=16)
        bubble.pack(side="right", anchor="e", padx=(80, 5))

        lbl = ctk.CTkLabel(
            bubble, text=message, font=self.large_font, text_color=COLOR_TEXT_PRIMARY, wraplength=550, justify="left"
        )
        lbl.pack(padx=16, pady=10)

        self.scroll_chat_to_bottom()
   

    def handle_suggestion_click(self, confirmed_word: str):
        """Triggered when the user clicks the suggestion button."""
        # 1. Place the confirmed word into the input box
        self.user_input_entry.delete(0, "end")
        self.user_input_entry.insert(0, confirmed_word)
        
        # 2. Trigger your main send function. This automatically handles 
        # creating the user bubble, the typing animation, and fetching data!
        self.on_send_message() 

    def append_assistant_placeholder(self) -> tuple:
        """Appends a left-aligned assistant bubble placeholder."""
        row_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=8)

        # Avatar - Increased size and forced text_color to white for visibility
        avatar = ctk.CTkLabel(
            row_frame, 
            text="🤖", 
            font=ctk.CTkFont(size=28), 
            text_color="white"
        )
        avatar.pack(side="left", anchor="n", padx=(5, 8))

        bubble = ctk.CTkFrame(row_frame, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color="#2B2D31")
        bubble.pack(side="left", anchor="w", padx=(0, 80))

        status_lbl = ctk.CTkLabel(
            bubble, text="Shelfy is thinking...", font=self.normal_font, text_color=COLOR_ACCENT
        )
        status_lbl.pack(padx=16, pady=10, anchor="w")

        self.scroll_chat_to_bottom()
        return bubble, status_lbl

    def process_assistant_response(self, user_text: str, bubble_frame: ctk.CTkFrame):
        """Processes query via ChatbotManager backend and renders formatted result."""
        self.animator.stop()

        # Update Session Title for Saving Logic
        current_title = self.session_title_lbl.cget("text")
        if "New Shopping List" in current_title:
            # Set a dynamic title on the first message
            chat_title = user_text[:24] + "..." if len(user_text) > 24 else user_text
            self.session_title_lbl.configure(text=f"Trip: {chat_title}")
        else:
            chat_title = current_title.replace("Trip: ", "")

        # Call NLP / Backend
        response = self.chatbot.process_input(user_text)

        # Clear placeholder contents inside bubble_frame
        for w in bubble_frame.winfo_children():
            w.destroy()

        # Bot Response Text Message
        bot_msg = response.get("message", "Here is what I found for your list:")
        msg_lbl = ctk.CTkLabel(
            bubble_frame, text=bot_msg, font=self.large_font, text_color=COLOR_TEXT_PRIMARY, wraplength=550, justify="left"
        )
        msg_lbl.pack(padx=16, pady=(12, 8), anchor="w")

        # Items Found
        found_items = response.get("found_items", [])
        if found_items:
            items_container = ctk.CTkFrame(bubble_frame, fg_color="transparent")
            items_container.pack(fill="x", padx=12, pady=(0, 12))

            for item in found_items:
                self.create_item_card(items_container, item)

            # Accumulate items globally
            self.current_found_items.extend(found_items)
            self.update_cart_display()

        # --- UPDATED: Clickable Suggestions ---
        # --- UPDATED: Clickable Suggestions with YES / NO buttons ---
        suggestions = response.get("suggestions", [])
        for sug in suggestions:
            suggested_word = sug.get("suggestion")
            original_word = sug.get("original")
            
            sug_card = ctk.CTkFrame(bubble_frame, fg_color="#2B2D31", corner_radius=8)
            sug_card.pack(fill="x", padx=12, pady=4)
            
            lbl = ctk.CTkLabel(
                sug_card,
                text=f"💡 I couldn't find '{original_word}'. Did you mean:",
                font=self.small_font,
                text_color="#FF9800",
            )
            lbl.pack(padx=10, pady=(6, 0), anchor="w")
            
            # --- Container to hold buttons side-by-side ---
            btn_frame = ctk.CTkFrame(sug_card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(4, 6))
            
            # The YES Button
            yes_btn = ctk.CTkButton(
                btn_frame,
                text=f"Yes, search for '{suggested_word}'",
                font=self.small_font,
                fg_color="#00E676",
                text_color="black",
                hover_color="#00C853",
                height=28,
                corner_radius=8,
                command=lambda w=suggested_word: self.handle_suggestion_click(w)
            )
            yes_btn.pack(side="left", padx=(0, 8))

            # The NO Button
            no_btn = ctk.CTkButton(
                btn_frame,
                text="No, ignore",
                font=self.small_font,
                fg_color="#3A1C1C",       # Dark reddish background
                text_color="#FF6B6B",     # Light red text
                hover_color="#5C2B2B",
                height=28,
                corner_radius=8,
                # Destroy this specific suggestion card when clicked
                command=lambda card=sug_card: card.destroy() 
            )
            no_btn.pack(side="left")

        # Not Found items
        not_found = response.get("not_found", [])
        for nf in not_found:
            nf_card = ctk.CTkFrame(bubble_frame, fg_color="#2D1A1A", corner_radius=8)
            nf_card.pack(fill="x", padx=12, pady=4)
            lbl = ctk.CTkLabel(
                nf_card,
                text=f"❌ Item not available in store database: '{nf.get('original')}'",
                font=self.small_font,
                text_color=COLOR_STATUS_ERROR,
            )
            lbl.pack(padx=10, pady=6, anchor="w")

        # Save to local memory
        self._local_chats[self.current_session_id] = {
            "title": chat_title,
            "items": list(self.current_found_items) 
        }

        # Save to Firebase
        try:
            self.db.save_chat_history(self.current_session_id, chat_title, self.current_found_items)
        except Exception as e:
            print(f"Warning: Could not save to Firebase Database: {e}")
            
        # Reload Sidebar
        self.load_sidebar_history()
        self.scroll_chat_to_bottom()
        
    def create_item_card(self, parent: ctk.CTkFrame, item: dict):
        """Creates a stylish product card emphasizing ONLY the shelf."""
        card = ctk.CTkFrame(parent, fg_color="#18191C", corner_radius=10, border_width=1, border_color="#2B2D31")
        card.pack(fill="x", pady=4)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=15, pady=12, fill="x", expand=True)

        name = item.get("name", "Unknown Product")
        shelf = item.get("shelf", "N/A")

        name_lbl = ctk.CTkLabel(info, text=name, font=self.subtitle_font, text_color=COLOR_TEXT_PRIMARY)
        name_lbl.pack(anchor="w", pady=(0, 4))

        # Only showing the shelf now
        details_lbl = ctk.CTkLabel(
            info,
            text=f"📍 Shelf: {shelf}",
            font=self.large_font,
            text_color=COLOR_ACCENT,
        )
        details_lbl.pack(anchor="w")

    def update_cart_display(self):
        """Recalculates cart items, excluding cost metrics."""
        count = len(self.current_found_items)
        self.cart_badge.configure(text=f"🛒 Cart: {count} items")

    def scroll_chat_to_bottom(self):
        """Forces scroll view to animate/jump to latest messages."""
        self.update_idletasks()
        try:
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # =========================================================================
    # 4. SIDEBAR & SESSION MANAGEMENT
    # =========================================================================
    def load_sidebar_history(self):
        """Fetches chat history and populates sidebar entries (using local fallback)."""
        for child in self.history_scroll.winfo_children():
            child.destroy()

        # Combine local cache and Firebase data
        all_chats = dict(self._local_chats)
        try:
            db_chats = self.db.get_all_chats()
            if isinstance(db_chats, dict):
                all_chats.update(db_chats)
        except Exception as e:
            print(f"Warning: Failed to fetch history from Firebase: {e}")

        if not all_chats:
            ctk.CTkLabel(
                self.history_scroll, text="No previous saved trips", font=self.small_font, text_color=COLOR_TEXT_SECONDARY
            ).pack(pady=15)
            return

        # Render list items
        for session_id, chat_data in reversed(list(all_chats.items())):
            self.create_history_item(session_id, chat_data)

    def create_history_item(self, session_id: str, chat_data: dict):
        """Renders an individual history item row in the sidebar."""
        title = chat_data.get("title", "Grocery Trip")

        row = ctk.CTkFrame(self.history_scroll, fg_color="transparent")
        row.pack(fill="x", pady=2)

        # Active session highlighting
        bg_col = "#2B2D31" if session_id == self.current_session_id else "transparent"

        btn = ctk.CTkButton(
            row,
            text=f"💬 {title}",
            anchor="w",
            fg_color=bg_col,
            hover_color="#2B2D31",
            text_color=COLOR_TEXT_PRIMARY,
            font=self.small_font,
            height=32,
            command=lambda s_id=session_id, data=chat_data: self.load_chat_session(s_id, data),
        )
        btn.pack(side="left", fill="x", expand=True)

        # Delete Session Icon Button
        del_btn = ctk.CTkButton(
            row,
            text="🗑",
            width=26,
            height=32,
            fg_color="transparent",
            hover_color="#3A1C1C",
            text_color=COLOR_TEXT_SECONDARY,
            command=lambda s_id=session_id: self.delete_session(s_id),
        )
        del_btn.pack(side="right")

    def filter_sidebar_history(self, event=None):
        """Filters sidebar trip history based on search query."""
        query = self.history_search_entry.get().strip().lower()
        
        all_chats = dict(self._local_chats)
        try:
            db_chats = self.db.get_all_chats()
            if isinstance(db_chats, dict):
                all_chats.update(db_chats)
        except Exception:
            pass

        for child in self.history_scroll.winfo_children():
            child.destroy()

        if not all_chats:
            return

        for session_id, chat_data in reversed(list(all_chats.items())):
            title = chat_data.get("title", "Grocery Trip")
            if query in title.lower():
                self.create_history_item(session_id, chat_data)

    def load_chat_session(self, session_id: str, chat_data: dict):
        """Restores a historical chat session into the workspace."""
        self.current_session_id = session_id
        self.clear_current_chat_view()

        items = chat_data.get("items", [])
        self.current_found_items = items
        self.update_cart_display()

        title = chat_data.get("title", "Grocery Trip")
        self.session_title_lbl.configure(text=f"Trip: {title}")

        # Hide empty state frame
        self.empty_state_frame.pack_forget()

        # Render loaded query message & restored items card stack
        self.append_user_bubble(f"Restored saved list: '{title}'")

        row_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=8)

        avatar = ctk.CTkLabel(row_frame, text="🤖", font=ctk.CTkFont(size=24))
        avatar.pack(side="left", anchor="n", padx=(5, 8))

        bubble = ctk.CTkFrame(row_frame, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color="#2B2D31")
        bubble.pack(side="left", anchor="w", padx=(0, 80))

        msg_lbl = ctk.CTkLabel(
            bubble, text=f"Here are the items saved for this session:", font=self.large_font, text_color=COLOR_TEXT_PRIMARY
        )
        msg_lbl.pack(padx=16, pady=(12, 8), anchor="w")

        items_container = ctk.CTkFrame(bubble, fg_color="transparent")
        items_container.pack(fill="x", padx=12, pady=(0, 12))

        for item in items:
            self.create_item_card(items_container, item)

        self.load_sidebar_history()
        self.scroll_chat_to_bottom()

    def delete_session(self, session_id: str):
        """Deletes a session from cloud DB (and local cache) and updates UI."""
        if session_id in self._local_chats:
            del self._local_chats[session_id]
            
        try:
            self.db.delete_chat_session(session_id)
        except Exception as e:
            print(f"Warning: Failed to delete from Firebase: {e}")
            
        if session_id == self.current_session_id:
            self.start_new_chat()
        else:
            self.load_sidebar_history()

    def start_new_chat(self):
        """Resets workspace for a fresh shopping trip session."""
        self.current_session_id = str(uuid.uuid4())
        self.clear_current_chat_view()
        self.session_title_lbl.configure(text="Current Trip: New Shopping List")

        # Show empty welcome state
        self.empty_state_frame.pack(expand=True, fill="both", pady=40)
        self.load_sidebar_history()

    def clear_current_chat_view(self):
        """Clears all speech bubbles from scroll container."""
        for child in self.chat_scroll.winfo_children():
            if child != self.empty_state_frame:
                child.destroy()

        self.current_found_items = []
        self.update_cart_display()

    def logout(self):
        """Logs out the current user and returns to Auth Screen."""
        self.db.current_user = None
        self.app_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)

    # =========================================================================
    # 5. PDF EXPORT HANDLER
    # =========================================================================
    def export_pdf(self):
        """Exports the current found items list to a PDF document."""
        if not self.current_found_items:
            tk.messagebox.showwarning("Cart Empty", "Your current trip cart is empty. Add items before exporting.")
            return

        try:
            # FIX: Reverted to 1 parameter call based on your original PDFPrinter configuration
            filepath = self.printer.generate_pdf(self.current_found_items)
            
            if filepath:
                tk.messagebox.showinfo("Export Successful", f"Shopping list exported successfully to:\n{filepath}")
            else:
                tk.messagebox.showerror("Export Failed", "Failed to generate PDF file.")
        except Exception as e:
            tk.messagebox.showerror("Export Error", f"An error occurred while generating PDF:\n{e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = ShelfyGUI()
    app.mainloop()