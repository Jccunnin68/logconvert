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
        
        print("LogConverterGUI: Initializing...")  # Console debug
        
        # Create the main interface
        self.create_widgets()
        
        print("LogConverterGUI: Widgets created")  # Console debug
        
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
        self.drop_frame = tk.Frame(file_frame, bg="lightgray", relief="ridge", bd=2, height=60)
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
        
        ttk.Label(url_frame, text="Wiki Page URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Wiki API URL configuration
        ttk.Label(url_frame, text="Wiki API URL:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.api_url_var = tk.StringVar(value=WIKI_API_URL)
        self.api_url_entry = ttk.Entry(url_frame, textvariable=self.api_url_var, width=50)
        self.api_url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        config_btn = ttk.Button(url_frame, text="Set API", command=self.configure_api)
        config_btn.grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        help_btn = ttk.Button(url_frame, text="Help", command=self.show_url_help)
        help_btn.grid(row=0, column=2, padx=(5, 0))
        
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
        
        # Add initial status message
        self.log_status("GUI initialized successfully!")
        self.log_status("Ready to process log files...")
        self.log_status("To use URL input, configure the Wiki API URL first.")
        print("GUI ready!")  # Console debug
        
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
    
    def configure_api(self):
        """Configure the Wiki API URL"""
        api_url = self.api_url_var.get().strip()
        if not api_url:
            messagebox.showerror("Error", "Please enter a Wiki API URL")
            return
            
        if not api_url.endswith('/api.php'):
            if messagebox.askyesno("Confirm", 
                                 f"The URL doesn't end with '/api.php'.\n\nURL: {api_url}\n\nDo you want to use it anyway?"):
                pass
            else:
                return
        
        # Update the global variable
        global WIKI_API_URL
        WIKI_API_URL = api_url
        
        self.log_status(f"Wiki API URL configured: {api_url}")
        messagebox.showinfo("Success", f"Wiki API URL set to:\n{api_url}")
    
    def test_url_connection(self):
        """Test if the wiki URL is accessible"""
        api_url = self.api_url_var.get().strip()
        if not api_url:
            messagebox.showerror("Error", "Please configure the Wiki API URL first")
            return
            
        try:
            self.log_status("Testing API connection...")
            import requests
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                self.log_status("✓ API connection successful")
                messagebox.showinfo("Success", "Wiki API is accessible!")
            else:
                self.log_status(f"✗ API returned status code: {response.status_code}")
                messagebox.showerror("Error", f"API returned error: {response.status_code}")
        except Exception as e:
            self.log_status(f"✗ API connection failed: {e}")
            messagebox.showerror("Error", f"Could not connect to API:\n{e}")
    
    def show_url_help(self):
        """Show help for URL input"""
        help_text = """URL Input Help:

1. Wiki Page URL: Enter the full URL of the wiki page you want to process
   Example: https://your-wiki.com/wiki/Mission_Log_Name

2. Wiki API URL: This is the API endpoint for your MediaWiki installation
   Example: https://your-wiki.com/api.php
   
   - Click "Set API" to configure this URL
   - This only needs to be set once per session
   - The URL should end with '/api.php'

3. How it works:
   - The tool extracts the page name from the wiki page URL
   - It uses the API URL to fetch the raw wikitext
   - The wikitext is then processed the same as file input

Note: You need both URLs configured to use this feature."""
        
        messagebox.showinfo("URL Input Help", help_text)
    
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
        try:
            self.log_status("=== PROCESS BUTTON CLICKED ===")
            self.root.update()  # Force GUI update
            
            if self.processing:
                self.log_status("Already processing, ignoring...")
                return
                
            # Validate inputs
            file_path = self.file_var.get().strip()
            url = self.url_var.get().strip()
            output_file = self.output_var.get().strip()
            
            self.log_status(f"File path: '{file_path}'")
            self.log_status(f"URL: '{url}'")
            self.log_status(f"Output file: '{output_file}'")
            self.root.update()  # Force GUI update
            
            if not file_path and not url:
                self.log_status("ERROR: No file or URL provided")
                messagebox.showerror("Error", "Please select a file or enter a URL")
                return
                
            if file_path and url:
                self.log_status("ERROR: Both file and URL provided")
                messagebox.showerror("Error", "Please select either a file OR enter a URL, not both")
                return
                
            if not output_file:
                self.log_status("ERROR: No output filename")
                messagebox.showerror("Error", "Please specify an output filename")
                return
            
            # Update global API URL if configured in GUI
            if url:
                global WIKI_API_URL
                gui_api_url = self.api_url_var.get().strip()
                if gui_api_url and gui_api_url != WIKI_API_URL:
                    WIKI_API_URL = gui_api_url
                    self.log_status(f"Using API URL: {WIKI_API_URL}")
                
                # Check URL configuration
                if 'wiki.yourdomain.com' in WIKI_API_URL:
                    self.log_status("ERROR: Wiki API URL not configured")
                    messagebox.showerror("Configuration Error", 
                                       "Please configure the Wiki API URL using the 'Set API' button before using URL input")
                    return
            
            # Process directly in main thread for now (no threading to avoid issues)
            self.log_status("=== STARTING PROCESSING ===")
            self.processing = True
            self.process_btn.config(state='disabled')
            self.progress.start()
            self.root.update()  # Force GUI update
            
            # Process directly
            self._process_directly(file_path, url, output_file)
            
        except Exception as e:
            self.log_status(f"CRITICAL ERROR in process_log: {e}")
            import traceback
            self.log_status(f"Full traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self._processing_complete()
    
    def _process_directly(self, file_path, url, output_file):
        """Process directly in main thread for debugging"""
        try:
            self.log_status("Processing started...")
            self.root.update()
            
            title = ""
            wikitext = ""
            
            if file_path:
                self.log_status(f"Reading file: {file_path}")
                self.root.update()
                
                # Check if file exists first
                if not os.path.exists(file_path):
                    self.log_status(f"File does not exist: {file_path}")
                    return
                    
                result = process_file(file_path)
                if result:
                    title, wikitext = result
                    self.log_status("File read successfully")
                    self.log_status(f"Title: {title}")
                    self.log_status(f"Content length: {len(wikitext)} characters")
                    self.root.update()
                else:
                    self.log_status("Failed to read file")
                    return
                    
            elif url:
                self.log_status(f"Fetching from URL: {url}")
                self.root.update()
                result = get_wikitext_from_url(url)
                if result:
                    title, wikitext = result
                    self.log_status("URL content fetched successfully")
                    self.root.update()
                else:
                    self.log_status("Failed to fetch URL content")
                    return
            
            if not wikitext:
                self.log_status("No content to process")
                return
            
            self.log_status("Processing content...")
            self.root.update()
            
            processor = ContentProcessor()
            processed_content = processor.process_log_content(title, wikitext)
            
            self.log_status("Content processed successfully!")
            self.log_status(f"Processed content length: {len(processed_content)} characters")
            self.root.update()
            
            # Save output
            try:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                output_path = os.path.join(script_dir, output_file)
                
                self.log_status(f"Saving to: {output_path}")
                self.root.update()
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_content)
                
                self.log_status(f"=== SUCCESS! ===")
                self.log_status(f"File saved to: {output_path}")
                self.log_status(f"Processed {len(wikitext.splitlines())} lines")
                
                # Show success message
                messagebox.showinfo("Success", f"Processing complete!\n\nFile saved to:\n{output_path}")
                
                # Offer to open the file
                if messagebox.askyesno("Open File", "Would you like to open the processed file?"):
                    try:
                        if sys.platform.startswith('win'):
                            os.startfile(output_path)
                        elif sys.platform.startswith('darwin'):
                            os.system(f'open "{output_path}"')
                        else:
                            os.system(f'xdg-open "{output_path}"')
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not open file: {e}")
                
            except Exception as e:
                self.log_status(f"Error writing output file: {e}")
                messagebox.showerror("Error", f"Could not save file: {e}")
                
        except Exception as e:
            self.log_status(f"Processing error: {e}")
            import traceback
            self.log_status(f"Full traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Processing failed: {e}")
        finally:
            # Re-enable UI
            self._processing_complete()
    
    def _process_worker(self, file_path, url, output_file):
        """Worker thread for processing"""
        try:
            self.log_status("Worker thread started!")
            self.log_status("Starting processing...")
            
            title = ""
            wikitext = ""
            
            if file_path:
                self.log_status(f"Reading file: {file_path}")
                # Check if file exists first
                if not os.path.exists(file_path):
                    self.log_status(f"File does not exist: {file_path}")
                    return
                    
                result = process_file(file_path)
                if result:
                    title, wikitext = result
                    self.log_status("File read successfully")
                    self.log_status(f"Title: {title}")
                    self.log_status(f"Content length: {len(wikitext)} characters")
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
            import traceback
            self.log_status(f"Full traceback: {traceback.format_exc()}")
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