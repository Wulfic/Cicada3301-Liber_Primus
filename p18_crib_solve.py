"""
P18 Crib-based solver.
We have 34/53 confirmed key positions. This script:
1. Shows the partial decryption with known/unknown positions marked
2. For each unknown key position, tries all 29 values and shows context
3. Uses word boundaries (-) to constrain guesses
4. Tries crib-dragging with common LP phrases
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53

confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}
unknown = sorted(set(range(KLEN)) - set(confirmed.keys()))

with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Parse into structured form: list of (char, type) where type='rune','sep','newline'
tokens = []
cipher = []
for ch in raw:
    if ch in GP:
        tokens.append(('rune', len(cipher)))
        cipher.append(GP[ch])
    elif ch == '-':
        tokens.append(('sep', None))
    elif ch == '.':
        tokens.append(('period', None))
    elif ch == '\n':
        tokens.append(('newline', None))

N = len(cipher)
print(f"Total cipher runes: {N}")
print(f"Key length: {KLEN}")
print(f"Known positions: {len(confirmed)}/53")
print(f"Unknown key positions: {unknown}")
print()

# Best key from hill climbing (score=-1261.99)
best_hc_key = [28, 24, 21, 6, 19, 6, 6, 5, 11, 15, 8, 2, 18, 18, 25, 25, 15, 10, 16, 24, 
13, 11, 20, 2, 5, 5, 27, 3, 12, 19, 14, 17, 5, 18, 4, 25, 27, 26, 24, 16, 5, 8, 
23, 26, 21, 25, 7, 25, 24, 28, 1, 21, 27]

def decrypt_with_key(key):
    return [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]

def show_text(key, mark_unknown=False):
    dec = decrypt_with_key(key)
    rune_idx = 0
    result = []
    for tok_type, tok_val in tokens:
        if tok_type == 'rune':
            i = tok_val
            kp = i % KLEN
            val = dec[i]
            lat = LAT[val]
            if mark_unknown and kp in unknown:
                lat = f'[{lat}]'
            result.append(lat)
            rune_idx += 1
        elif tok_type == 'sep':
            result.append(' ')
        elif tok_type == 'period':
            result.append('. ')
        elif tok_type == 'newline':
            result.append('\n')
    return ''.join(result)

# Show the hill climbing best result with unknown positions marked
print("=" * 70)
print("HILL CLIMBING BEST (unknown positions in [brackets]):")
print("=" * 70)
print(show_text(best_hc_key, mark_unknown=True))
print()

# For each unknown key position, show which cipher positions it affects
# and what the context looks like
print("=" * 70)
print("ANALYSIS OF UNKNOWN KEY POSITIONS:")
print("=" * 70)
for kp in unknown:
    positions = [i for i in range(N) if i % KLEN == kp]
    print(f"\n--- Key position {kp}: cipher positions {positions} ---")
    for ci in positions:
        # Show context: 3 positions before and after
        context_start = max(0, ci - 4)
        context_end = min(N - 1, ci + 4)
        
        dec = decrypt_with_key(best_hc_key)
        ctx_parts = []
        for j in range(context_start, context_end + 1):
            kpj = j % KLEN
            lat = LAT[dec[j]]
            if j == ci:
                lat = f'>>>{lat}<<<'
            elif kpj in unknown:
                lat = f'[{lat}]'
            ctx_parts.append(lat)
        
        # Also determine word boundaries
        print(f"  pos={ci}: cipher={cipher[ci]:2d}  hc_val={best_hc_key[kp]}({LAT[best_hc_key[kp]]})  context: {'|'.join(ctx_parts)}")
        
        # Try all 29 values and show which produce common letters
        print(f"    All values: ", end='')
        for v in range(MOD):
            plain = (cipher[ci] - v) % MOD
            print(f"{v}={LAT[plain]} ", end='')
        print()

print()
print("=" * 70)
print("WORD-LEVEL ANALYSIS:")
print("=" * 70)

# Parse words with positions
words = []
current_word_runes = []
for tok_type, tok_val in tokens:
    if tok_type == 'rune':
        current_word_runes.append(tok_val)
    elif tok_type in ('sep', 'period', 'newline'):
        if current_word_runes:
            words.append(list(current_word_runes))
            current_word_runes = []
if current_word_runes:
    words.append(list(current_word_runes))

dec = decrypt_with_key(best_hc_key)
print(f"\nTotal words: {len(words)}")
for wi, word_positions in enumerate(words):
    # Check if this word has any unknown positions
    has_unknown = any((pos % KLEN) in unknown for pos in word_positions)
    word_text = ''.join(LAT[dec[pos]] for pos in word_positions)
    
    if has_unknown:
        # Show which positions are unknown
        marked = []
        for pos in word_positions:
            kp = pos % KLEN
            lat = LAT[dec[pos]]
            if kp in unknown:
                marked.append(f'[{lat}:{kp}]')
            else:
                marked.append(lat)
        
        # Get surrounding known words for context
        prev_words = []
        for pwi in range(max(0, wi-2), wi):
            pw = ''.join(LAT[dec[pos]] for pos in words[pwi])
            prev_words.append(pw)
        next_words = []
        for nwi in range(wi+1, min(len(words), wi+3)):
            nw = ''.join(LAT[dec[pos]] for pos in words[nwi])
            next_words.append(nw)
        
        print(f"  Word {wi:3d}: {''.join(marked):40s}  context: {' '.join(prev_words)} ___ {' '.join(next_words)}")

print()
print("=" * 70) 
print("TRYING COMMON CRIBS AT UNKNOWN POSITIONS:")
print("=" * 70)

# Common LP words and phrases to try as cribs
cribs_text = [
    "WARNING", "BELIEVE", "NOTHING", "SACRED", "WELCOME", "PILGRIM",
    "JOURNEY", "WITHIN", "EMERGE", "INSTAR", "DIVINITY", "COMMAND",
    "WISDOM", "INSTRUCTION", "PRIMES", "TOTIENT", "ENCRYPTED",
    "CIRCUMFERENCE", "CONSUMPTION", "PRESERVATION", "ADHERENCE",
    "BEING", "TRUTH", "DISCOVER", "FOLLOW", "IMPOSE", "QUESTION",
    "KNOWLEDGE", "EXPERIENCE", "DEATH", "STRUGGLE", "SUFFERING",
    "INNOCENCE", "ILLUSIONS", "CERTAINTY", "REALITY", "REALITIES",
    "PILGRIMAGE", "SHAPE", "OURSELVES", "OUTSIDE", "GOING",
    "INTELLIGENCE", "HOLY", "LIVES", "SELF", "THROUGH",
    "BEGINNING", "PATTERN", "ORDER", "CHAOS", "DARKNESS", "LIGHT",
    "SPIRIT", "MIND", "BODY", "SOUL", "NATURE", "FIRE",
    "AN END", "A KOAN", "SOME WISDOM", "AN INSTRUCTION", 
    "THE CIRCUMFERENCE", "THE PRIMES", "THE TOTIENT",
    "BEHAVIORS", "LOSS", "DECEPTION", "WEAK", "STRONG",
    "PRIMALITY", "WEALTH", "DESTROY", "PROGRAM", "MASTER",
    "STUDENT", "VOICE", "HEAD", "ENLIGHTENED",
    "PARABLE", "CHAPTER","LIBER", "VERSE", "PSALM",
    "UNDERSTANDING", "PATH", "WANDER", "SEEK", "FIND",
    "SHADOW", "VEIL", "WORLD", "FAITH", "TRUST",
]

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []; i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else: i += 1
    return result

# For each word that has unknown positions, try crib words that match the length
# and are consistent with the known positions
for wi, word_positions in enumerate(words):
    has_unknown = any((pos % KLEN) in unknown for pos in word_positions)
    if not has_unknown:
        continue
    
    word_len_runes = len(word_positions)
    
    # What we know: for each position, either we know the plaintext (confirmed key)
    # or we don't
    known_plain = {}
    unknown_plain = {}
    for pi, pos in enumerate(word_positions):
        kp = pos % KLEN
        if kp not in unknown:
            known_plain[pi] = dec[pos]
        else:
            unknown_plain[pi] = kp  # which key position is unknown
    
    # Try each crib
    for crib_text in cribs_text:
        crib_gp = eng_to_gp(crib_text)
        if len(crib_gp) != word_len_runes:
            continue
        
        # Check if known positions match
        match = True
        for pi, expected_val in known_plain.items():
            if crib_gp[pi] != expected_val:
                match = False
                break
        
        if match:
            # This crib is consistent! Show what key values it implies
            implied_keys = {}
            for pi in unknown_plain:
                # cipher[pos] - key ≡ plaintext (mod 29)
                # key = (cipher[pos] - plaintext) mod 29
                pos = word_positions[pi]
                kp = unknown_plain[pi]
                implied_key = (cipher[pos] - crib_gp[pi]) % MOD
                implied_keys[kp] = (implied_key, LAT[crib_gp[pi]], crib_text)
            
            current_word = ''.join(LAT[dec[pos]] for pos in word_positions)
            print(f"  Word {wi:3d} ({current_word:20s}) matches crib '{crib_text}'")
            for kp, (kv, lat, _) in implied_keys.items():
                print(f"    → key[{kp}] = {kv} ({LAT[kv]}) [currently {best_hc_key[kp]}({LAT[best_hc_key[kp]]})]")

# Also try multi-word cribs
print()
print("=" * 70)
print("MULTI-WORD CRIB PATTERNS:")
print("=" * 70)

multi_cribs = [
    "AN END", "A KOAN", "SOME WISDOM", "AN INSTRUCTION",
    "A WARNING", "A PARABLE", "A BEING", "A LAW",
    "THE GREAT", "THE END", "THE WAY", "THE LOSS",
    "THE TRUTH", "THE PATH", "THE MIND", "THE SELF",
    "THE WORLD", "THE FIRE", "THE VOID", "THE LIGHT",
    "OF ALL", "OF SELF", "OF TRUTH", "OF ALL THINGS",
    "IT IS", "WE ARE", "WE MUST", "YOU ARE", "YOU WILL",
    "TO THE", "TO ALL", "TO SELF", "TO BE", "IN THE",
    "IS THE", "IS NOT", "IS HOLY", "IS SACRED",
    "LIKE THE INSTAR", "FIND THE DIVINITY", 
    "WITHIN AND EMERGE", "THROUGH THIS",
    "AND THE", "AND YOU", "AND OUR", "BUT FOR",
    "NOT AN", "NOT WHAT", "WILL FIND", "WILL DISCOVER",
]

# Try spanning word boundaries
for crib in multi_cribs:
    crib_words = crib.split()
    crib_gp_words = [eng_to_gp(w) for w in crib_words]
    
    # Try to match sequences of consecutive words
    for start_wi in range(len(words) - len(crib_words) + 1):
        # Check GP lengths match
        len_match = True
        for ci, gp_word in enumerate(crib_gp_words):
            if len(gp_word) != len(words[start_wi + ci]):
                len_match = False
                break
        if not len_match:
            continue
        
        # Check known positions match
        all_match = True
        implied = {}
        for ci, gp_word in enumerate(crib_gp_words):
            word_pos = words[start_wi + ci]
            for pi, pos in enumerate(word_pos):
                kp = pos % KLEN
                if kp not in unknown:
                    if dec[pos] != gp_word[pi]:
                        all_match = False
                        break
                else:
                    ik = (cipher[pos] - gp_word[pi]) % MOD
                    if kp in implied and implied[kp] != ik:
                        all_match = False
                        break
                    implied[kp] = ik
            if not all_match:
                break
        
        if all_match and implied:
            current_text = ' '.join(''.join(LAT[dec[pos]] for pos in words[start_wi+ci]) for ci in range(len(crib_words)))
            print(f"  Words {start_wi}-{start_wi+len(crib_words)-1} ({current_text}) → crib '{crib}'")
            for kp, kv in sorted(implied.items()):
                print(f"    → key[{kp}] = {kv} ({LAT[kv]}) [hc: {best_hc_key[kp]}({LAT[best_hc_key[kp]]})]")

# Summary of key position constraints
print()
print("=" * 70)
print("KEY POSITION CONSTRAINT SUMMARY:")
print("=" * 70)
print("Confirmed key values:")
for kp in range(KLEN):
    if kp in confirmed:
        print(f"  key[{kp:2d}] = {confirmed[kp]:2d} ({LAT[confirmed[kp]]}) [CONFIRMED]")
    else:
        print(f"  key[{kp:2d}] = {best_hc_key[kp]:2d} ({LAT[best_hc_key[kp]]}) [HC guess]")
