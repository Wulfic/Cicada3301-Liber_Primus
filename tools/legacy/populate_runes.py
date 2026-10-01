
import os
import re

RUNES_FULL_PATH = "LiberPrimus/reference/transcripts/runes_full.txt"
PAGES_DIR = "LiberPrimus/pages"

def clean_block(block):
    lines = block.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line.endswith('/'):
            line = line[:-1]
        if line:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def populate():
    if not os.path.exists(RUNES_FULL_PATH):
        print(f"Error: {RUNES_FULL_PATH} not found.")
        return

    with open(RUNES_FULL_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by % which seems to be the page delimiter
    blocks = content.split('%')
    
    # Check alignment
    # Page 0 should match first block
    # Page 56 should match the block starting with ᛈᚪᚱᚪᛒᛚᛖ
    
    print(f"Found {len(blocks)} blocks in runes_full.txt")

    for i, block in enumerate(blocks):
        page_num = i
        # Skip if page number is beyond what we expect (74 is max usually)
        if page_num > 74:
            print(f"Warning: More blocks than pages? Block {i}")
            
        page_dir = os.path.join(PAGES_DIR, f"page_{page_num:02d}")
        runes_path = os.path.join(page_dir, "runes.txt")
        
        cleaned_runes = clean_block(block)
        
        # Validation checks for known pages
        if page_num == 56:
            if not cleaned_runes.startswith("ᛈᚪᚱᚪᛒᛚᛖ"):
                print(f"MISMATCH at Page 56. Block starts with: {cleaned_runes[:10]}")
        
        if not os.path.exists(page_dir):
            os.makedirs(page_dir, exist_ok=True)
            print(f"Created directory {page_dir}")
            
        if not os.path.exists(runes_path):
            print(f"Writing runes to {runes_path}")
            with open(runes_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_runes)
        else:
            # Optional: check if empty
            with open(runes_path, 'r', encoding='utf-8') as f:
                existing = f.read().strip()
            if not existing:
                print(f"Overwriting empty file {runes_path}")
                with open(runes_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_runes)
            else:
                # print(f"Page {page_num} already has runes. Skipping.")
                pass

if __name__ == "__main__":
    populate()
