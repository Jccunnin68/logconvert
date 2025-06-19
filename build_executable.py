#!/usr/bin/env python
"""
Build script for creating the log converter executable.
"""
import os
import sys
import subprocess
import shutil

def clean_build_dirs():
    """Remove previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Remove .spec files
    for file in os.listdir('.'):
        if file.endswith('.spec'):
            print(f"Removing {file}...")
            os.remove(file)

def build_executable():
    """Build the executables using PyInstaller"""
    print("Building log converter executables...")
    
    # Build command-line version
    print("Building command-line version...")
    cmd_cli = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--name=logconvert-cli',  # Name the executable
        '--console',  # Keep console window for command-line usage
        '--add-data=character_maps.py;.',  # Include character_maps.py
        'log_converter.py'  # Main script
    ]
    
    # Build GUI version
    print("Building GUI version...")
    cmd_gui = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--name=logconvert-gui',  # Name the executable
        '--console',  # Keep console window for debugging
        '--add-data=character_maps.py;.',  # Include character_maps.py
        'gui_converter.py'  # GUI script
    ]
    
    try:
        # Build CLI version
        result = subprocess.run(cmd_cli, check=True, capture_output=True, text=True)
        print("CLI version build successful!")
        
        # Build GUI version
        result = subprocess.run(cmd_gui, check=True, capture_output=True, text=True)
        print("GUI version build successful!")
        
        print(f"Executables created at:")
        print(f"  - dist/logconvert-cli.exe (command-line version)")
        print(f"  - dist/logconvert-gui.exe (GUI version)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("Log Converter Executable Builder")
    print("=" * 40)
    
    # Check if PyInstaller is available
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if build_executable():
        print("\nBuild completed successfully!")
        print("You can find the executables in the 'dist' folder.")
        print("\nUsage examples:")
        print("Command-line version:")
        print("  logconvert-cli.exe --file log.txt")
        print("  logconvert-cli.exe --url https://example.com/wiki/LogPage")
        print("\nGUI version:")
        print("  logconvert-gui.exe (double-click to run)")
        print("  Then drag and drop files or paste URLs in the interface")
    else:
        print("\nBuild failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 