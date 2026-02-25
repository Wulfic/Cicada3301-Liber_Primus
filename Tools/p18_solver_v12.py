"""
P18 SOLVER v12 - Unconstrained optimization
No frozen values - full search over all 53 key positions.
Tests SUB, ADD, and Beaufort modes.
Uses simulated annealing with word matches + text quality scoring.

Key finding: the 34 "confirmed" values may have FALSE MATCHES.
Only 26/68 words match with them, and 13 words with ALL confirmed
buckets produce non-English. Need to test if different key values
can push past 26.
"""
import os, sys, random, math
from collections import Counter

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53
random.seed(42)

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

cipher, words = load_page(18)
N = len(cipher)

# Build comprehensive word list (rune-length indexed)
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

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

# Load dictionary and build rune-length indexed lookup
WORDLIST = set()
WORDS_BY_RUNELEN = {}

common_words = """
A AN AM AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF OH OK ON OR SO TO UP US WE
THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR OUT HAD HAS HIS HOW ITS LET
MAY NEW NOW OLD SEE WAY WHO BOY DID GET HIM HIS PUT SAY SHE TOO USE DAD MOM ANY
THAT WITH HAVE THIS WILL YOUR FROM THEY BEEN CALL CAME COME EACH FIND FIRST GIVE
GOOD GREAT HERE INTO JUST KNOW LIKE LONG LOOK MAKE MANY MOST MUCH MUST NAME NEED
ONLY OVER PART READ SAID SAME SEEM SELF SHOW SIDE SOME SUCH TAKE TELL TERM THEM
THEN THEY TURN VERY WANT WHAT WHEN WORD WORK YEAR ABOUT AFTER AGAIN BEING BRING
COULD EVERY FIRST FOUND GREAT HOUSE LARGE LIGHT MIGHT NEVER OTHER RIGHT SHALL SMALL
SOUND STILL THEIR THERE THESE THINK THREE WHERE WHICH WORLD WOULD WRITE YOUNG
BEFORE CHANGE DIFFER FOLLOW NUMBER SHOULD THROUGH
ABOVE BELOW BUILD CLOSE DEATH EARTH FALSE FAITH FAVOR FINAL FORCE GIVEN GLORY
HEART HUMAN IDEAS INNER LEARN LEAVE LIGHT LIAR MEANS MIGHT MOUTH NORTH OCCUR
ORDER PEACE PLACE PLANT POINT POWER PRIME PROVE QUEEN QUITE REACH RIGHT ROUND SCENE
SENSE SERVE SINCE SPEAK SPEND STAGE STAND START STATE STONE STORY TEACH THING THINK
THOSE THREE TODAY TOTAL TRUTH TRULY UNDER UNTIL USING VALUE VOICE WASTE WATCH WATER
WHILE WHITE WHOLE WOMEN
WITHIN WISDOM SACRED DIVINE DIVINE SPIRIT CIPHER PRIMES FATHER MOTHER NATURE EITHER
PEOPLE REASON READER MASTER MORTAL HIDDEN APPEAR BEYOND ANSWER BECOME NUMBER
PUBLIC ATTACK LENGTH BREATH WEALTH HEALTH STEALTH GROWTH
ALL THE AND FOR ARE BUT NOT YOU ONE OUR HIS HER ITS OWN LOW HOW FAR TWO SET ACE
DAY WAY MAN GOD END HID USE BIG RUN CUT SET RED OWN TRY ASK AGE FEW WAR SEA AID
ADD ACT KEY TEN YES TOP SIT RAN FIT MET BET HIT ROT COP FAN TIP NOR FOX FIG JAR RAW
""".strip().split()

for w in common_words:
    gp = text_to_gp(w)
    if gp:
        WORDLIST.add(w.upper())
        rl = len(gp)
        if rl not in WORDS_BY_RUNELEN:
            WORDS_BY_RUNELEN[rl] = []
        WORDS_BY_RUNELEN[rl].append((w.upper(), tuple(gp)))

# Also try to load a larger dictionary
try:
    with open('Tools/english_words.txt', 'r') as f:
        for line in f:
            w = line.strip()
            if len(w) < 1 or len(w) > 12: continue
            gp = text_to_gp(w)
            if gp:
                WORDLIST.add(w.upper())
                rl = len(gp)
                if rl not in WORDS_BY_RUNELEN:
                    WORDS_BY_RUNELEN[rl] = []
                WORDS_BY_RUNELEN[rl].append((w.upper(), tuple(gp)))
except:
    pass

# Deduplicate
for rl in WORDS_BY_RUNELEN:
    seen = set()
    deduped = []
    for w, gp in WORDS_BY_RUNELEN[rl]:
        if gp not in seen:
            seen.add(gp)
            deduped.append((w, gp))
    WORDS_BY_RUNELEN[rl] = deduped

print(f"Dictionary: {len(WORDLIST)} words")
for rl in sorted(WORDS_BY_RUNELEN.keys()):
    print(f"  {rl}-rune: {len(WORDS_BY_RUNELEN[rl])} unique words")

# Precompute word info
word_info = []
for wi, (start, wrunes) in enumerate(words):
    rl = len(wrunes)
    buckets = [(start + j) % KLEN for j in range(rl)]
    cipher_vals = [cipher[start + j] for j in range(rl)]
    # For each dictionary word of matching length, compute needed key values
    candidates = []
    if rl in WORDS_BY_RUNELEN:
        for eng_word, gp_vals in WORDS_BY_RUNELEN[rl]:
            needed = tuple((cipher_vals[j] - gp_vals[j]) % MOD for j in range(rl))
            candidates.append((eng_word, needed))
    word_info.append({
        'idx': wi, 'start': start, 'len': rl,
        'buckets': buckets, 'cipher': cipher_vals,
        'candidates': candidates
    })

def score_key(key, mode='SUB'):
    """Count word matches for given key and cipher mode."""
    n_match = 0
    matched = []
    for wi in word_info:
        buckets = wi['buckets']
        cipher_vals = wi['cipher']
        rl = wi['len']
        
        if mode == 'SUB':
            dec = tuple((cipher_vals[j] - key[buckets[j]]) % MOD for j in range(rl))
        elif mode == 'ADD':
            dec = tuple((cipher_vals[j] + key[buckets[j]]) % MOD for j in range(rl))
        elif mode == 'BEAU':
            dec = tuple((key[buckets[j]] - cipher_vals[j]) % MOD for j in range(rl))
        
        for eng_word, gp_vals in wi['candidates']:
            if dec == gp_vals:
                n_match += 1
                matched.append((wi['idx'], eng_word))
                break
    
    return n_match, matched

# Also score based on English letter frequency
ENG_FREQ = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
            0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
            0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
            0.082, 0.003, 0.020, 0.003, 0.003]

def text_quality(key, mode='SUB'):
    """Score text quality based on letter frequency + bigram frequency."""
    if mode == 'SUB':
        dec = [(cipher[i] - key[i % KLEN]) % MOD for i in range(N)]
    elif mode == 'ADD':
        dec = [(cipher[i] + key[i % KLEN]) % MOD for i in range(N)]
    elif mode == 'BEAU':
        dec = [(key[i % KLEN] - cipher[i]) % MOD for i in range(N)]
    
    # Letter frequency correlation
    counts = Counter(dec)
    freq_score = sum(ENG_FREQ[v] * counts.get(v, 0) / N for v in range(MOD))
    
    return freq_score

def combined_score(key, mode='SUB'):
    n_words, matched = score_key(key, mode)
    tq = text_quality(key, mode)
    return n_words * 10 + tq * 100, n_words, matched

# =======================================================================
# Phase 1: Simulated annealing for each mode
# =======================================================================
for mode in ['SUB', 'ADD', 'BEAU']:
    print(f"\n{'='*80}")
    print(f"Mode: {mode} - Simulated Annealing")
    print(f"{'='*80}")
    
    best_overall_key = None
    best_overall_score = -1
    best_overall_words = 0
    best_overall_matched = []
    
    N_RESTARTS = 200
    for restart in range(N_RESTARTS):
        # Random initial key
        key = [random.randint(0, MOD-1) for _ in range(KLEN)]
        
        score, n_words, matched = combined_score(key, mode)
        
        # Simulated annealing
        T = 5.0
        T_min = 0.01
        alpha = 0.995
        
        best_key = list(key)
        best_score = score
        best_nw = n_words
        best_m = matched
        
        while T > T_min:
            # Mutate: change one position
            pos = random.randint(0, KLEN-1)
            old_val = key[pos]
            key[pos] = random.randint(0, MOD-1)
            
            new_score, new_nw, new_matched = combined_score(key, mode)
            
            delta = new_score - score
            if delta > 0 or random.random() < math.exp(delta / T):
                score = new_score
                n_words = new_nw
                matched = new_matched
                if score > best_score:
                    best_score = score
                    best_key = list(key)
                    best_nw = n_words
                    best_m = matched
            else:
                key[pos] = old_val
            
            T *= alpha
        
        if best_nw > best_overall_words or (best_nw == best_overall_words and best_score > best_overall_score):
            best_overall_words = best_nw
            best_overall_score = best_score
            best_overall_key = list(best_key)
            best_overall_matched = best_m
        
        if (restart + 1) % 50 == 0:
            print(f"  Restart {restart+1}/{N_RESTARTS}: best so far = {best_overall_words} words")
    
    print(f"\n  BEST: {best_overall_words} word matches")
    print(f"  Key: {best_overall_key}")
    print(f"  Key (LAT): {''.join(LAT[v] for v in best_overall_key)}")
    
    # Show all words
    if mode == 'SUB':
        dec = [(cipher[i] - best_overall_key[i % KLEN]) % MOD for i in range(N)]
    elif mode == 'ADD':
        dec = [(cipher[i] + best_overall_key[i % KLEN]) % MOD for i in range(N)]
    elif mode == 'BEAU':
        dec = [(best_overall_key[i % KLEN] - cipher[i]) % MOD for i in range(N)]
    
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals)
        is_match = any(wi == m[0] for m in best_overall_matched)
        marker = "Y" if is_match else " "
        print(f"  {marker} w{wi:2d}: '{txt}'")
    
    # Compare with previously confirmed key (for SUB mode)
    if mode == 'SUB':
        confirmed = {2:21, 3:6, 4:19, 5:6, 6:6,
                    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
                    23:2, 24:5, 25:5, 26:27, 27:3, 28:12, 29:19,
                    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
                    46:7, 47:25, 48:24, 50:1, 51:21}
        n_agree = sum(1 for b, v in confirmed.items() if best_overall_key[b] == v)
        print(f"\n  Agrees with previous confirmed: {n_agree}/{len(confirmed)}")
        diffs = {b: (v, best_overall_key[b]) for b, v in confirmed.items() if best_overall_key[b] != v}
        if diffs:
            print(f"  Differences:")
            for b, (old, new) in sorted(diffs.items()):
                print(f"    Bucket {b}: confirmed={old}({LAT[old]}), SA={new}({LAT[new]})")

print(f"\n=== DONE ===")
