#!/usr/bin/env python
"""
Very simple GUI test
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
import os

print("Starting simple test...")

class VerySimpleGUI:
    def __init__(self, root):
        print("Creating GUI...")
        self.root = root
        self.root.title("Simple Test")
        self.root.geometry("400x300")
        
        # Just a button and text area
        self.button = ttk.Button(root, text="Click Me!", command=self.button_click)
        self.button.pack(pady=20)
        
        self.text = scrolledtext.ScrolledText(root, height=10)
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text.insert(tk.END, "Simple GUI loaded!\n")
        self.text.insert(tk.END, "Click the button to test.\n")
        print("GUI created successfully")
        
    def button_click(self):
        print("Button clicked! (console)")
        self.text.insert(tk.END, "Button clicked! (GUI)\n")
        self.text.see(tk.END)
        
        # Test the imports
        try:
            print("Testing imports...")
            from log_converter import ContentProcessor
            self.text.insert(tk.END, "✓ Import successful\n")
            print("✓ Import successful")
        except Exception as e:
            self.text.insert(tk.END, f"✗ Import failed: {e}\n")
            print(f"✗ Import failed: {e}")

def main():
    print("Creating tkinter root...")
    root = tk.Tk()
    print("Root created")
    
    app = VerySimpleGUI(root)
    print("Starting mainloop...")
    root.mainloop()
    print("Mainloop ended")

if __name__ == "__main__":
    main() 