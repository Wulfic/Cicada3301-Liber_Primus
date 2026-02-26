
import os
import random
import time
from collections import Counter

# --- CONFIGURATION ---
ITERATIONS = 50000
TRIES = 3

# Primes to test if no prediction or prediction fails
TEST_LENGTHS = [71, 83, 79, 89, 101, 103, 97, 107, 109, 113, 137]

# Hypotheses from Master Solving Doc
PREDICTIONS = {
    71: [1, 5, 8, 9, 13, 15, 17, 18, 21, 22, 23, 27, 29, 31, 32, 33, 36, 48, 54, 55],
    83: [2, 3, 6, 7, 11, 24, 38, 41, 42],
    79: [14, 28, 30, 39, 46, 50, 53],
    89: [16, 25, 26, 40, 43, 51],
    103: [4, 12, 19, 34],
    101: [35, 37, 47, 52],
    97: [20, 44],
    113: [0],
    137: [10],
    107: [45]
}

# Invert for easy lookup
PAGE_TO_KEYLEN = {}
for k, pages in PREDICTIONS.items():
    for p in pages:
        PAGE_TO_KEYLEN[p] = k

RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']

BIGRAM_SCORES = {
    'LE': 52, 'UI': 46, 'IL': 46, 'HE': 33, 'TH': 33, 'IC': 26, 'ET': 19,
    'HA': 19, 'EO': 19, 'WA': 19, 'AR': 19, 'EF': 19, 'AL': 19, 'LC': 13,
    'AN': 13, 'CA': 13, 'NH': 13, 'EA': 13, 'LU': 13, 'RN': 13, 'NF': 13,
    'FS': 13, 'SU': 13, 'FI': 13, 'IS': 13, 'SO': 13, 'OD': 13, 'DI': 13,
    'CE': 13, 'OM': 13, 'MU': 13, 'EU': 13, 'UY': 13, 'YD': 13, 'DN': 13,
    'NU': 13, 'UH': 13, 'AT': 13, 'EN': 13, 'NA': 13, 'AI': 13, 'WE': 6,
    'EL': 6, 'CU': 6, 'UM': 6, 'MA': 6, 'NW': 6, 'WY': 6, 'YL': 6,
}

def load_page(page_num):
    paths = [
        f"LiberPrimus/pages/page_{page_num:02d}/runes.txt",
        f"LiberPrimus/pages/page_{page_num:02d}/runes.txt"
    ]
    for path in paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [RUNE_TO_IDX[r] for r in content if r in RUNE_TO_IDX]
    return None

def decrypt(cipher, key):
    return [(c - k) % 29 for c, k in zip(cipher, key * (len(cipher) // len(key) + 1))]

def score_text(plain_indices):
    letters = [IDX_TO_LETTER[i] for i in plain_indices]
    text = "".join(letters)
    score = 0
    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        score += BIGRAM_SCORES.get(bigram, -5)
    
    words = ["UILE", "EALL", "IAEO", "TH", "EO", "THE"]
    for w in words:
        if w in text:
            score += 20 * len(w)
    return score

def hill_climb(cipher, key_len, iterations=ITERATIONS):
    key = [random.randint(0, 28) for _ in range(key_len)]
    best_key = list(key)
    best_score = score_text(decrypt(cipher, key))
    no_improve = 0
    
    for i in range(iterations):
        candidate_key = list(best_key)
        idx = random.randint(0, key_len - 1)
        if random.random() < 0.7:
             change = random.choice([-1, 1, -2, 2])
             candidate_key[idx] = (candidate_key[idx] + change) % 29
        else:
             candidate_key[idx] = random.randint(0, 28)
            
        plain = decrypt(cipher, candidate_key)
        score = score_text(plain)
        
        if score > best_score:
            best_score = score
            best_key = list(candidate_key)
            no_improve = 0
        else:
            no_improve += 1
            
        if no_improve > 3000:
             key = [random.randint(0, 28) for _ in range(key_len)]
             plain = decrypt(cipher, key)
             score = score_text(plain)
             if score > best_score:
                 best_score = score
                 best_key = key
             no_improve = 0
    return best_key, best_score

def format_text(indices):
    return "".join([IDX_TO_LETTER[i] for i in indices]).lower()

def main():
    print("# BATCH ANALYSIS REPORT")
    print(f"Iterations: {ITERATIONS}")
    print("-" * 50)
    
    # Process pages 10 to 57
    for page in range(10, 58):
        cipher = load_page(page)
        if not cipher:
            print(f"## Page {page}\n* No runes.txt found.\n")
            continue
            
        print(f"## Page {page}")
        
        # Determine lengths to test
        lengths = []
        if page in PAGE_TO_KEYLEN:
            lengths.append(PAGE_TO_KEYLEN[page])
        
        # Add a few others for robustness/exploration, but prioritize the prediction
        # If no prediction, use all common primes
        if not lengths:
            lengths = [71, 83, 79, 89] # Most common
            
        best_page_score = -99999
        best_page_key = []
        best_page_text = ""
        best_len = 0
        
        for klen in lengths:
            # print(f"  > Testing Key Length {klen}...")
            run_best_score = -99999
            run_best_key = []
            
            for t in range(TRIES):
                key, score = hill_climb(cipher, klen)
                if score > run_best_score:
                    run_best_score = score
                    run_best_key = key
            
            if run_best_score > best_page_score:
                best_page_score = run_best_score
                best_page_key = run_best_key
                best_len = klen
                best_page_text = format_text(decrypt(cipher, run_best_key))
                
        print(f"* **Best Score:** {best_page_score}")
        print(f"* **Key Length:** {best_len}")
        print(f"* **Key:** `{best_page_key}`")
        print("```")
        print(best_page_text[:200])
        print("```")
        print("\n")

if __name__ == "__main__":
    main()
