#!/usr/bin/env python3
"""Remove ALL problematic Unicode characters from Python source files"""

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

def remove_problematic_unicode(filepath):
    """Remove all problematic Unicode characters from a file"""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_size = len(content)

        # Remove ALL characters outside basic ASCII + common extended ASCII
        # Keep: letters, numbers, punctuation, whitespace, newlines
        # Remove: emojis, variation selectors, and other problematic Unicode
        cleaned_content = ""
        removed_count = 0

        for char in content:
            char_code = ord(char)
            # Keep basic ASCII (0-127) and some extended chars like smart quotes
            # But exclude emoji range and variation selectors
            if char_code <= 127 or char in ['"', '"', ''', ''', '…', '–', '—']:
                cleaned_content += char
            elif 0xFE00 <= char_code <= 0xFE0F:  # Variation selectors
                removed_count += 1
            elif 0x1F300 <= char_code <= 0x1F9FF:  # Emoji range
                removed_count += 1
            elif 0x2600 <= char_code <= 0x27BF:  # Misc symbols
                removed_count += 1
            elif char_code > 127:
                # For other high Unicode, replace with space to be safe
                cleaned_content += ' '
                removed_count += 1
            else:
                cleaned_content += char

        if removed_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"Cleaned {filepath}: Removed {removed_count} problematic Unicode characters")
        else:
            print(f"No problematic Unicode found in {filepath}")

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    print("Removing problematic Unicode characters from Python files...")
    for filename in files_to_clean:
        remove_problematic_unicode(filename)
    print("Done!")
