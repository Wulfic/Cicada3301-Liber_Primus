"""
P02 Crib Dragging Key Refinement

Starting with partial 43-element key, improve it by:
1. Analyzing which key positions contribute to known English fragments
2. Testing alternatives for unclear positions  
3. Scoring with word-level English matching
"""

GP = {chr(k):v for k,v in [(0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),(0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),(0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),(0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),(0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
IDX = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

# Load common words (including Cicada-specific)
WORDS = set()
with open('data/wordlist.txt') as f:
    for line in f:
        w = line.strip().upper()
        if w:
            WORDS.add(w)
# Add Cicada-specific
for w in "THE A AN I IN IS IT OF TO AND BE THAT FOR NOT ON WITH AS SAME OTHER SONG EACH THEIR ALL THIS FROM SELF TRUTH SEEK WITHIN SACRED HOLY PILGRIM WISDOM KNOWLEDGE EVERY PATH FIND ABOVE WAY BEING SHALL MUST OUR YOUR LIKE MORE BUT HIS HER THEY WE ARE YOU DO AT WHAT SO UP IF ABOUT WHO WHICH WHEN HOW THEN NO JUST THEM SOME".split():
    WORDS.add(w)

# Known Cicada content words
CICADA_WORDS = set("WELCOME PILGRIM JOURNEY SACRED DIVINITY CIRCUMFERENCE WISDOM INSTRUCTION CONSUMPTION PRESERVATION ADHERENCE COMMAND SELF REALITY KOAN MASTER BEING TRUTH WITHIN ABOVE BEYOND LOSS QUESTION DISCOVER IMPOSE INNOCENT ILLUSION CERTAINTY STRUGGLE SUFFERING END GREAT NECESSARY WAY PILGRIM EMERGE INSTAR SHAPE INTELLIGENCE HOLY LAW ENCRYPT UNTO EACH".split())
WORDS.update(CICADA_WORDS)

def load_runes(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    words = []; current = []
    for ch in text:
        if ch in GP: current.append(GP[ch])
        elif ch == '\u2022' or ch in '-. \n':
            if current: words.append(current); current = []
    if current: words.append(current)
    flat = [r for w in words for r in w]
    return flat, words

def decrypt_sub(flat, key):
    return [(flat[i] - key[i % len(key)]) % 29 for i in range(len(flat))]

def indices_to_runeglish(indices):
    return ''.join(IDX[i] for i in indices)

def is_valid_word(w):
    """Check if runeglish word could be English"""
    # Direct match
    if w in WORDS:
        return True
    # Common runeglish mappings: C→K, OE→OI/OY, NG→ING, EA→EAR, etc.
    # TH→TH, NG→NG (already handled in GP)
    return False

def score_text(words_text):
    """Score decoded word list"""
    score = 0
    for w in words_text:
        wu = w.upper()
        if wu in WORDS:
            score += len(wu) * 2  # Bonus for longer words
        elif len(wu) >= 3:
            # Check for partial matches (common fragments)
            for cw in ["THE", "AND", "FOR", "NOT", "BUT", "ALL", "ARE"]:
                if cw in wu:
                    score += len(cw)
    return score

flat, words = load_runes('pages/page_02/runes.txt')
key = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]

print(f"P02: {len(flat)} runes, {len(words)} words, key length {len(key)}")

# Detailed position analysis
dec = decrypt_sub(flat, key)

# Show position-by-position with key index
print("\nPosition | KeyIdx | Cipher | Key | Plain | Letter")
print("-" * 55)

# Get word boundaries
word_starts = []
pos = 0
for w in words:
    word_starts.append(pos)
    pos += len(w)

for i in range(len(flat)):
    ki = i % 43
    c = flat[i]
    k = key[ki]
    p = (c - k) % 29
    sep = "|" if i in word_starts else " "
    print(f"{i:4d} {sep} ki={ki:2d} c={c:2d} k={k:2d} -> {p:2d} {IDX[p]:3s}")

# Current decoded text
print("\n" + "="*60)
print("Current SUB output:")
pos = 0
for i, w in enumerate(words):
    dw = dec[pos:pos+len(w)]
    text = indices_to_runeglish(dw)
    positions = list(range(pos, pos+len(w)))
    key_indices = [p % 43 for p in positions]
    print(f"Word {i:2d}: [{positions[0]:3d}-{positions[-1]:3d}] keys={key_indices} → '{text}'")
    pos += len(w)

# Try improving key: for each key position, try all 29 values
# and score the resulting text
print("\n" + "="*60)
print("Key optimization - trying all values for each key position:")

best_key = list(key)
best_score = score_text([indices_to_runeglish(dec[sum(len(w) for w in words[:i]):sum(len(w) for w in words[:i])+len(words[i])]) for i in range(len(words))])
print(f"Initial score: {best_score}")

improved = True
iteration = 0
while improved and iteration < 10:
    improved = False
    iteration += 1
    for ki in range(43):
        current_val = best_key[ki]
        best_val = current_val
        best_ki_score = -1
        
        for try_val in range(29):
            test_key = list(best_key)
            test_key[ki] = try_val
            test_dec = decrypt_sub(flat, test_key)
            
            # Build word text
            pos = 0; wt = []
            for w in words:
                dw = test_dec[pos:pos+len(w)]
                wt.append(indices_to_runeglish(dw))
                pos += len(w)
            
            s = score_text(wt)
            
            # Also check single-rune constraint
            pos = 0
            for w in words:
                if len(w) == 1:
                    p = test_dec[pos]
                    if p in (10, 24):  # I or A
                        s += 5  # Bonus for valid singles
                pos += len(w)
            
            if s > best_ki_score:
                best_ki_score = s
                best_val = try_val
        
        if best_val != current_val:
            best_key[ki] = best_val
            improved = True
    
    # Recalculate score
    test_dec = decrypt_sub(flat, best_key)
    pos = 0; wt = []
    for w in words:
        dw = test_dec[pos:pos+len(w)]
        wt.append(indices_to_runeglish(dw))
        pos += len(w)
    new_score = score_text(wt)
    print(f"Iteration {iteration}: score={new_score}, key changed={best_key != key}")

# Final output
print("\n" + "="*60)
print("OPTIMIZED OUTPUT:")
final_dec = decrypt_sub(flat, best_key)
pos = 0; final_words = []
for w in words:
    dw = final_dec[pos:pos+len(w)]
    final_words.append(indices_to_runeglish(dw))
    pos += len(w)
print(' '.join(final_words))

# Show key changes
print("\nKey changes:")
for i in range(43):
    if key[i] != best_key[i]:
        print(f"  Position {i}: {key[i]}({IDX[key[i]]}) → {best_key[i]}({IDX[best_key[i]]})")

print(f"\nFinal key: {best_key}")

# Check singles in final output
pos = 0
for i, w in enumerate(words):
    if len(w) == 1:
        p = final_dec[pos]
        valid = "ok" if p in (10, 24) else "X"
        print(f"Single word {i} at pos {pos} (keyidx {pos%43}): {IDX[p]} {valid}")
    pos += len(w)
