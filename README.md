# Log Converter

A Python tool for converting wiki log files to formatted text with character name resolution and dialogue formatting.

## Features

- Process wiki log files from URLs or local files
- Character name resolution with ship context
- Scene tag conversion
- Timestamp removal
- Dialogue formatting

## Building the Executable

### Prerequisites

- Python 3.6 or higher
- pip package manager

### Build Instructions

#### Option 1: Using the batch file (Windows)
```bash
build.bat
```

#### Option 2: Manual build
```bash
# Install dependencies
pip install -r requirements.txt

# Run the build script
python build_executable.py
```

The executables will be created in the `dist` folder:
- `logconvert-cli.exe` - Command-line version
- `logconvert-gui.exe` - GUI version with drag-and-drop support

## Usage

### GUI Version (Recommended)

Double-click `logconvert-gui.exe` to launch the graphical interface. The GUI provides:

- **Drag and Drop**: Drag log files directly onto the gray drop area
- **File Browser**: Click the "Browse" button or click the drop area to select files
- **URL Input**: Paste wiki URLs directly into the URL field
- **Progress Tracking**: Real-time status updates and progress bar
- **Auto-open Results**: Option to automatically open the processed file when complete

### Command Line Version

```bash
# Process a local file
logconvert-cli.exe --file log.txt --output processed_log.txt

# Process from wiki URL (requires WIKI_API_URL configuration)
logconvert-cli.exe --url https://example.com/wiki/LogPage --output processed_log.txt
```

### Configuration

Before using the URL option, you need to configure the `WIKI_API_URL` in the `log_converter.py` file:

```python
WIKI_API_URL = 'https://your-wiki-domain.com/api.php'
```

## Project Structure

- `log_converter.py` - Main application logic (command-line interface)
- `gui_converter.py` - GUI application with drag-and-drop support
- `character_maps.py` - Character name mappings and resolution
- `build_executable.py` - Build script for creating executables
- `setup.py` - Package configuration
- `build.bat` - Windows batch file for easy building
- `requirements.txt` - Python dependencies

## Dependencies

- requests - For HTTP requests to wiki APIs
- beautifulsoup4 - For HTML parsing
- pyinstaller - For creating executables
- tkinterdnd2 - For drag-and-drop functionality in GUI (optional)

## Building from Source

If you prefer to run from source instead of using the executable:

```bash
pip install -r requirements.txt
python log_converter.py --file your_log.txt
``` 