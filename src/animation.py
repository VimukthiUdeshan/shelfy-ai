# src/animation.py

import customtkinter as ctk
from typing import List

class TypingAnimator:
    """
    Handles dynamic text animations for labels, creating a typing 
    or "thinking" effect using Tkinter's event loop.
    """

    def __init__(self, target_label: ctk.CTkLabel, base_text: str = "AI is thinking"):
        """
        Initializes the animator.

        Args:
            target_label (ctk.CTkLabel): The CustomTkinter label to animate.
            base_text (str): The static base text (e.g., "AI is thinking").
        """
        self.label = target_label
        self.base_text = base_text
        self.is_animating = False
        self.dot_count = 0
        self._after_id = None

    def start(self, delay: int = 400):
        """
        Starts the typing animation.

        Args:
            delay (int): Milliseconds between frame updates.
        """
        self.is_animating = True
        self._animate(delay)

    def _animate(self, delay: int):
        """
        Internal loop for the animation sequence. Updates the label text.
        """
        if not self.is_animating:
            return

        # Create cycling dots (0 to 3 dots)
        dots = "." * (self.dot_count % 4)
        self.label.configure(text=f"{self.base_text}{dots}")
        self.dot_count += 1

        # Schedule the next frame recursively
        self._after_id = self.label.after(delay, self._animate, delay)

    def stop(self, final_text: str = ""):
        """
        Stops the animation safely and sets an optional final static text.

        Args:
            final_text (str): The text to display when animation terminates.
        """
        self.is_animating = False
        
        # Cancel pending Tkinter after() callbacks to prevent memory leaks
        if self._after_id:
            self.label.after_cancel(self._after_id)
            self._after_id = None
            
        if final_text:
            self.label.configure(text=final_text)


class SequentialRevealer:
    """
    Handles staggered, sequential appearance animations for a list of widgets, 
    making search results pop up one by one.
    """

    def __init__(self, root_window: ctk.CTk, delay_ms: int = 300):
        """
        Initializes the revealer.

        Args:
            root_window (ctk.CTk): The master window executing the 'after' loop.
            delay_ms (int): Delay in milliseconds between each widget's appearance.
        """
        self.root = root_window
        self.delay = delay_ms

    def reveal(self, widgets: List[ctk.CTkFrame], pack_options: dict = None):
        """
        Reveals widgets sequentially by calling pack() on them one by one.

        Args:
            widgets (List[ctk.CTkFrame]): The UI components (e.g., result cards) to reveal.
            pack_options (dict): Options to pass to the pack() geometry manager.
        """
        if pack_options is None:
            pack_options = {"pady": 5, "fill": "x", "padx": 10}

        self._reveal_step(widgets, 0, pack_options)

    def _reveal_step(self, widgets: List[ctk.CTkFrame], index: int, pack_options: dict):
        """
        Recursive internal step function triggering the next widget's appearance.
        """
        if index < len(widgets):
            # Display the current widget safely
            try:
                widgets[index].pack(**pack_options)
            except Exception as e:
                print(f"Animation reveal error: {e}")
                return
            
            # Schedule the next widget appearance
            self.root.after(
                self.delay, 
                self._reveal_step, 
                widgets, 
                index + 1, 
                pack_options
            )