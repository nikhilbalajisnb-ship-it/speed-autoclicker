#!/usr/bin/env python3
"""
Core AutoClicker logic for macOS
Handles clicking simulation and hotkey detection with optimized timing
"""

import threading
import time
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key
import json
from pathlib import Path


class AutoClicker:
    """Main AutoClicker class for macOS with optimized Roblox support"""
    
    def __init__(self, config):
        """
        Initialize the AutoClicker
        
        Args:
            config (dict): Configuration dictionary with cps, cdc, hotkey settings
        """
        self.config = config
        self.mouse = Controller()
        self.listener = None
        
        # Clicking state
        self.is_clicking = False
        self.clicking_thread = None
        
        # Callbacks
        self.on_toggle_callback = None
        self.on_error_callback = None
        
        # Parse initial hotkey
        self.hotkey = config.get("hotkey", "q").lower()
        self.cps = config.get("cps", 10.0)
        self.cdc = config.get("cdc", 100.0)
        self.timing_mode = config.get("timing_mode", "balanced")  # "precision", "balanced", "aggressive"
        
        # Start listening to keyboard
        self._start_listener()
    
    def _start_listener(self):
        """Start listening to keyboard events"""
        try:
            self.listener = Listener(on_press=self._on_key_press)
            self.listener.start()
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"Error starting listener: {e}")
    
    def _on_key_press(self, key):
        """
        Handle key press events
        
        Args:
            key: The key that was pressed
        """
        try:
            # Get the character representation
            if hasattr(key, 'char') and key.char:
                char = key.char.lower()
            else:
                return
            
            # Check if it matches the hotkey
            if char == self.hotkey:
                self.toggle_clicking()
        except AttributeError:
            pass
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"Error in key press handler: {e}")
    
    def toggle_clicking(self):
        """Toggle clicking on/off"""
        self.is_clicking = not self.is_clicking
        
        if self.is_clicking:
            self._start_clicking()
        else:
            self._stop_clicking()
        
        if self.on_toggle_callback:
            self.on_toggle_callback(self.is_clicking)
    
    def _start_clicking(self):
        """Start the clicking thread"""
        if self.clicking_thread is None or not self.clicking_thread.is_alive():
            self.clicking_thread = threading.Thread(target=self._click_loop, daemon=True)
            self.clicking_thread.start()
    
    def _stop_clicking(self):
        """Stop the clicking thread"""
        self.is_clicking = False
    
    def _calculate_delays(self):
        """
        Calculate optimal delays based on timing mode
        
        Returns:
            tuple: (pre_delay, click_delay, post_delay)
        """
        # CPS delay calculation
        cps_delay = (1.0 / self.cps) if self.cps > 0 else 1.0
        cdc_delay = self.cdc / 1000.0  # Convert milliseconds to seconds
        
        if self.timing_mode == "precision":
            # Precision mode: Maximum accuracy, slight delay before click
            # Pre-delay: minimal, Post-delay: full delay split
            pre_delay = 0.001  # 1ms minimal pre-delay
            click_delay = 0.001  # Fast click registration
            post_delay = max(0, cps_delay + cdc_delay - pre_delay)
            
        elif self.timing_mode == "aggressive":
            # Aggressive mode: Minimum latency, click first then wait
            # Best for Roblox - immediate feedback
            pre_delay = 0.0  # No pre-delay
            click_delay = 0.0  # Instant click
            post_delay = cps_delay + cdc_delay
            
        else:  # balanced (default)
            # Balanced mode: Good response with stability
            pre_delay = 0.0005  # 0.5ms pre-delay
            click_delay = 0.0005  # 0.5ms click response
            post_delay = max(0, cps_delay + cdc_delay - pre_delay)
        
        return pre_delay, click_delay, post_delay
    
    def _click_loop(self):
        """Main clicking loop optimized for Roblox"""
        try:
            pre_delay, click_delay, post_delay = self._calculate_delays()
            
            while self.is_clicking:
                # Pre-click delay (minimal)
                if pre_delay > 0:
                    time.sleep(pre_delay)
                
                # Perform click - use immediate approach for low latency
                try:
                    self.mouse.click(Button.left, 1)
                except Exception:
                    pass
                
                # Click registration delay
                if click_delay > 0:
                    time.sleep(click_delay)
                
                # Post-click delay (remaining time until next click)
                if post_delay > 0:
                    time.sleep(post_delay)
                    
        except Exception as e:
            self.is_clicking = False
            if self.on_error_callback:
                self.on_error_callback(f"Error in click loop: {e}")
    
    def set_cps(self, cps):
        """
        Set clicks per second
        
        Args:
            cps (float): Clicks per second (e.g., 64.26)
        """
        try:
            cps = float(cps)
            if cps <= 0:
                raise ValueError("CPS must be greater than 0")
            self.cps = cps
            self.config['cps'] = cps
            self._save_config()
        except ValueError as e:
            if self.on_error_callback:
                self.on_error_callback(f"Invalid CPS value: {e}")
    
    def set_cdc(self, cdc):
        """
        Set click delay/cooldown in milliseconds
        
        Args:
            cdc (float): Click delay in milliseconds (e.g., 15.5)
        """
        try:
            cdc = float(cdc)
            if cdc < 0:
                raise ValueError("CDC cannot be negative")
            self.cdc = cdc
            self.config['cdc'] = cdc
            self._save_config()
        except ValueError as e:
            if self.on_error_callback:
                self.on_error_callback(f"Invalid CDC value: {e}")
    
    def set_hotkey(self, hotkey):
        """
        Set the activation hotkey
        
        Args:
            hotkey (str): The key to use as hotkey (e.g., 'q', 'r', '1')
        """
        try:
            if not hotkey or len(hotkey) != 1:
                raise ValueError("Hotkey must be a single character")
            self.hotkey = hotkey.lower()
            self.config['hotkey'] = self.hotkey
            self._save_config()
        except ValueError as e:
            if self.on_error_callback:
                self.on_error_callback(f"Invalid hotkey: {e}")
    
    def set_timing_mode(self, mode):
        """
        Set the timing mode for click registration
        
        Args:
            mode (str): Timing mode - 'precision', 'balanced', or 'aggressive'
        """
        if mode not in ["precision", "balanced", "aggressive"]:
            if self.on_error_callback:
                self.on_error_callback("Invalid timing mode. Use: precision, balanced, or aggressive")
            return
        
        self.timing_mode = mode
        self.config['timing_mode'] = mode
        self._save_config()
    
    def _save_config(self):
        """Save current configuration to config.json"""
        try:
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            if self.on_error_callback:
                self.on_error_callback(f"Error saving config: {e}")
    
    def stop(self):
        """Stop the autoclicker and cleanup"""
        self.is_clicking = False
        if self.listener:
            self.listener.stop()
