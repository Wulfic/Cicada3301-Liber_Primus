"""
P54 Vigenère Solver - k=13 (IoC=2.008)
76 runes, 19 words
Single-rune constraints: word 0 (A/I), word 7 (A/I)
Uses LP corpus for quadgram scoring + word matching
Tests both SUB and ADD modes
"""
import sys, io, os, random, math
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(r'c:\Users\tyler\Repos\Cicada3301')
import functools
print = functools.partial(print, flush=True)

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 13

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

# Build LP corpus from solved pages
corpus_texts = [
    # P59: A WARNING
    "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    # P61: WELCOME
    "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE",
    # P62: WISDOM
    "WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    # P63: SOME WISDOM
    "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS SHADOWS ARE THE REAL BUFFERS VOID CARNAL OBSCURA FORM MOBIUS ANALOGUE VOID MOURNFUL AETHEREAL CABAL",
    # P67: AN INSTRUCTION
    "AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
    # P68: THE LOSS OF DIVINITY
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIOURS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIOURS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY",
    # P74: AN INSTRUCTION
    "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS KNOW THIS",
    # P55: AN END (solved by F-skip + totient)
    "AN END SOME WISDOM IS HARM LESS THAN GOOD IN THOSE CASES LET IT BE AN END IT IS THROUGH THE UNDERSTANDING OF NG THAT ONE MAY DISTINGUISH THE SAGE FROM THE FOOL",
    # P13 (cleartext)
    "SOME WISDOM IS NOT MEANT FOR FOOLS",
    # P10 (cleartext)
    "A KOAN PARABLE FROM THE BOOK OF SHADOWS",
    # Additional LP-style text
    "A KOAN A STUDENT ASKED THE MASTER ARE THERE LAWS THAT A PILGRIM MUST FOLLOW THE MASTER REPLIED STUDY THE FLAME OF A FIRE REPLIED THE MASTER AND THE STUDENT WENT AND SAT BEFORE A FIRE HE RETURNED TO THE MASTER AND SAID I HAVE DONE AS YOU HAVE ASKED AND THE MASTER REPLIED AND WHAT DID THE FIRE TEACH YOU",
    "SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN",
    "THE PARABLE OF THE INSTAR",
]

# Build GP quadgram model
gp_corpus = []
for text in corpus_texts:
    gp_corpus.extend(eng_to_gp(text))

# Build n-gram frequencies
def build_ngram_model(corpus, n=4):
    counts = defaultdict(int)
    for i in range(len(corpus) - n + 1):
        gram = tuple(corpus[i:i+n])
        counts[gram] += 1
    total = sum(counts.values())
    log_freqs = {}
    floor_val = math.log(0.01 / total)
    for gram, count in counts.items():
        log_freqs[gram] = math.log(count / total)
    return log_freqs, floor_val

quad_log, quad_floor = build_ngram_model(gp_corpus, 4)
tri_log, tri_floor = build_ngram_model(gp_corpus, 3)
bi_log, bi_floor = build_ngram_model(gp_corpus, 2)

print(f"Corpus: {len(gp_corpus)} GP values")
print(f"Quadgrams: {len(quad_log)}, Trigrams: {len(tri_log)}, Bigrams: {len(bi_log)}")

def score_quad(plaintext):
    s = 0
    for i in range(len(plaintext) - 3):
        gram = tuple(plaintext[i:i+4])
        s += quad_log.get(gram, quad_floor)
    return s

def score_combined(plaintext):
    s = 0
    for i in range(len(plaintext) - 3):
        gram = tuple(plaintext[i:i+4])
        s += quad_log.get(gram, quad_floor)
    for i in range(len(plaintext) - 2):
        gram = tuple(plaintext[i:i+3])
        s += tri_log.get(gram, tri_floor) * 0.3
    for i in range(len(plaintext) - 1):
        gram = tuple(plaintext[i:i+2])
        s += bi_log.get(gram, bi_floor) * 0.1
    return s

# Read cipher
with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)
print(f"\nP54: {N} runes, k={KLEN}")

# Parse words
words = []
current = []
idx = 0
for ch in raw:
    if ch in GP:
        current.append(idx)
        idx += 1
    elif ch in '-.\n&$':
        if current:
            words.append(list(current))
            current = []
if current:
    words.append(list(current))

word_lens = [len(w) for w in words]
print(f"Words: {len(words)}, lengths: {word_lens}")

# Build dictionary
all_words = set()
for text in corpus_texts:
    all_words.update(text.split())
# Add common English
common = "A I OF TO IN IS IT OR AN AT BE BY DO GO HE IF ME MY NO ON SO UP US WE THE AND FOR ARE BUT NOT YOU ALL ANY CAN HER WAS ONE OUR HAS HIS HOW MAN NEW NOW OLD SEE WAY WHO DID GET HIS HOW ITS LET MAY OWN SAY SHE TOO USE HER THAT THIS WILL YOUR HAVE FROM THEY BEEN WITH SOME WHAT WHEN THEM EACH MAKE LIKE LONG LOOK MANY FIND KNOW WANT GIVE COME TAKE MOST ONLY OVER SUCH ALSO BACK INTO YEAR JUST THAN TELL VERY EVEN HAND HIGH KEEP LAST NEED NEXT SAME SHOW SEEM TURN MUST MUCH MOVE HEAD STILL HERE THEN WELL LEFT WORK CALL LIFE DOWN MORE PART SAID GONE NAME DONE GOOD HELP BORN REAL THROUGH WITHIN WITHOUT SHOULD BEFORE BETWEEN ALWAYS AROUND BECOME BEHIND ENOUGH FOLLOW ITSELF NUMBER OTHERS PEOPLE THINGS RETURN SACRED TOWARD WORLD TRUTH BEING WHICH THEIR THERE WOULD ABOUT COULD GOING GREAT SMALL FOUND ALONG NOTHING BECAUSE BELIEVE ANOTHER WHETHER THOUGHT AGAINST ALTHOUGH HOWEVER ALREADY PERHAPS CONSUME PILGRIM JOURNEY WISDOM STRUGGLE SUFFERING DIVINITY COMMAND PRIMES TOTIENT FUNCTION HOLY ENCRYPTED INTELLIGENCE YOURSELF INNOCENCE ILLUSIONS CERTAINTY REALITY DISCOVER PILGRIMAGE CIRCUMFERENCE CONSUMPTION PRESERVATION ADHERENCE PRIMALITY DECEPTION DESTROY PROGRAM ENLIGHTENED INSTRUCTION UNREASONABLE KOAN PARABLE WELCOME INSTAR EMERGE QUESTION DEATH TRUST LEARN VOICE STUDENT MASTER KNOWLEDGE EXPERIENCE CONSCIOUSNESS AWARENESS EXISTENCE UNDERSTANDING FLAME FIRE REPLIED STUDIED SAT WAR PREPARE PREPARED WEALTH ATTACH ATTACHED AMASS DUST BOOK SACRED SHADOWS VOID CARNAL OBSCURA FORM MOBIUS ANALOGUE MOURNFUL AETHEREAL CABAL LAW LAWS CHAPTER INTUS BEHAVIOURS PRACTICING"
all_words.update(common.split())

gp_dict = {}
for w in all_words:
    gp = tuple(eng_to_gp(w))
    if gp:
        gp_dict[gp] = w

print(f"Dictionary: {len(gp_dict)} unique GP words")

# Single-rune constraints
# Word 0: 1 rune at pos 0 → key[0]: cipher[0]=21
# A(24): key[0] = (21-24)%29 = 26(Y)  
# I(10): key[0] = (21-10)%29 = 11(J)
# Word 7: 1 rune at pos 23 → key[23%13]=key[10]: cipher[23]=17
# A(24): key[10] = (17-24)%29 = 22(OE)
# I(10): key[10] = (17-10)%29 = 7(W)

print("\nSingle-rune constraints:")
print(f"  Word 0 (cipher[0]={cipher[0]}): A → key[0]=26(Y), I → key[0]=11(J)")
print(f"  Word 7 (cipher[23]={cipher[23]}): A → key[10]=22(OE), I → key[10]=7(W)")

# ============================================================
# Hill Climbing for both SUB and ADD modes
# ============================================================
def decrypt_sub(cipher, key, klen):
    return [(cipher[i] - key[i % klen]) % MOD for i in range(len(cipher))]

def decrypt_add(cipher, key, klen):
    return [(cipher[i] + key[i % klen]) % MOD for i in range(len(cipher))]

def word_score(plaintext, words_list):
    """Count dictionary word matches"""
    score = 0
    matched = []
    for wi, wpos in enumerate(words_list):
        word_gp = tuple(plaintext[i] for i in wpos)
        if word_gp in gp_dict:
            score += len(wpos)
            matched.append((wi, gp_dict[word_gp]))
    return score, matched

def hill_climb(cipher, klen, mode, max_restarts=5000, constraints=None):
    """
    constraints: dict of key_pos -> list of allowed values
    """
    n = len(cipher)
    best_score = float('-inf')
    best_key = None
    best_text = None
    best_words = []
    
    for restart in range(max_restarts):
        # Random key
        key = [random.randint(0, MOD-1) for _ in range(klen)]
        
        # Apply constraints
        if constraints:
            for kp, allowed in constraints.items():
                key[kp] = random.choice(allowed)
        
        # Decrypt
        if mode == 'SUB':
            plain = decrypt_sub(cipher, key, klen)
        else:
            plain = decrypt_add(cipher, key, klen)
        
        score = score_combined(plain)
        
        # Hill climb
        improved = True
        while improved:
            improved = False
            for pos in range(klen):
                if constraints and pos in constraints:
                    choices = constraints[pos]
                else:
                    choices = range(MOD)
                
                orig = key[pos]
                for v in choices:
                    if v == orig:
                        continue
                    key[pos] = v
                    if mode == 'SUB':
                        plain = decrypt_sub(cipher, key, klen)
                    else:
                        plain = decrypt_add(cipher, key, klen)
                    new_score = score_combined(plain)
                    if new_score > score:
                        score = new_score
                        improved = True
                        break
                    else:
                        key[pos] = orig
        
        if score > best_score:
            best_score = score
            best_key = list(key)
            if mode == 'SUB':
                best_plain = decrypt_sub(cipher, key, klen)
            else:
                best_plain = decrypt_add(cipher, key, klen)
            w_score, matched = word_score(best_plain, words)
            best_text = ''.join(LAT[v] for v in best_plain)
            best_words = matched
            
            if restart % 100 == 0 or w_score >= 10:
                # Display with word boundaries
                display = []
                for wi, wpos in enumerate(words):
                    w = ''.join(LAT[best_plain[i]] for i in wpos)
                    display.append(w)
                text_disp = ' '.join(display)
                print(f"  R{restart:5d} {mode} score={score:.2f} words={w_score} key={best_key}")
                print(f"    {text_disp}")
                if matched:
                    print(f"    Matched: {matched}")
    
    return best_key, best_score, best_text, best_words

# Run for both modes with all 4 constraint combinations
print("\n" + "=" * 70)
print("HILL CLIMBING - Vigenère SUB mode")
print("=" * 70)

constraint_combos = [
    ({0: [26], 10: [22]}, "A...A"),
    ({0: [26], 10: [7]}, "A...I"),
    ({0: [11], 10: [22]}, "I...A"),
    ({0: [11], 10: [7]}, "I...I"),
]

results = []
for constraints, desc in constraint_combos:
    print(f"\n--- Constraints: word0={desc[0]}, word7={desc[-1]} ({desc}) ---")
    key, score, text, matched = hill_climb(cipher, KLEN, 'SUB', max_restarts=2000, constraints=constraints)
    w_score, w_match = word_score(decrypt_sub(cipher, key, KLEN), words)
    results.append(('SUB', desc, key, score, text, w_match, w_score))

print("\n" + "=" * 70)
print("HILL CLIMBING - Vigenère ADD mode")
print("=" * 70)

# ADD mode constraints
# Word 0: cipher[0]=21, plain=A(24): key[0]=(24-21)%29=3
# Word 0: cipher[0]=21, plain=I(10): key[0]=(10-21)%29=-11%29=18
# Word 7: cipher[23]=17, plain=A(24): key[10]=(24-17)%29=7
# Word 7: cipher[23]=17, plain=I(10): key[10]=(10-17)%29=-7%29=22
add_constraints = [
    ({0: [3], 10: [7]}, "A...A"),
    ({0: [3], 10: [22]}, "A...I"),
    ({0: [18], 10: [7]}, "I...A"),
    ({0: [18], 10: [22]}, "I...I"),
]

for constraints, desc in add_constraints:
    print(f"\n--- ADD Constraints: word0={desc[0]}, word7={desc[-1]} ({desc}) ---")
    key, score, text, matched = hill_climb(cipher, KLEN, 'ADD', max_restarts=2000, constraints=constraints)
    w_score, w_match = word_score(decrypt_add(cipher, key, KLEN), words)
    results.append(('ADD', desc, key, score, text, w_match, w_score))

# Summary
print("\n" + "=" * 70)
print("SUMMARY - Best results by mode and constraint")
print("=" * 70)
results.sort(key=lambda x: x[3], reverse=True)
for mode, desc, key, score, text, matched, w_score in results:
    display = []
    if mode == 'SUB':
        plain = decrypt_sub(cipher, key, KLEN)
    else:
        plain = decrypt_add(cipher, key, KLEN)
    for wi, wpos in enumerate(words):
        w = ''.join(LAT[plain[i]] for i in wpos)
        display.append(w)
    text_disp = ' '.join(display)
    print(f"\n  {mode} {desc}: score={score:.2f}, words_matched={w_score}")
    print(f"    Key: {key}")
    print(f"    Text: {text_disp}")
    if matched:
        print(f"    Matched: {matched}")

# Also try Beaufort mode
print("\n" + "=" * 70)
print("HILL CLIMBING - Beaufort mode (plain = key - cipher)")
print("=" * 70)

def decrypt_beau(cipher, key, klen):
    return [(key[i % klen] - cipher[i]) % MOD for i in range(len(cipher))]

# Beaufort constraints: plain[0] = (key[0] - cipher[0]) % 29
# A(24): key[0] = (24 + 21) % 29 = 45 % 29 = 16
# I(10): key[0] = (10 + 21) % 29 = 31 % 29 = 2
# Word 7: plain = (key[10] - 17) % 29
# A(24): key[10] = (24 + 17) % 29 = 41 % 29 = 12
# I(10): key[10] = (10 + 17) % 29 = 27
beau_constraints = [
    ({0: [16], 10: [12]}, "A...A"),
    ({0: [16], 10: [27]}, "A...I"),
    ({0: [2], 10: [12]}, "I...A"),
    ({0: [2], 10: [27]}, "I...I"),
]

for constraints, desc in beau_constraints:
    print(f"\n--- BEAU Constraints: word0={desc[0]}, word7={desc[-1]} ({desc}) ---")
    
    best_score = float('-inf')
    best_key = None
    for restart in range(2000):
        key = [random.randint(0, MOD-1) for _ in range(KLEN)]
        for kp, allowed in constraints.items():
            key[kp] = random.choice(allowed)
        
        plain = decrypt_beau(cipher, key, KLEN)
        score = score_combined(plain)
        
        improved = True
        while improved:
            improved = False
            for pos in range(KLEN):
                if pos in constraints:
                    choices = constraints[pos]
                else:
                    choices = range(MOD)
                orig = key[pos]
                for v in choices:
                    if v == orig: continue
                    key[pos] = v
                    plain = decrypt_beau(cipher, key, KLEN)
                    ns = score_combined(plain)
                    if ns > score:
                        score = ns
                        improved = True
                        break
                    else:
                        key[pos] = orig
        
        if score > best_score:
            best_score = score
            best_key = list(key)
            plain = decrypt_beau(cipher, best_key, KLEN)
            w_score, w_match = word_score(plain, words)
            
            if restart % 500 == 0 or w_score >= 10:
                display = []
                for wi, wpos in enumerate(words):
                    w = ''.join(LAT[plain[i]] for i in wpos)
                    display.append(w)
                print(f"  R{restart:5d} BEAU score={score:.2f} words={w_score}")
                print(f"    {' '.join(display)}")
    
    plain = decrypt_beau(cipher, best_key, KLEN)
    w_score, w_match = word_score(plain, words)
    results.append(('BEAU', desc, best_key, best_score, '', w_match, w_score))

# Final best
print("\n" + "=" * 70)
print("FINAL BEST RESULT")
print("=" * 70)
results.sort(key=lambda x: x[3], reverse=True)
mode, desc, key, score, text, matched, w_score = results[0]
print(f"Mode: {mode}, Constraints: {desc}")
print(f"Score: {score:.2f}, Words matched: {w_score}")
print(f"Key: {key}")
if mode == 'SUB':
    plain = decrypt_sub(cipher, key, KLEN)
elif mode == 'ADD':
    plain = decrypt_add(cipher, key, KLEN)
else:
    plain = decrypt_beau(cipher, key, KLEN)
display = []
for wi, wpos in enumerate(words):
    w = ''.join(LAT[plain[i]] for i in wpos)
    display.append(w)
print(f"Text: {' '.join(display)}")
if matched:
    print(f"Matched words: {matched}")

print("\nDONE")
