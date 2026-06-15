#!/usr/bin/env python3
"""
GUI for the Speed AutoClicker
Built with tkinter for cross-platform compatibility
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re


class AutoClickerGUI:
    """GUI class for the AutoClicker application"""
    
    def __init__(self, root, autoclicker, config):
        """
        Initialize the GUI
        
        Args:
            root: Tkinter root window
            autoclicker: AutoClicker instance
            config: Configuration dictionary
        """
        self.root = root
        self.autoclicker = autoclicker
        self.config = config
        
        # Set up styles
        self._setup_styles()
        
        # Set up GUI elements
        self._create_widgets()
        
        # Connect callbacks
        self._setup_callbacks()
        
        # Configure window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """Set up tkinter styles"""
        style = ttk.Style()
        style.theme_use('aqua')  # Use macOS aqua theme
        
        # Define custom styles
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Normal.TLabel', font=('Helvetica', 10))
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Speed AutoClicker", style='Title.TLabel')
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # ===== CPS Section =====
        cps_label = ttk.Label(main_frame, text="CPS (Clicks Per Second)", style='Heading.TLabel')
        cps_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        
        cps_frame = ttk.Frame(main_frame)
        cps_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.cps_input = ttk.Entry(cps_frame, width=15)
        self.cps_input.insert(0, str(self.config.get('cps', 10.0)))
        self.cps_input.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cps_value_label = ttk.Label(cps_frame, text=f"Current: {self.config.get('cps', 10.0)}", style='Normal.TLabel')
        self.cps_value_label.pack(side=tk.LEFT)
        
        # Bind focus out event to validate CPS input
        self.cps_input.bind("<FocusOut>", self._on_cps_change)
        self.cps_input.bind("<Return>", self._on_cps_change)
        
        # ===== CDC Section =====
        cdc_label = ttk.Label(main_frame, text="CDC (Click Delay ms)", style='Heading.TLabel')
        cdc_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        cdc_frame = ttk.Frame(main_frame)
        cdc_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.cdc_input = ttk.Entry(cdc_frame, width=15)
        self.cdc_input.insert(0, str(self.config.get('cdc', 100.0)))
        self.cdc_input.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cdc_value_label = ttk.Label(cdc_frame, text=f"Current: {self.config.get('cdc', 100.0)}", style='Normal.TLabel')
        self.cdc_value_label.pack(side=tk.LEFT)
        
        # Bind focus out event to validate CDC input
        self.cdc_input.bind("<FocusOut>", self._on_cdc_change)
        self.cdc_input.bind("<Return>", self._on_cdc_change)
        
        # ===== Hotkey Section =====
        hotkey_label = ttk.Label(main_frame, text="Hotkey (Single Key)", style='Heading.TLabel')
        hotkey_label.grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.hotkey_input = ttk.Entry(hotkey_frame, width=15)
        self.hotkey_input.insert(0, self.config.get('hotkey', 'q'))
        self.hotkey_input.pack(side=tk.LEFT, padx=(0, 10))
        
        self.hotkey_value_label = ttk.Label(hotkey_frame, text=f"Current: {self.config.get('hotkey', 'q')}", style='Normal.TLabel')
        self.hotkey_value_label.pack(side=tk.LEFT)
        
        # Bind focus out event to validate hotkey input
        self.hotkey_input.bind("<FocusOut>", self._on_hotkey_change)
        self.hotkey_input.bind("<Return>", self._on_hotkey_change)
        
        # ===== Timing Mode Section =====
        timing_label = ttk.Label(main_frame, text="Timing Mode", style='Heading.TLabel')
        timing_label.grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        timing_frame = ttk.Frame(main_frame)
        timing_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.timing_var = tk.StringVar(value=self.config.get('timing_mode', 'balanced'))
        timing_options = ['precision', 'balanced', 'aggressive']
        timing_combo = ttk.Combobox(timing_frame, textvariable=self.timing_var, values=timing_options, state='readonly', width=12)
        timing_combo.pack(side=tk.LEFT, padx=(0, 10))
        timing_combo.bind('<<ComboboxSelected>>', self._on_timing_mode_change)
        
        timing_info = ttk.Label(timing_frame, text="Best for Roblox: Aggressive", style='Normal.TLabel')
        timing_info.pack(side=tk.LEFT)
        
        # ===== Status Section =====
        status_label = ttk.Label(main_frame, text="Status", style='Heading.TLabel')
        status_label.grid(row=9, column=0, sticky=tk.W, pady=(10, 5))
        
        self.status_label = ttk.Label(main_frame, text="🔴 IDLE (Press hotkey to start)", style='Normal.TLabel')
        self.status_label.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=(0, 20))
        
        # ===== Control Buttons =====
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.toggle_button = ttk.Button(button_frame, text="Start (Press Q)", command=self._toggle_clicking)
        self.toggle_button.pack(side=tk.LEFT, padx=(0, 10))
        
        reset_button = ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults)
        reset_button.pack(side=tk.LEFT)
        
        # ===== Info Section =====
        info_frame = ttk.LabelFrame(main_frame, text="Info", padding="10")
        info_frame.grid(row=12, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_text = ttk.Label(info_frame, text="• Default hotkey: Q\n• Decimal support: Yes (e.g., 64.26)\n• Aggressive mode has lowest latency for Roblox", style='Normal.TLabel', justify=tk.LEFT)
        info_text.pack(anchor=tk.W)
    
    def _validate_decimal_input(self, value, field_name):
        """
        Validate decimal input
        
        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            
        Returns:
            tuple: (is_valid, float_value)
        """
        try:
            # Remove whitespace
            value = value.strip()
            
            # Check if empty
            if not value:
                return False, None
            
            # Validate decimal format
            if not re.match(r'^-?\d+(\.\d+)?$', value):
                return False, None
            
            float_value = float(value)
            return True, float_value
        except (ValueError, AttributeError):
            return False, None
    
    def _on_cps_change(self, event=None):
        """Handle CPS input change"""
        value = self.cps_input.get()
        is_valid, float_value = self._validate_decimal_input(value, "CPS")
        
        if is_valid and float_value > 0:
            self.autoclicker.set_cps(float_value)
            self.cps_value_label.config(text=f"Current: {float_value}")
            self.cps_input.delete(0, tk.END)
            self.cps_input.insert(0, str(float_value))
        else:
            messagebox.showerror("Invalid Input", "CPS must be a positive decimal number")
            self.cps_input.delete(0, tk.END)
            self.cps_input.insert(0, str(self.autoclicker.cps))
    
    def _on_cdc_change(self, event=None):
        """Handle CDC input change"""
        value = self.cdc_input.get()
        is_valid, float_value = self._validate_decimal_input(value, "CDC")
        
        if is_valid and float_value >= 0:
            self.autoclicker.set_cdc(float_value)
            self.cdc_value_label.config(text=f"Current: {float_value}")
            self.cdc_input.delete(0, tk.END)
            self.cdc_input.insert(0, str(float_value))
        else:
            messagebox.showerror("Invalid Input", "CDC must be a non-negative decimal number")
            self.cdc_input.delete(0, tk.END)
            self.cdc_input.insert(0, str(self.autoclicker.cdc))
    
    def _on_hotkey_change(self, event=None):
        """Handle hotkey input change"""
        value = self.hotkey_input.get().strip()
        
        if not value or len(value) != 1:
            messagebox.showerror("Invalid Input", "Hotkey must be a single character")
            self.hotkey_input.delete(0, tk.END)
            self.hotkey_input.insert(0, self.autoclicker.hotkey)
            return
        
        if value.isspace():
            messagebox.showerror("Invalid Input", "Hotkey cannot be a space")
            self.hotkey_input.delete(0, tk.END)
            self.hotkey_input.insert(0, self.autoclicker.hotkey)
            return
        
        self.autoclicker.set_hotkey(value)
        self.hotkey_value_label.config(text=f"Current: {value.lower()}")
        self.hotkey_input.delete(0, tk.END)
        self.hotkey_input.insert(0, value.lower())
    
    def _on_timing_mode_change(self, event=None):
        """Handle timing mode change"""
        mode = self.timing_var.get()
        self.autoclicker.set_timing_mode(mode)
    
    def _toggle_clicking(self):
        """Toggle clicking on/off via button"""
        self.autoclicker.toggle_clicking()
    
    def _reset_defaults(self):
        """Reset all values to defaults"""
        self.autoclicker.set_cps(10.0)
        self.autoclicker.set_cdc(100.0)
        self.autoclicker.set_hotkey('q')
        self.autoclicker.set_timing_mode('balanced')
        
        self.cps_input.delete(0, tk.END)
        self.cps_input.insert(0, "10.0")
        self.cps_value_label.config(text="Current: 10.0")
        
        self.cdc_input.delete(0, tk.END)
        self.cdc_input.insert(0, "100.0")
        self.cdc_value_label.config(text="Current: 100.0")
        
        self.hotkey_input.delete(0, tk.END)
        self.hotkey_input.insert(0, "q")
        self.hotkey_value_label.config(text="Current: q")
        
        self.timing_var.set('balanced')
        
        messagebox.showinfo("Reset", "Settings reset to defaults")
    
    def _setup_callbacks(self):
        """Setup callbacks from autoclicker"""
        self.autoclicker.on_toggle_callback = self._on_autoclicker_toggle
        self.autoclicker.on_error_callback = self._on_autoclicker_error
    
    def _on_autoclicker_toggle(self, is_clicking):
        """Handle autoclicker toggle"""
        if is_clicking:
            self.status_label.config(text="🟢 CLICKING")
            self.toggle_button.config(text="Stop (Press Q)")
        else:
            self.status_label.config(text="🔴 IDLE (Press hotkey to start)")
            self.toggle_button.config(text="Start (Press Q)")
    
    def _on_autoclicker_error(self, error_message):
        """Handle autoclicker error"""
        messagebox.showerror("AutoClicker Error", error_message)
    
    def _on_closing(self):
        """Handle window closing"""
        self.autoclicker.stop()
        self.root.destroy()
