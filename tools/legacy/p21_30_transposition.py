"""
P21-30 Transposition Solver
After keyword Vigenère decryption produces high IoC but scrambled text,
try various transposition reversals to recover plaintext.
P19 hint: "REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR K"
"""

GP = {
    '\u16A0':0, '\u16A2':1, '\u16A6':2, '\u16A9':3, '\u16B1':4, '\u16B3':5, '\u16B7':6, '\u16B9':7,
    '\u16BB':8, '\u16BE':9, '\u16C1':10, '\u16C4':11, '\u16C7':12, '\u16C8':13, '\u16C9':14, '\u16CB':15,
    '\u16CF':16, '\u16D2':17, '\u16D6':18, '\u16D7':19, '\u16DA':20, '\u16DD':21, '\u16DF':22, '\u16DE':23,
    '\u16AA':24, '\u16AB':25, '\u16A3':26, '\u16E1':27, '\u16E0':28
}
IDX = {0:'F', 1:'U', 2:'TH', 3:'O', 4:'R', 5:'C', 6:'G', 7:'W', 8:'H', 9:'N', 10:'I', 11:'J', 12:'EO',
       13:'P', 14:'X', 15:'S', 16:'T', 17:'B', 18:'E', 19:'M', 20:'L', 21:'NG', 22:'OE', 23:'D', 24:'A',
       25:'AE', 26:'Y', 27:'IA', 28:'EA'}

KEYWORDS = {
    21: ("CABAL", "beaufort"),
    22: ("DIVINITY", "beaufort"),
    23: ("ENCRYPTION", "add"),
    24: ("OBSCURA", "beaufort"),
    25: ("CABAL", "beaufort"),
    26: ("ENCRYPT", "add"),
    27: ("SHADOWS", "add"),
    28: ("DEOR", "sub"),
    29: ("TOTIENT", "beaufort"),
    30: ("MOURNFUL", "add"),
}

# Convert keyword to GP indices
def keyword_to_indices(kw):
    mapping = {'F':0, 'U':1, 'V':1, 'TH':2, 'O':3, 'R':4, 'C':5, 'K':5, 'G':6, 'W':7,
               'H':8, 'N':9, 'I':10, 'J':11, 'EO':12, 'P':13, 'X':14, 'S':15, 'T':16,
               'B':17, 'E':18, 'M':19, 'L':20, 'NG':21, 'OE':22, 'D':23, 'A':24,
               'AE':25, 'Y':26, 'IA':27, 'EA':28}
    result = []
    i = 0
    while i < len(kw):
        if i+1 < len(kw) and kw[i:i+2] in mapping:
            result.append(mapping[kw[i:i+2]])
            i += 2
        elif kw[i] in mapping:
            result.append(mapping[kw[i]])
            i += 1
        else:
            i += 1
    return result

def load_page(page_num):
    path = f"pages/page_{page_num:02d}/runes.txt"
    with open(path, encoding='utf-8') as f:
        text = f.read()
    # Parse runes and word structure
    words = []
    current = []
    for ch in text:
        if ch in GP:
            current.append(GP[ch])
        elif ch in '- .\n':
            if current:
                words.append(current)
                current = []
    if current:
        words.append(current)
    flat = [r for w in words for r in w]
    return flat, words

def decrypt_keyword(cipher_flat, keyword, mode):
    key = keyword_to_indices(keyword)
    kl = len(key)
    if mode == "sub":
        return [(cipher_flat[i] - key[i % kl]) % 29 for i in range(len(cipher_flat))]
    elif mode == "add":
        return [(cipher_flat[i] + key[i % kl]) % 29 for i in range(len(cipher_flat))]
    elif mode == "beaufort":
        return [(key[i % kl] - cipher_flat[i]) % 29 for i in range(len(cipher_flat))]

def indices_to_text(indices):
    return ''.join(IDX[i] for i in indices)

def words_to_text(words, indices):
    pos = 0
    result = []
    for w in words:
        word_idx = indices[pos:pos+len(w)]
        result.append(indices_to_text(word_idx))
        pos += len(w)
    return result

# Simple English word scoring
COMMON_WORDS = set("THE A AN I IN IS IT OF TO AND BE THAT HAVE FOR NOT ON WITH HE AS YOU DO AT THIS BUT HIS BY FROM THEY WE SAY HER SHE OR WILL MY ONE ALL WOULD THERE THEIR WHAT SO UP OUT IF ABOUT WHO GET WHICH GO ME WHEN MAKE CAN LIKE TIME NO JUST HIM KNOW TAKE PEOPLE INTO YEAR YOUR GOOD SOME COULD THEM SEE OTHER THAN THEN NOW LOOK ONLY COME ITS OVER THINK ALSO BACK AFTER USE TWO HOW OUR WORK FIRST WELL WAY EVEN NEW WANT BECAUSE ANY THESE GIVE DAY MOST US WITHIN THROUGH SELF BEING TRUTH PATH WISDOM KNOWLEDGE PILGRIM EVERY SACRED DIVINE SEEK FIND ABOVE BEYOND BETWEEN BELOW".lower().split())
COMMON_WORDS.update("UNTO UNTO EACH HOLY SACRED DEEP WEB THERE EXISTS PAGE DUTY EVERY SEEK CIRCUMFERENCE VOID SHADOW CABAL DIVINITY FORM ANALOG MOURNFUL TOTIENT ENCRYPT OBSCURA BUFFER".lower().split())

def score_words(word_list):
    score = 0
    for w in word_list:
        wl = w.lower()
        # Handle runeglish: TH→TH, NG→NG, etc.
        if wl in COMMON_WORDS:
            score += len(wl)
        elif len(wl) <= 2 and wl in {'i', 'a'}:
            score += 3
    return score

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0: return False
        i += 6
    return True

def get_primes_up_to(n):
    return [i for i in range(2, n+1) if is_prime(i)]

# Columnar transposition reversal
def reverse_columnar(text_indices, width, col_order=None):
    n = len(text_indices)
    nrows = (n + width - 1) // width
    # Number of full columns
    full_cols = n % width if n % width != 0 else width
    
    if col_order is None:
        col_order = list(range(width))
    
    # Each column has nrows elements, except last few might have nrows-1
    col_lengths = []
    for c in range(width):
        if n % width == 0:
            col_lengths.append(nrows)
        else:
            if c < full_cols:
                col_lengths.append(nrows)
            else:
                col_lengths.append(nrows - 1)
    
    # Split cipher into columns by reading order
    columns = {}
    pos = 0
    for read_idx in range(width):
        col_idx = col_order[read_idx]
        clen = col_lengths[col_idx]
        columns[col_idx] = text_indices[pos:pos+clen]
        pos += clen
    
    # Reconstruct by rows
    result = []
    for row in range(nrows):
        for col in range(width):
            if row < len(columns.get(col, [])):
                result.append(columns[col][row])
    return result

# Test all pages
import itertools

print("=" * 80)
print("P21-30 TRANSPOSITION SOLVER")
print("=" * 80)

for page in range(21, 31):
    kw, mode = KEYWORDS[page]
    flat, words = load_page(page)
    dec = decrypt_keyword(flat, kw, mode)
    
    dec_words = words_to_text(words, dec)
    base_score = score_words(dec_words)
    
    print(f"\n{'='*60}")
    print(f"Page {page}: keyword={kw}, mode={mode}, runes={len(flat)}, words={len(words)}")
    print(f"Base word score: {base_score}")
    print(f"Decoded words: {' '.join(dec_words[:20])}...")
    
    # Check if individual words are English
    eng_words = [w for w in dec_words if w.lower() in COMMON_WORDS]
    print(f"English words found: {eng_words}")
    
    # Try columnar transposition with prime widths
    best_score = base_score
    best_params = None
    best_text = None
    
    for width in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if width >= len(flat):
            continue
        
        # Try natural column order
        reversed_flat = reverse_columnar(dec, width)
        rev_words = words_to_text(words, reversed_flat)
        s = score_words(rev_words)
        if s > best_score:
            best_score = s
            best_params = f"columnar w={width} natural"
            best_text = ' '.join(rev_words[:20])
        
        # Try reversed column order
        reversed_flat2 = reverse_columnar(dec, width, list(range(width-1, -1, -1)))
        rev_words2 = words_to_text(words, reversed_flat2)
        s2 = score_words(rev_words2)
        if s2 > best_score:
            best_score = s2
            best_params = f"columnar w={width} reversed"
            best_text = ' '.join(rev_words2[:20])
        
        # For small widths, try all permutations
        if width <= 7:
            for perm in itertools.permutations(range(width)):
                reversed_flat3 = reverse_columnar(dec, width, list(perm))
                rev_words3 = words_to_text(words, reversed_flat3)
                s3 = score_words(rev_words3)
                if s3 > best_score:
                    best_score = s3
                    best_params = f"columnar w={width} perm={perm}"
                    best_text = ' '.join(rev_words3[:20])
    
    # Try prime-position extraction/rearrangement
    primes_in_range = get_primes_up_to(len(dec))
    non_primes = [i for i in range(len(dec)) if i not in set(primes_in_range)]
    
    # Read primes first, then non-primes
    reorder1 = [dec[i] for i in primes_in_range if i < len(dec)] + [dec[i] for i in non_primes if i < len(dec)]
    rev_words4 = words_to_text(words, reorder1)
    s4 = score_words(rev_words4)
    if s4 > best_score:
        best_score = s4
        best_params = "prime-first"
        best_text = ' '.join(rev_words4[:20])
    
    # Interleave: place prime-indexed values at non-prime positions and vice versa
    reorder2 = list(dec)
    prime_vals = [dec[i] for i in primes_in_range if i < len(dec)]
    nonprime_vals = [dec[i] for i in non_primes if i < len(dec)]
    for i, p in enumerate(primes_in_range):
        if p < len(dec) and i < len(nonprime_vals):
            reorder2[p] = nonprime_vals[i]
    for i, np_idx in enumerate(non_primes):
        if np_idx < len(dec) and i < len(prime_vals):
            reorder2[np_idx] = prime_vals[i]
    rev_words5 = words_to_text(words, reorder2)
    s5 = score_words(rev_words5)
    if s5 > best_score:
        best_score = s5
        best_params = "prime-nonprime-swap"
        best_text = ' '.join(rev_words5[:20])
    
    if best_params:
        print(f"BEST: score={best_score}, method={best_params}")
        print(f"Text: {best_text}")
    else:
        print(f"No improvement over base score {base_score}")

    # Word-level rearrangement: check if words individually match English
    # This is important — maybe the WORD ORDER is scrambled, not character order
    print(f"\nAll decoded words ({len(dec_words)}): {' '.join(dec_words)}")
