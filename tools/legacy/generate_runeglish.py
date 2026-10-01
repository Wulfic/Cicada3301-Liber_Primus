
import os
import re
import glob

# Configuration
WORKSPACE_ROOT = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus"
PAGES_DIR = os.path.join(WORKSPACE_ROOT, "pages")
BATCH_RESULTS_PATH = os.path.join(WORKSPACE_ROOT, "BATCH_RESULTS.md")
OUTPUT_DIR = os.path.join(WORKSPACE_ROOT, "runeglish_output")

# Gematria Primus Mapping
RUNE_MAP = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
# Inverse map for numbers back to Transliterated Text (or Runes)
# Here mapping to Transliterated form as per Master Doc
NUM_TO_TEXT = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R', 5: 'C', 6: 'G', 7: 'W',
    8: 'H', 9: 'N', 10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X', 15: 'S',
    16: 'T', 17: 'B', 18: 'E', 19: 'M', 20: 'L', 21: 'NG', 22: 'OE', 23: 'D',
    24: 'A', 25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA'
}

def parse_keys_from_batch_results(filepath):
    keys = {} # page_num (int) -> key (list of ints)
    current_page = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        # ## Page 01
        m_page = re.match(r'## Page (\d+)', line)
        if m_page:
            current_page = int(m_page.group(1))
            continue
            
        # - **Key:** [8, 0, 10, ... ]
        if line.startswith('- **Key:**'):
            # Extract list content
            content = line.split('[')[1].split(']')[0]
            key_list = [int(x.strip()) for x in content.split(',')]
            if current_page is not None:
                keys[current_page] = key_list
                
    return keys

def decrypt_page(page_num, key, runes_text):
    decrypted_text = ""
    key_len = len(key)
    # We only increment key index for valid runes that we decrypt
    # Punctuation is preserved and does not consume a key step (usually)
    # WAIT: Master Doc says "Hyphens = word boundaries". 
    # Usually in Vigenere/OTP, punctuation is skipped and key is NOT advanced, or IS advanced?
    # Master Doc says "plaintext[i] = (cipher[i] - key[i mod keylen]) mod 29"
    # This implies i is the index into the arrays.
    
    # We need to extract ONLY the runes to decrypt properly first, then re-insert?
    # Or does the key skip punctuation?
    # Let's assume standard behavior: Skip punctuation in cipher steam, do NOT consume key (or do?).
    # Standard Vigenere usually only processes letters.
    # Page 0 analysis says "Word preservation - Hyphens = word boundaries".
    # This implies hyphens are NOT part of the mod 29 alphabets.
    
    # Let's build a list of (rune_val, original_char_index)
    rune_indices = []
    for i, char in enumerate(runes_text):
        if char in RUNE_MAP:
            rune_indices.append((RUNE_MAP[char], i))
            
    # Decrypt
    decrypted_vals = {}
    for i, (cipher_val, char_idx) in enumerate(rune_indices):
        key_val = key[i % key_len]
        plain_val = (cipher_val - key_val) % 29
        decrypted_vals[char_idx] = plain_val
        
    # Reconstruct text
    result = []
    for i, char in enumerate(runes_text):
        if i in decrypted_vals:
            result.append(NUM_TO_TEXT[decrypted_vals[i]])
        else:
            result.append(char)
            
    return "".join(result)

def parse_keys_from_json(filepath):
    import json
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert string keys to int
    return {int(k): v for k, v in data.items()}

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    VERIFIED_KEYS_PATH = os.path.join(WORKSPACE_ROOT, "verified_keys.json")
    print(f"Loading verified keys from {VERIFIED_KEYS_PATH}...")
    
    if os.path.exists(VERIFIED_KEYS_PATH):
        keys = parse_keys_from_json(VERIFIED_KEYS_PATH)
    else:
        print(f"Verified keys not found. Falling back to {BATCH_RESULTS_PATH}...")
        keys = parse_keys_from_batch_results(BATCH_RESULTS_PATH)
        
    print(f"Found keys for {len(keys)} pages.")
    
    for page_num in sorted(keys.keys()):
        page_dir_name = f"page_{page_num:02d}"
        runes_path = os.path.join(PAGES_DIR, page_dir_name, "runes.txt")
        
        if not os.path.exists(runes_path):
            print(f"Skipping Page {page_num}: runes.txt not found at {runes_path}")
            continue
            
        print(f"Decrypting Page {page_num}...")
        try:
            with open(runes_path, 'r', encoding='utf-8') as f:
                runes_text = f.read()
                
            decrypted = decrypt_page(page_num, keys[page_num], runes_text)
            
            output_path = os.path.join(OUTPUT_DIR, f"page_{page_num:02d}_runeglish.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(decrypted)
                
        except Exception as e:
            print(f"Error decrypting page {page_num}: {e}")

    print(f"Decryption complete. Check {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
