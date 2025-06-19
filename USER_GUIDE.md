# Log Converter - User Guide

A simple tool to convert and format Star Trek simulation log files for better readability.

## 🚀 Quick Start

### GUI Version (Recommended)
Double-click **`logconvert-gui.exe`** to open the graphical interface.

### What You'll See
- **File Input**: Browse button and drag-and-drop area
- **Output**: Where to save your processed file
- **Process Log**: Button to start conversion
- **Status Area**: Shows progress and results

## 📁 How to Use

### Step 1: Select Your Log File
**Option A - Browse:**
1. Click the **"Browse"** button
2. Find your log file (usually a `.txt` file)
3. Click **"Open"**

**Option B - Drag & Drop:**
1. Drag your log file from Windows Explorer
2. Drop it onto the gray area in the application

### Step 2: Set Output Name (Optional)
- The default output name is `processed_log.txt`
- You can change this to anything you want (e.g., `my_converted_log.txt`)

### Step 3: Process the Log
1. Click **"Process Log"**
2. Watch the status area for progress updates
3. When complete, you'll see a success message

### Step 4: View Your Results
- Click **"Yes"** when asked if you want to open the file
- Or manually open the file from the same folder as the application

## 📝 What the Tool Does

### Input (Raw Log):
```
[12:30] [DOIC1] T'Pol: This is dialogue from the bridge.
[12:31] [DOIC1] Archer@Captain: Acknowledged.
```

### Output (Formatted):
```
**LogFileName**

-Line 1- -Scene A- T'Pol: This is dialogue from the bridge.
-Line 2- -Scene A- Archer: Acknowledged.
```

### Features:
- ✅ **Removes timestamps** - Cleans up `[12:30]` tags
- ✅ **Converts scene tags** - Changes `[DOIC1]` to `-Scene A-`
- ✅ **Resolves character names** - Handles character name variations
- ✅ **Adds line numbers** - Each line gets a number for reference
- ✅ **Formats dialogue** - Clean, readable conversation format

## 🖥️ Command Line Version (Advanced)

For users comfortable with command prompt:

```
logconvert-cli.exe --file "your_log_file.txt" --output "processed_output.txt"
```

## 🔧 Troubleshooting

### "No file selected" error
- Make sure you've selected a file using Browse or drag-and-drop

### "File does not exist" error
- Check that the file path is correct
- Make sure the file isn't moved or deleted

### Empty output file
- Your input file might be empty or in an unsupported format
- Try with a different log file

### Can't find the output file
- Check the same folder where the application is located
- Look for the filename you specified in the "Output" field

## 📋 File Requirements

### Supported Input Files:
- **Text files** (`.txt`)
- **Log files** with timestamp and scene formatting
- **UTF-8 encoding** (standard text files)

### Typical Log Format:
```
[HH:MM] [DOIC#] CharacterName: Dialogue text
[HH:MM] [DOIC#] *Action descriptions*
```

## 💡 Tips

1. **File Names**: Use descriptive output names like `stardancer_mission_01.txt`
2. **Organization**: Create a folder for your processed logs
3. **Batch Processing**: Process one file at a time for best results
4. **Backup**: Keep your original log files safe

## ❓ Need Help?

If you encounter issues:
1. Make sure your log file follows the expected format
2. Try with a smaller test file first
3. Check that you have write permissions in the output folder

---

**Version**: Log Converter v1.0  
**Compatible with**: Windows 10/11  
**Requirements**: None (standalone executable) 