#!/usr/bin/env python
"""
GUI version of the Log Converter
Provides a simple interface with drag-and-drop file support and URL input
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from log_converter import ContentProcessor, get_wikitext_from_url, process_file, WIKI_API_URL
import logging

class LogConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Converter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure logging to capture in GUI
        self.log_messages = []
        
        # Variables
        self.processing = False
        
        # Create the main interface
        self.create_widgets()
        
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Log Converter", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File input section
        file_frame = ttk.LabelFrame(main_frame, text="File Input", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        # Drag and drop area
        self.drop_frame = tk.Frame(file_frame, bg="lightgray", relief="dashed", bd=2, height=60)
        self.drop_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.drop_frame.columnconfigure(0, weight=1)
        self.drop_frame.grid_propagate(False)  # Maintain fixed height
        
        drop_label = tk.Label(self.drop_frame, text="Drag and drop files here or click to browse", 
                             bg="lightgray", fg="gray")
        drop_label.grid(row=0, column=0, pady=20)
        
        # Enable drag and drop using tkinterdnd2 (fallback to click)
        self.setup_drag_drop()
        
        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="URL Input", padding="10")
        url_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Output file section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(output_frame, text="Output file:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.output_var = tk.StringVar(value="processed_log.txt")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=50)
        self.output_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Process Log", command=self.process_log)
        self.process_btn.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status/Results area
        results_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.status_text = scrolledtext.ScrolledText(results_frame, height=8, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind events
        self.file_entry.bind('<Return>', lambda e: self.process_log())
        self.url_entry.bind('<Return>', lambda e: self.process_log())
        
        # Configure drag and drop for the entire drop frame
        self.setup_drag_drop()
        
    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        # Always enable click-to-browse
        self.drop_frame.bind('<Button-1>', self.on_drop_click)
        
        # Try to enable drag and drop using tkinterdnd2 if available
        try:
            import tkinterdnd2
            from tkinterdnd2 import DND_FILES
            
            # Make the drop frame accept drops
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_file_drop)
            
        except ImportError:
            # Fallback message - drag and drop not available
            pass
        
    def on_drop_click(self, event):
        """Handle click on drop area"""
        self.browse_file()
        
    def on_file_drop(self, event):
        """Handle file drop events"""
        try:
            files = event.data.split()
            if files:
                # Clean up the file path (remove brackets and quotes)
                file_path = files[0].strip('{}')
                self.file_var.set(file_path)
                self.log_status(f"File dropped: {os.path.basename(file_path)}")
        except Exception as e:
            self.log_status(f"Error handling dropped file: {e}")
            # Fall back to browse dialog
            self.browse_file()
    
    def browse_file(self):
        """Open file dialog to select a file"""
        filename = filedialog.askopenfilename(
            title="Select Log File",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.file_var.set(filename)
            self.log_status(f"File selected: {os.path.basename(filename)}")
    
    def log_status(self, message):
        """Add a message to the status area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_status(self):
        """Clear the status area"""
        self.status_text.delete(1.0, tk.END)
    
    def process_log(self):
        """Process the log file or URL"""
        if self.processing:
            return
            
        # Validate inputs
        file_path = self.file_var.get().strip()
        url = self.url_var.get().strip()
        output_file = self.output_var.get().strip()
        
        if not file_path and not url:
            messagebox.showerror("Error", "Please select a file or enter a URL")
            return
            
        if file_path and url:
            messagebox.showerror("Error", "Please select either a file OR enter a URL, not both")
            return
            
        if not output_file:
            messagebox.showerror("Error", "Please specify an output filename")
            return
        
        # Check URL configuration if using URL
        if url and 'wiki.yourdomain.com' in WIKI_API_URL:
            messagebox.showerror("Configuration Error", 
                               "Please configure the WIKI_API_URL in log_converter.py before using URL input")
            return
        
        # Start processing in a separate thread
        self.processing = True
        self.process_btn.config(state='disabled')
        self.progress.start()
        self.clear_status()
        
        thread = threading.Thread(target=self._process_worker, args=(file_path, url, output_file))
        thread.daemon = True
        thread.start()
    
    def _process_worker(self, file_path, url, output_file):
        """Worker thread for processing"""
        try:
            self.log_status("Starting processing...")
            
            title = ""
            wikitext = ""
            
            if file_path:
                self.log_status(f"Reading file: {file_path}")
                result = process_file(file_path)
                if result:
                    title, wikitext = result
                    self.log_status("File read successfully")
                else:
                    self.log_status("Failed to read file")
                    return
                    
            elif url:
                self.log_status(f"Fetching from URL: {url}")
                result = get_wikitext_from_url(url)
                if result:
                    title, wikitext = result
                    self.log_status("URL content fetched successfully")
                else:
                    self.log_status("Failed to fetch URL content")
                    return
            
            if not wikitext:
                self.log_status("No content to process")
                return
            
            self.log_status("Processing content...")
            processor = ContentProcessor()
            processed_content = processor.process_log_content(title, wikitext)
            
            # Save output
            try:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                output_path = os.path.join(script_dir, output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                self.log_status(f"Successfully processed and saved to: {output_path}")
                self.log_status(f"Processed {len(wikitext.splitlines())} lines")
                
                # Offer to open the file
                self.root.after(0, lambda: self._ask_open_file(output_path))
                
            except Exception as e:
                self.log_status(f"Error writing output file: {e}")
                
        except Exception as e:
            self.log_status(f"Processing error: {e}")
        finally:
            # Re-enable UI
            self.root.after(0, self._processing_complete)
    
    def _processing_complete(self):
        """Called when processing is complete"""
        self.processing = False
        self.process_btn.config(state='normal')
        self.progress.stop()
    
    def _ask_open_file(self, file_path):
        """Ask if user wants to open the output file"""
        if messagebox.askyesno("Processing Complete", 
                              f"Processing complete!\n\nFile saved to:\n{file_path}\n\nWould you like to open it?"):
            try:
                if sys.platform.startswith('win'):
                    os.startfile(file_path)
                elif sys.platform.startswith('darwin'):
                    os.system(f'open "{file_path}"')
                else:
                    os.system(f'xdg-open "{file_path}"')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

def main():
    """Main GUI application entry point"""
    # Try to use tkinterdnd2 for drag and drop support
    try:
        import tkinterdnd2
        root = tkinterdnd2.TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
    
    app = LogConverterGUI(root)
    
    # Set up window icon (if available)
    try:
        root.iconbitmap(default='icon.ico')  # Add an icon file if you have one
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main() 