"""
P18 SOLVER v4 - Use matched words to precisely determine key values
Starting from the best SUB key (17/68 words matched), use known-correct words
to derive exact key values at their positions, then propagate.
"""
import os
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29
KLEN = 53

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    path = f'LiberPrimus/pages/page_{pg:02d}/runes.txt'
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words = []
    current = []
    start = 0
    pos = 0
    for c in raw:
        if c in GP:
            if not current:
                start = pos
            current.append(GP[c])
            pos += 1
        elif current:
            words.append((start, list(current)))
            current = []
    if current:
        words.append((start, list(current)))
    return runes, words

def ioc(values):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1))

# English word → GP rune encoding (using digraphs)
def eng_to_gp(word):
    """Convert English word to GP rune values, using digraph-aware encoding."""
    result = []
    i = 0
    w = word.upper()
    while i < len(w):
        # Check digraphs first
        if i + 1 < len(w):
            di = w[i:i+2]
            if di == 'TH': result.append(2); i += 2; continue
            elif di == 'NG': result.append(21); i += 2; continue
            elif di == 'EO': result.append(12); i += 2; continue
            elif di == 'OE': result.append(22); i += 2; continue
            elif di == 'EA': result.append(28); i += 2; continue
            elif di == 'AE': result.append(25); i += 2; continue
            elif di == 'IA': result.append(27); i += 2; continue
        # Single letter
        c = w[i]
        mapping = {
            'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
            'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
            'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15
        }
        if c in mapping:
            result.append(mapping[c])
            i += 1
        else:
            i += 1  # skip unknown chars
    return result

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# Print word structure
print("\nWord structure:")
for wi, (start, wrunes) in enumerate(words):
    print(f"  w{wi:2d}: pos={start:3d}-{start+len(wrunes)-1:3d} len={len(wrunes):2d} cipher={wrunes} ({' '.join(LAT[v] for v in wrunes)})")
    if wi > 30: 
        print(f"  ... ({len(words)-31} more words)")
        break

# Best key from v3 (SUB mode, combo #28)
best_key = [10, 6, 7, 6, 16, 6, 6, 5, 26, 18, 14, 23, 4, 18, 25, 22, 15, 10, 16, 24, 13, 11, 20, 19, 24, 20, 27, 3, 12, 19, 23, 17, 9, 9, 18, 12, 24, 18, 24, 16, 5, 8, 23, 26, 21, 25, 7, 25, 24, 5, 1, 21, 3]

# Decrypt and show matched words with their positions
dec = [(cipher[i] - best_key[i%KLEN]) % 29 for i in range(N)]

common_words = {'THE','AND','OF','TO','IN','IS','IT','THAT','WAS','FOR','ON','ARE','WITH',
                'AS','AT','BE','THIS','FROM','OR','AN','BY','NOT','BUT','WHAT','ALL','A','I',
                'HE','SHE','THEY','WE','YOU','HIS','HER','ITS','OUR','THEIR','WHO','WHICH',
                'HAS','HAD','HAVE','BEEN','ONE','EACH','LIKE','DO','SO','IF','NO','MY','UP',
                'ABOUT','OUT','THEM','THEN','INTO','SOME','THAN','OVER','SUCH','ALSO',
                'TIME','VERY','YOUR','MAKE','HOW','THERE','WHEN','COULD','THESE','THOSE',
                'WOULD','OTHER','MORE','AFTER','MANY','WILL','SHALL','WITHIN','DEEP','WEB',
                'KNOW','TRUTH','SELF','REALITY','BEING','MIND','LIFE','DEATH','THROUGH',
                'PATH','MUST','CAN','MAY','PART','WHOLE','BEFORE','EVERY','NEVER','ALWAYS',
                'ONCE','MOST','FIRST','LAST','NEXT','OWN','SAME','MUCH','BOTH','STILL',
                'EVEN','TOO','JUST','UNDER','UPON','SAID','CAME','TOOK','GAVE','MADE',
                'KNEW','WENT','TOLD','DID','SEEK','FIND','SEE','WISDOM'}

print("\n=== Matched words analysis ===")
for wi, (start, wrunes) in enumerate(words):
    n = len(wrunes)
    dec_runes = dec[start:start+n]
    dec_word = ''.join(LAT[v] for v in dec_runes)
    is_match = dec_word.upper() in common_words
    
    if is_match:
        # Derive key values at these positions
        key_vals = [(cipher[start+j] - dec_runes[j]) % 29 for j in range(n)]
        buckets = [(start+j) % KLEN for j in range(n)]
        print(f"  ✓ w{wi:2d}: '{dec_word}' pos={start}-{start+n-1} runes={dec_runes}")
        print(f"         buckets={buckets} keys={key_vals}")
    elif wi < 40 or n <= 3:
        print(f"  ✗ w{wi:2d}: '{dec_word}' pos={start}-{start+n-1} len={n}")

# === Now: for each matched word, verify the key values are consistent ===
print("\n=== Key value cross-validation ===")
bucket_keys = {}  # bucket -> set of (key_value, source_word)
for wi, (start, wrunes) in enumerate(words):
    n = len(wrunes)
    dec_runes = dec[start:start+n]
    dec_word = ''.join(LAT[v] for v in dec_runes)
    
    if dec_word.upper() in common_words:
        for j in range(n):
            b = (start + j) % KLEN
            k = (cipher[start+j] - dec_runes[j]) % 29
            if b not in bucket_keys:
                bucket_keys[b] = set()
            bucket_keys[b].add((k, wi))

print("Key assignments from matched words:")
conflicts = 0
for b in sorted(bucket_keys.keys()):
    entries = bucket_keys[b]
    keys = set(k for k, _ in entries)
    sources = [(k, wi) for k, wi in entries]
    if len(keys) > 1:
        conflicts += 1
        print(f"  bucket {b:2d}: CONFLICT! {sources}")
    else:
        k = list(keys)[0]
        print(f"  bucket {b:2d}: key={k:2d} ({LAT[k]:3s}) from words {[wi for _, wi in entries]}")

print(f"\n{len(bucket_keys)} buckets determined, {conflicts} conflicts")

# === Build refined key from word-derived values ===
print("\n=== Building refined key ===")
refined_key = list(best_key)  # Start from hill-climbed key

for b in sorted(bucket_keys.keys()):
    entries = bucket_keys[b]
    keys = set(k for k, _ in entries)
    if len(keys) == 1:
        refined_key[b] = list(keys)[0]
    else:
        # Conflict: pick the key value supported by the most words
        key_counts = Counter(k for k, _ in entries)
        refined_key[b] = key_counts.most_common(1)[0][0]

# Re-decrypt with refined key
dec_r = [(cipher[i] - refined_key[i%KLEN]) % 29 for i in range(N)]
ic_r = ioc(dec_r) * 29

dec_words_r = []
for start, wrunes in words:
    n = len(wrunes)
    wd = dec_r[start:start+n]
    dec_words_r.append(''.join(LAT[v] for v in wd))

matched_r = sum(1 for w in dec_words_r if w.upper() in common_words)
text_r = ''.join(LAT[v] for v in dec_r)

print(f"\nRefined: IoC={ic_r:.3f} words={matched_r}/{len(words)}")
print(f"Key: {refined_key}")
print(f"Words: {' '.join(dec_words_r[:40])}")
print(f"Full text: {text_r}")

# === Try to fix remaining words by trying adjacent shifts ===
print("\n=== Fixing remaining words ===")
# For each non-matching word, try ±1,±2 on each key position within the word
extended_common = set(common_words)
extended_common.update({'LOOK','AGE','NEW','OLD','GREAT','SMALL','LONG','SHORT','HIGH','LOW',
    'THINK','BECOME','FEEL','LEAVE','BEGIN','SEEM','CAME','HELP','SHOW','HEAR','PLAY',
    'TURN','MOVE','LIVE','BELIEVE','BRING','HAPPEN','WRITE','PROVIDE','SIT','STAND',
    'LOSE','PAY','MEET','INCLUDE','CONTINUE','SET','LEARN','CHANGE','LEAD','UNDERSTAND',
    'WATCH','FOLLOW','STOP','CREATE','SPEAK','READ','ALLOW','ADD','GROW','OPEN','WALK',
    'WIN','OFFER','REMEMBER','LOVE','CONSIDER','APPEAR','BUY','WAIT','SERVE','DIE',
    'SEND','EXPECT','BUILD','STAY','FALL','CUT','REACH','KILL','REMAIN','WORK',
    'THOSE','HERSELF','HIMSELF','ITSELF','MYSELF','NOTHING','SOMETHING','ANYTHING',
    'EVERYTHING','EVERYONE','SOMEONE','ANYONE','WORLD','YEAR','HAND','NIGHT','DAY',
    'THING','MAN','WOMAN','CHILD','EYE','WORD','ANOTHER','ENOUGH','SUCH',
    'CONSUMPTION','INTELLIGENCE','WARNING'})

# For each unmatched word of length 1-5, try ALL possible words from dictionary that match length
# This is the crib dragging approach
print("\nCrib dragging on short words...")
gp_dict = {}  # rune_length -> list of (word, gp_values)
for w in extended_common:
    gp = eng_to_gp(w)
    rune_len = len(gp)
    if rune_len not in gp_dict:
        gp_dict[rune_len] = []
    gp_dict[rune_len].append((w, gp))

for wi, (start, wrunes) in enumerate(words):
    n = len(wrunes)
    dec_word = dec_words_r[wi]
    
    if dec_word.upper() in common_words:
        continue  # Already matched
    
    if n not in gp_dict:
        continue
    
    candidates = []
    for cand_word, cand_gp in gp_dict[n]:
        # What key values would this candidate require?
        needed_keys = {}
        ok = True
        for j in range(n):
            b = (start + j) % KLEN
            k = (cipher[start+j] - cand_gp[j]) % 29
            needed_keys[b] = k
        
        # Check consistency with refined key at known-good positions
        consistent = True
        for b, k in needed_keys.items():
            if b in bucket_keys:
                known_keys = set(kv for kv, _ in bucket_keys[b])
                if len(known_keys) == 1 and k not in known_keys:
                    consistent = False
                    break
        
        if consistent:
            candidates.append((cand_word, needed_keys))
    
    if len(candidates) == 1:
        cand_word, needed_keys = candidates[0]
        print(f"  w{wi:2d} '{dec_word}' → UNIQUE match: '{cand_word}' (keys: {needed_keys})")
        for b, k in needed_keys.items():
            if b not in bucket_keys:
                bucket_keys[b] = set()
            bucket_keys[b].add((k, wi))
            refined_key[b] = k
    elif 1 < len(candidates) <= 5:
        print(f"  w{wi:2d} '{dec_word}' → {len(candidates)} candidates: {[c[0] for c in candidates]}")
    # Many candidates = skip (not informative)

# Re-decrypt with further refined key
dec_r2 = [(cipher[i] - refined_key[i%KLEN]) % 29 for i in range(N)]
dec_words_r2 = []
for start, wrunes in words:
    n = len(wrunes)
    wd = dec_r2[start:start+n]
    dec_words_r2.append(''.join(LAT[v] for v in wd))

matched_r2 = sum(1 for w in dec_words_r2 if w.upper() in extended_common)
text_r2 = ''.join(LAT[v] for v in dec_r2)
ic_r2 = ioc(dec_r2) * 29

print(f"\nFurther refined: IoC={ic_r2:.3f} words={matched_r2}/{len(words)}")
print(f"Key: {refined_key}")
print(f"Words: {' '.join(dec_words_r2[:50])}")
print(f"Full text: {text_r2}")

# Show ALL matched words now
matched_list = [(dec_words_r2[i], i) for i in range(len(dec_words_r2)) if dec_words_r2[i].upper() in extended_common]
print(f"\nAll matched words: {matched_list}")

# Show how many key buckets are now determined
determined = sum(1 for b in range(KLEN) if b in bucket_keys and len(set(k for k, _ in bucket_keys[b])) == 1)
print(f"\nKey buckets determined: {determined}/{KLEN}")
undetermined = [b for b in range(KLEN) if b not in bucket_keys or len(set(k for k, _ in bucket_keys[b])) != 1]
print(f"Undetermined: {undetermined}")

print("\n=== DONE ===")
