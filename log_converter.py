import re
import argparse
import requests
from typing import Tuple, Optional
import logging
import os

# This file is copied from the Elsie project and should be kept in sync
try:
    from character_maps import SHIP_SPECIFIC_CHARACTER_CORRECTIONS, resolve_character_name_with_context, FALLBACK_CHARACTER_CORRECTIONS, FLEET_SHIP_NAMES
except ImportError:
    print("ERROR: character_maps.py not found. Please ensure it is in the same directory.")
    exit(1)


# --- Standalone Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# MediaWiki API endpoint for the wiki you are targeting.
# This needs to be changed to the base URL of the wiki's api.php file.
# For example: 'https://stardancer.org/api.php'
WIKI_API_URL = 'https://wiki.yourdomain.com/api.php' # <-- IMPORTANT: CONFIGURE THIS

class ContentProcessor:
    """Handles content processing, classification, and formatting"""
    
    def __init__(self):
        self.character_maps = SHIP_SPECIFIC_CHARACTER_CORRECTIONS

    def _cleanup_line(self, line: str) -> str:
        """Performs final formatting on the line content."""
        line = re.sub(r"'''(.*?)'''", r'\\1', line)
        line = re.sub(r"''(.*?)''", r'\\1', line)
        # Remove any remaining HTML-like tags
        line = re.sub(r'<[^>]+>', '', line)
        return line

    def _remove_timestamp(self, line: str) -> str:
        """Removes a timestamp from the start of a line."""
        timestamp_pattern = r'^\s*\[\s*\d{1,2}:\d{2}(?::\d{2})?\s*\]\s*'
        return re.sub(timestamp_pattern, '', line)

    def _convert_scene_tags(self, line: str) -> Tuple[str, str]:
        """Converts [DOIC] tags."""
        scene_tag = ""
        scene_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E', '6': 'F'}
        doic_pattern = r'\[\s*(DOIC(\d)?)\s*\]'
        match = re.search(doic_pattern, line, re.IGNORECASE)
        
        if match:
            original_tag = match.group(0)
            digit = match.group(2)
            scene_tag = f"-Scene {scene_map.get(digit, '?')}-" if digit else "-Setting-"
            line = line.replace(original_tag, "", 1).lstrip()
            
        return line, scene_tag

    def _assign_speaker(self, line: str, ship_context: str) -> Tuple[str, str]:
        """Assigns a speaker from patterns."""
        # Pattern for speakers in brackets, e.g., [T'Pol]
        bracket_speaker_pattern = r'^\s*\[\s*([^\]]+?)\s*\]'
        bracket_match = re.search(bracket_speaker_pattern, line)
        if bracket_match and self._is_known_character(bracket_match.group(1), ship_context):
            speaker = bracket_match.group(1).strip()
            # Remove the speaker tag and any following colon
            line = line[bracket_match.end(0):].lstrip()
            if line.startswith(':'):
                line = line[1:].lstrip()
            return line, speaker

        # Pattern for speakers with @-tags, e.g., Archer@Captain:
        at_tag_pattern = r'^\s*([^:]+@\S+)\s*:'
        at_match = re.search(at_tag_pattern, line)
        if at_match:
            speaker = at_match.group(1).strip()
            line = line[at_match.end(0):].lstrip()
            return line, speaker
        
        # General pattern for 'Speaker: Dialogue'
        colon_pattern = r'^\s*([^:]{2,40}?)\s*:'
        colon_match = re.search(colon_pattern, line)
        if colon_match:
            potential_speaker = colon_match.group(1).strip()
            # Heuristic to avoid matching parts of sentences
            if (' ' in potential_speaker or (potential_speaker.isalpha() and potential_speaker[0].isupper())) and len(potential_speaker.split()) < 5:
                 line = line[colon_match.end(0):].lstrip()
                 return line, potential_speaker

        return line, ""

    def _is_known_character(self, name: str, ship_context: str) -> bool:
        """Checks if a name is a known character by trying to resolve it."""
        resolved_name = resolve_character_name_with_context(name, ship_context)
        return resolved_name != 'Unknown' and resolved_name is not None

    def _get_ship_context(self, title: str) -> str:
        """Determines the ship context from the page title."""
        title_lower = title.lower()
        for ship_name in FLEET_SHIP_NAMES:
            if ship_name.lower() in title_lower:
                return ship_name.lower().replace('uss ', '')
        return ""

    def process_log_content(self, title: str, wikitext: str) -> str:
        """Processes raw wikitext from a log page."""
        if not wikitext:
            return ""
        
        ship_context = self._get_ship_context(title)
        cleaned_lines = []
        lines = wikitext.splitlines()
        line_number = 1
        last_setting_speaker = ""
        last_processed_speaker = ""

        for original_line in lines:
            work_line = original_line.strip()
            if not work_line:
                continue

            line_with_number = f"-Line {line_number}- "
            work_line = self._remove_timestamp(work_line)
            work_line, scene_tag = self._convert_scene_tags(work_line)
            
            is_action_line = work_line.startswith('*')
            
            work_line, speaker = self._assign_speaker(work_line, ship_context)
            
            if scene_tag == "-Setting-":
                if '@' in speaker:
                    speaker = last_setting_speaker if last_setting_speaker else "Narrator"
                elif not speaker and last_setting_speaker:
                    speaker = last_setting_speaker
                elif is_action_line and not speaker:
                    speaker = "Narrator"

                if speaker:
                    last_setting_speaker = speaker
                
                words = work_line.rstrip().split()
                if words and "end" in [word.lower() for word in words[-4:]]:
                    last_setting_speaker = ""
            else:
                last_setting_speaker = ""

            raw_speaker_name = speaker.split('@')[0].strip()
            if "DGM" in raw_speaker_name:
                if is_action_line:
                    final_speaker = "Narrator"
                else:
                    final_speaker = last_processed_speaker
            elif raw_speaker_name:
                final_speaker = resolve_character_name_with_context(raw_speaker_name, ship_context)
            else:
                final_speaker = ""

            work_line = self._cleanup_line(work_line)

            final_line = line_with_number
            if scene_tag:
                final_line += f"{scene_tag} "
            
            if final_speaker:
                final_line += f"{final_speaker}: "
            
            final_line += work_line
            cleaned_lines.append(final_line)
            line_number += 1
            
            if final_speaker:
                last_processed_speaker = final_speaker

        return f"**{title}**\\n\\n" + "\\n".join(cleaned_lines)

def get_wikitext_from_url(page_url: str) -> Optional[Tuple[str, str]]:
    """Fetches the raw wikitext of a page from a MediaWiki API."""
    try:
        page_title = page_url.split('/')[-1]
        params = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "revisions",
            "rvprop": "content",
            "formatversion": 2
        }
        response = requests.get(WIKI_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        page = data['query']['pages'][0]
        if 'missing' in page:
            logging.error(f"Page '{page_title}' not found on the wiki.")
            return None
        wikitext = page['revisions'][0]['content']
        return page_title, wikitext
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {e}")
        return None
    except (KeyError, IndexError):
        logging.error("Error parsing wiki API response. Check API URL and page title.")
        return None

def process_file(file_path: str) -> Optional[Tuple[str, str]]:
    """Reads wikitext from a local file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            wikitext = f.read()
        # Use the filename (without extension) as the title
        title = os.path.splitext(os.path.basename(file_path))[0]
        return title, wikitext
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return None

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Process a wiki log file from a URL or a local file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="The full URL of the wiki log page.")
    group.add_argument("--file", help="The path to a local .txt file containing the log wikitext.")
    parser.add_argument("--output", help="The name of the output file.", default="processed_log.txt")
    
    args = parser.parse_args()

    title = ""
    wikitext = ""

    if args.url:
        if 'wiki.yourdomain.com' in WIKI_API_URL:
            logging.error("Please configure the WIKI_API_URL in the script before using the --url option.")
            return
            
        result = get_wikitext_from_url(args.url)
        if result:
            title, wikitext = result
    elif args.file:
        result = process_file(args.file)
        if result:
            title, wikitext = result

    if not wikitext:
        logging.info("No content to process. Exiting.")
        return

    processor = ContentProcessor()
    processed_content = processor.process_log_content(title, wikitext)
    
    try:
        # Save the output in the same directory as the script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_path = os.path.join(script_dir, args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        logging.info(f"Successfully processed content and saved to '{output_path}'")
    except Exception as e:
        logging.error(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main() 