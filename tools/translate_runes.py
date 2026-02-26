
KEY = [19, 6, 23, 16, 10, 22, 9, 27, 26, 11, 16, 3, 19, 0, 12, 7, 23, 17, 7, 1, 1, 5, 28, 7, 20, 21, 15, 1, 17, 20, 23, 8, 22, 9, 20, 16, 7, 8, 13, 22, 15, 10, 2, 11, 22, 22, 4, 9, 19, 24, 1, 8, 12, 18, 21, 11, 21, 22, 21, 12, 7, 6, 13, 1, 14, 12, 26, 11, 11, 5, 27, 21, 25, 8, 22, 15, 20, 4, 20, 4, 19, 26, 0, 19, 1, 6, 2, 3, 22, 26, 24, 1, 19, 22, 12, 0, 21, 18, 20, 5, 17, 4, 24, 10, 19, 14, 19, 7, 12, 12, 14, 16, 2]

RUNE_MAP = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}

# Phonetic/Transliteration Map
TRANS_MAP = {
    0: 'f', 1: 'u', 2: 'þ', 3: 'o', 4: 'r', 5: 'c', 6: 'g', 7: 'w',
    8: 'h', 9: 'n', 10: 'i', 11: 'j', 12: 'eo', 13: 'p', 14: 'x', 15: 's',
    16: 't', 17: 'b', 18: 'e', 19: 'm', 20: 'l', 21: 'ŋ', 22: 'œ', 23: 'd',
    24: 'a', 25: 'æ', 26: 'y', 27: 'ia', 28: 'ea'
}

def main():
    with open(r'c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages\page_00\runes.txt', 'r', encoding='utf-8') as f:
        runes_text = f.read()
    
    decrypted_chars = []
    key_idx = 0
    key_len = len(KEY)
    
    for char in runes_text:
        if char in RUNE_MAP:
            rune_val = RUNE_MAP[char]
            k = KEY[key_idx % key_len]
            plain_val = (rune_val - k) % 29
            decrypted_chars.append(TRANS_MAP[plain_val])
            key_idx += 1
        else:
            decrypted_chars.append(char)
            
    print("".join(decrypted_chars))

if __name__ == "__main__":
    main()
