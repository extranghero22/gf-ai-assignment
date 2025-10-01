"""
Clean the dataset to remove emojis that cause encoding issues
"""

import json
import re

def clean_text(text):
    """Remove emojis and other problematic Unicode characters"""
    # Remove emojis and other Unicode characters that cause issues
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F618"  # face blowing kiss
        u"\U0001F495"  # two hearts
        u"\U0001F50D"  # magnifying glass
        u"\U0001F970"  # smiling face with hearts
        "]+", flags=re.UNICODE)
    
    # Also remove any remaining problematic characters
    cleaned = emoji_pattern.sub('', text)
    
    # Remove any remaining non-ASCII characters that might cause issues
    cleaned = ''.join(char for char in cleaned if ord(char) < 128 or char.isspace())
    
    return cleaned.strip()

def clean_dataset():
    """Clean the girlfriend dataset"""
    
    print("Cleaning dataset...")
    
    # Read the original dataset
    with open('girlfriend_dataset.jsonl', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_entries = []
    
    for line in lines:
        if line.strip():
            try:
                entry = json.loads(line)
                
                # Clean the user message
                user_content = clean_text(entry['messages'][0]['content'])
                
                # Clean the assistant message
                assistant_content = clean_text(entry['messages'][1]['content'])
                
                # Create cleaned entry
                cleaned_entry = {
                    "messages": [
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": assistant_content}
                    ]
                }
                
                cleaned_entries.append(cleaned_entry)
                
            except json.JSONDecodeError:
                continue
    
    # Write cleaned dataset
    with open('girlfriend_dataset_clean.jsonl', 'w', encoding='utf-8') as f:
        for entry in cleaned_entries:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Cleaned {len(cleaned_entries)} entries")
    print("Saved to girlfriend_dataset_clean.jsonl")

if __name__ == "__main__":
    clean_dataset()
