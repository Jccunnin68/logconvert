#!/usr/bin/env python
"""
Minimal GUI test to isolate button click issue
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

class SimpleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Button Test")
        self.root.geometry("400x300")
        
        # Create button
        self.test_btn = ttk.Button(root, text="Test Button", command=self.button_clicked)
        self.test_btn.pack(pady=20)
        
        # Status area
        self.status_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_status("GUI initialized - click the button!")
        
    def log_status(self, message):
        """Add a message to the status area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def button_clicked(self):
        """Test button click handler"""
        self.log_status("Button was clicked!")
        try:
            # Test the log converter imports
            from log_converter import ContentProcessor, process_file
            self.log_status("✓ Imports successful")
            
            # Test processing
            result = process_file("test_log.txt")
            if result:
                title, content = result
                self.log_status(f"✓ File read: {title}, {len(content)} chars")
                
                processor = ContentProcessor()
                processed = processor.process_log_content(title, content)
                self.log_status(f"✓ Processing complete: {len(processed)} chars")
            else:
                self.log_status("✗ File read failed")
                
        except Exception as e:
            self.log_status(f"✗ Error: {e}")
            import traceback
            self.log_status(traceback.format_exc())

def main():
    root = tk.Tk()
    app = SimpleGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 