#!/usr/bin/env python3
"""Remove all emojis from Python source files to fix Windows encoding issues"""

import re
import os

# List of files to clean
files_to_clean = [
    "engagement_monitor.py",
    "topic_reengagement_system.py",
    "girlfriend_agent.py",
    "enhanced_main.py",
    "api_server.py",
    "energy_analyzer.py",
    "message_routing_agent.py",
    "safety_monitor.py",
    "response_adjustment_agent.py",
    "response_quality_agent.py",
    "response_analyzer.py"
]

# Regex pattern to match emojis
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001F018-\U0001F270"  # various symbols
    "\U0001F300-\U0001F5FF"  # misc symbols and pictographs
    "]+",
    flags=re.UNICODE
)

def remove_emojis_from_file(filepath):
    """Remove emojis from a single file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content)
        cleaned_content = emoji_pattern.sub('', content)

        if len(cleaned_content) != original_size:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Cleaned {filepath}: Removed {original_size - len(cleaned_content)} emoji characters")
        else:
            print(f"No emojis found in {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    print("Removing emojis from Python files...")
    for filename in files_to_clean:
        remove_emojis_from_file(filename)
    print("Done!")
