"""
P19 SOLVER - Brute force key length 47
IoC confirms kl=47 (1.419) over kl=43 (0.989).
First 43 key values known. Brute-force remaining 4 (29^4 = 707K).
Mode: ADD (plain = (cipher + key) % 29)
"""
import os, sys
from collections import Counter
from itertools import product

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
MOD = 29; KLEN = 47

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def load_page(pg):
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    runes = [GP[c] for c in raw if c in GP]
    words, current, start, pos = [], [], 0, 0
    for c in raw:
        if c in GP:
            if not current: start = pos
            current.append(GP[c]); pos += 1
        elif current:
            words.append((start, list(current))); current = []
    if current: words.append((start, list(current)))
    return runes, words

def text_to_gp(text):
    result = []
    i = 0
    text = text.upper()
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in DIGRAPHS:
                result.append(DIGRAPHS[di])
                i += 2
                continue
        if text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
        else:
            return None
        i += 1
    return result

cipher, words = load_page(19)
N = len(cipher)
print(f"P19: {N} runes, {len(words)} words")

# Known first 43 key values
key_base = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

# Build word list
common_words = """
A AN AM AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF OH OK ON OR SO TO UP US WE
THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS LET
MAY NEW NOW OLD SEE WAY WHO BOY DID GET HIM HIS PUT SAY SHE TOO USE ANY
THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN CALL CAME COME EACH FIND FIRST GIVE
GOOD GREAT HERE INTO JUST KNOW LIKE LONG LOOK MAKE MANY MOST MUCH MUST NAME NEED
ONLY OVER PART READ SAID SAME SEEM SELF SHOW SIDE SOME SUCH TAKE TELL TERM THEM
THEN THEY TURN VERY WANT WHAT WHEN WORD WORK YEAR ABOUT AFTER AGAIN BEING BRING
COULD EVERY FIRST FOUND GREAT HOUSE LARGE LIGHT MIGHT NEVER OTHER RIGHT SHALL SMALL
SOUND STILL THEIR THERE THESE THINK THREE WHERE WHICH WORLD WOULD WRITE YOUNG
ABOVE BELOW BUILD CLOSE DEATH EARTH FALSE FAITH FAVOR FINAL FORCE GIVEN GLORY
HEART HUMAN IDEAS INNER LEARN LEAVE LIGHT LIAR MEANS MIGHT MOUTH NORTH OCCUR
ORDER PEACE PLACE PLANT POINT POWER PRIME PROVE QUEEN QUITE REACH RIGHT ROUND
SENSE SERVE SINCE SPEAK SPEND STAGE STAND START STATE STONE STORY TEACH THING THINK
THOSE THREE TODAY TOTAL TRUTH TRULY UNDER UNTIL USING VALUE VOICE WASTE WATCH WATER
WHILE WHITE WHOLE WOMEN PATH DEOR REARRANGING PRIMES NUMBERS
WITHIN WISDOM SACRED DIVINE SPIRIT CIPHER FATHER MOTHER NATURE EITHER
PEOPLE REASON READER MASTER MORTAL HIDDEN APPEAR BEYOND ANSWER BECOME NUMBER QUEST
PUBLIC ATTACK LENGTH BREATH WEALTH HEALTH GROWTH
""".strip().split()

WORDSET = set()
WORDS_BY_LEN = {}
for w in common_words:
    gp = text_to_gp(w)
    if gp:
        WORDSET.add(w.upper())
        rl = len(gp)
        if rl not in WORDS_BY_LEN:
            WORDS_BY_LEN[rl] = set()
        WORDS_BY_LEN[rl].add(tuple(gp))

print(f"Dictionary: {len(WORDSET)} words")

# Precompute word info
word_info = []
for wi, (start, wrunes) in enumerate(words):
    rl = len(wrunes)
    buckets = [(start + j) % KLEN for j in range(rl)]
    cipher_vals = [cipher[start + j] for j in range(rl)]
    # Check which buckets are unknown (43-46)
    has_unknown = any(43 <= b <= 46 for b in buckets)
    word_info.append({
        'idx': wi, 'start': start, 'len': rl,
        'buckets': buckets, 'cipher': cipher_vals,
        'has_unknown': has_unknown,
        'gp_candidates': WORDS_BY_LEN.get(rl, set())
    })

def score_key(key):
    """Count word matches for given key with ADD mode."""
    n_match = 0
    matched = []
    for wi in word_info:
        buckets = wi['buckets']
        cipher_vals = wi['cipher']
        rl = wi['len']
        dec = tuple((cipher_vals[j] + key[buckets[j]]) % MOD for j in range(rl))
        if dec in wi['gp_candidates']:
            n_match += 1
            txt = ''.join(LAT[v] for v in dec)
            matched.append((wi['idx'], txt))
    return n_match, matched

# First check: how many words match with first 43 key values + zeros for 43-46
key_test = key_base + [0, 0, 0, 0]
n0, m0 = score_key(key_test)
print(f"\nBaseline (key[43-46]=0): {n0} word matches")

# Count how many words have all-known buckets (0-42 only)
known_only = sum(1 for wi in word_info if not wi['has_unknown'])
print(f"Words with all-known buckets: {known_only}/{len(words)}")
n_known, m_known = score_key(key_test)

# Brute force the 4 unknown positions
print(f"\nBrute-forcing key[43-46] over 29^4 = {29**4} combinations...")
best_score = 0
best_keys = []

# Track affected words - which words use buckets 43-46?
affected_words = [wi for wi in word_info if wi['has_unknown']]
print(f"Words affected by key[43-46]: {len(affected_words)}")
for wi in affected_words:
    print(f"  w{wi['idx']:2d} (pos {wi['start']}, {wi['len']} runes, buckets={wi['buckets']})")

# For efficiency, precompute the score from known-only words
known_score = 0
known_matches = []
for wi in word_info:
    if wi['has_unknown']:
        continue
    buckets = wi['buckets']
    cipher_vals = wi['cipher']
    rl = wi['len']
    dec = tuple((cipher_vals[j] + key_base[buckets[j]]) % MOD for j in range(rl))
    if dec in wi['gp_candidates']:
        known_score += 1
        txt = ''.join(LAT[v] for v in dec)
        known_matches.append((wi['idx'], txt))

print(f"\nKnown-bucket word matches: {known_score}")
for idx, txt in known_matches:
    print(f"  w{idx}: '{txt}'")

# Now brute force
total = 29**4
checked = 0
for v43, v44, v45, v46 in product(range(MOD), repeat=4):
    key_ext = [v43, v44, v45, v46]
    key_full = key_base + key_ext
    
    # Score only affected words (add to known_score)
    extra_score = 0
    extra_matches = []
    for wi in affected_words:
        buckets = wi['buckets']
        cipher_vals = wi['cipher']
        rl = wi['len']
        dec = tuple((cipher_vals[j] + key_full[buckets[j]]) % MOD for j in range(rl))
        if dec in wi['gp_candidates']:
            extra_score += 1
            txt = ''.join(LAT[v] for v in dec)
            extra_matches.append((wi['idx'], txt))
    
    total_score = known_score + extra_score
    
    if total_score > best_score:
        best_score = total_score
        best_keys = [(list(key_ext), list(extra_matches))]
        print(f"  New best: {total_score} words (key[43-46]={key_ext})")
        for idx, txt in (known_matches + extra_matches):
            pass
    elif total_score == best_score:
        best_keys.append((list(key_ext), list(extra_matches)))
    
    checked += 1
    if checked % 200000 == 0:
        print(f"  Progress: {checked}/{total} ({100*checked/total:.1f}%)")

print(f"\n{'='*80}")
print(f"RESULTS: Best score = {best_score} words")
print(f"Number of optimal keys: {len(best_keys)}")
print(f"{'='*80}")

# Show top results
for key_ext, extra_matches in best_keys[:20]:
    key_full = key_base + key_ext
    print(f"\n  Key[43-46] = {key_ext} ({' '.join(LAT[v] for v in key_ext)})")
    
    # Full decryption
    dec = [(cipher[i] + key_full[i % KLEN]) % MOD for i in range(N)]
    full_text = ''.join(LAT[v] for v in dec)
    
    # Words
    all_matches = known_matches + extra_matches
    match_set = set(idx for idx, _ in all_matches)
    
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals)
        marker = "Y" if wi in match_set else " "
        print(f"  {marker} w{wi:2d}: '{txt}'")
    
    # Show full text
    print(f"\n  Full text: {full_text[:200]}...")
    
    # IoC
    counts = Counter(dec)
    ioc = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
    print(f"  IoC*29: {ioc:.3f}")
    
    if len(best_keys) > 5:
        print(f"\n  (Showing first 1 of {len(best_keys)} optimal solutions)")
        break

print(f"\n=== DONE ===")
