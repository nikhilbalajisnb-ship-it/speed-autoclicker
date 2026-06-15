#!/usr/bin/env python3
"""
Speed AutoClicker for macOS
Main entry point for the GUI application
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from pathlib import Path
from autoclicker import AutoClicker
from gui import AutoClickerGUI


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    # Return default config
    return {
        "cps": 10.0,
        "cdc": 100.0,
        "hotkey": "q",
        "activation_key": "cmd",
        "timing_mode": "balanced",
        "theme": "dark"
    }


def main():
    """Main entry point"""
    config = load_config()
    
    # Create root window
    root = tk.Tk()
    root.title("Speed AutoClicker")
    root.geometry("550x700")  # Larger default window
    root.resizable(True, True)  # Allow resizing
    
    # Initialize AutoClicker
    autoclicker = AutoClicker(config)
    
    # Create GUI
    gui = AutoClickerGUI(root, autoclicker, config)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
