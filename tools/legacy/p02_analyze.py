"""
P02 Word-by-Word Decode Analysis
=================================
Shows exactly which words decode to LP vocabulary with KNOWN_KEY (+ confirmed anchors),
and which 7-rune window in the P06 koan matches word 4.
"""
import os

RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LATIN = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA',
]
N = 29
KEY_LEN = 43

# KNOWN_KEY from session 17 analysis
KNOWN_KEY = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1, 18, 9, 15, 20, 1,
             6, 21, 20, 25, 21, 11, 16, 22, 15, 16, 16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]
# Override with confirmed anchors
KNOWN_KEY[12] = 26  # Y — from THAT
KNOWN_KEY[13] = 9   # N — from THAT
KNOWN_KEY[14] = 1   # U — from THAT
# Fix singleton conflict: key[2] should give A(24) or I(10) not T(16)
# KNOWN_KEY[2] = 14 → T (WRONG for LP singleton)
# key[2] = 6 → gives A(24), key[2] = 20 → gives I(10)

DIGRAPH_TO_GP = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
MONO_TO_GP = {
    'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
    'D':23,'A':24,'Y':26,
}

def latin_to_gp(text):
    result = []
    t = text.upper()
    i = 0
    while i < len(t):
        if i+1 < len(t) and t[i:i+2] in DIGRAPH_TO_GP:
            result.append(DIGRAPH_TO_GP[t[i:i+2]])
            i += 2
        elif t[i] in MONO_TO_GP:
            result.append(MONO_TO_GP[t[i]])
            i += 1
        else:
            i += 1
    return result

def gp_to_text(gp_list):
    return ''.join(IDX_TO_LATIN[i] for i in gp_list)

def parse_word_structure(path):
    words = []
    cur = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not any(c in RUNE_TO_IDX for c in line):
            continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                cur.append(RUNE_TO_IDX[ch])
            elif ch in '-./':
                if cur:
                    words.append(cur[:])
                    cur = []
    if cur:
        words.append(cur)
    return words

# LP vocabulary for matching
LP_VOCAB = set()
for w in """A AN THE OF AND TO IS IT OR IN ON AT HE HIS HIM WAS HAD NOT YOU WHO BE THIS THAT
WHAT WITH WILL HAVE FROM ALL THEY THEN WHEN THAN ALSO ONLY WELL SOME FOR BUT ARE ALSO
AKOAN KOAN MAN DECIDED GO STUDY WITH MASTER WENT DOOR WISHES STUDENT TOLD NAME CALLED
THOUGHT MOMENT PROFESSOR HUMAN BEING SPECIES CONSCIOUSNESS INHABITING ARBITRARY BODY
MERELY GETTING IRRITATED TRAILED OFF PAUSE WELCOME COME HERE SAME OTHER SONG IDENTITY
LESSON EXPLAINED DURING SOUND HEAR HEARD SPEAKING LISTEN VOICE INNER
WISDOM TRUTH KNOWLEDGE FOLLOW BELIEVE SACRED DIVINE DIVINITY MIND REALITY WORLD PROGRAM
PRIMES TOTIENT INTELLIGENCE INSTRUCTION COMMAND KNOW IMPOSE NOTHING WITHIN PILGRIM
JOURNEY CONSUMPTION PRESERVATION ADHERENCE LOSS BEHAVIORS CAUSE CIRCUMFERENCE
QUESTION DISCOVER DECEPTION STRUGGLING SUFFERING INNOCENCE ILLUSIONS CERTAINTY
FOLLOWING ANSWERED REPLIED SAID ASKED EXPLAINED STARTED THOUGHT THINK
THESONG THEOTHER WITHAME SAMEAS THATTHE THEKOAN FORTHIS CANCOME
NOTHING NOWHERE NOTHINGIS ANSWERED REPLIED CALLED STUDENT PROFESSOR
THESTUDENT THEMASTER AMOMENT AHUMAN ABEING AKOAN AMAN
YOUARE ITHINK INTHIS THEONE FORTHE INTHEE INTHAT
HAUE UOICE BELIEUE NEUER CAUSETHE DIUINITY PRESERUATION BEHAUIORS
DISCOUER CNOW CWESTION HATH THOU THEE THINE THY DOTH HAST""".split():
    gp = tuple(latin_to_gp(w))
    if gp:
        LP_VOCAB.add(gp)

print(f"Vocabulary: {len(LP_VOCAB)} LP words\n")

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'pages', 'page_02', 'runes.txt')
word_src = parse_word_structure(path)

# Decode with KNOWN_KEY (standard version with key[2]=14)
print("=" * 70)
print("DECODE WITH KNOWN_KEY (key[2]=14, gives T for singleton)")
print("=" * 70)
ki = 0
word_decode_info = []
for wi, word in enumerate(word_src):
    enc = []
    for c in word:
        if c == 0:
            enc.append((0, None))
        else:
            enc.append((c, ki % KEY_LEN))
            ki += 1
    plain = tuple((c - KNOWN_KEY[kp]) % N if kp is not None else 0 for c, kp in enc)
    word_text = gp_to_text(plain)
    is_lp = plain in LP_VOCAB
    key_pos = [kp for _, kp in enc if kp is not None]
    word_decode_info.append((wi+1, word, enc, plain, word_text, is_lp, key_pos))

lp_count = sum(1 for *_, is_lp, _ in word_decode_info if is_lp)
print(f"LP words found: {lp_count}/{len(word_src)}")
print()

for (wi, word, enc, plain, word_text, is_lp, key_pos) in word_decode_info:
    mark = " ✓" if is_lp else ""
    key_vals = [KNOWN_KEY[kp] for kp in key_pos]
    key_letters = [IDX_TO_LATIN[v] for v in key_vals]
    print(f"  w{wi:2d} [{len(word):2d}rune] kp={key_pos}: {word_text:24s}{mark}")

# Try key[2] = 6 (gives A) and key[2] = 20 (gives I)
print("\n" + "=" * 70)
print("KEY[2] VARIANTS (fixing singleton conflict)")
print("=" * 70)
for k2_val, label in [(6, "A"), (20, "I")]:
    test_key = list(KNOWN_KEY)
    test_key[2] = k2_val
    # Only word 2 uses kp[2], check what it decodes to
    w2 = word_src[1]  # 0-indexed, word 2 is index 1
    c2 = w2[0]
    p2 = (c2 - k2_val) % N
    print(f"  key[2]={k2_val} ({IDX_TO_LATIN[k2_val]}): w2 cipher ᚢ({c2}) → plain {IDX_TO_LATIN[p2]} ({label})")

# Now show full decode with corrected key[2]=6
print("\n" + "=" * 70)
print("FULL DECODE WITH key[2]=6 (A singleton)")
print("=" * 70)
corrected_key = list(KNOWN_KEY)
corrected_key[2] = 6  # A for singleton
ki = 0
full_words = []
for wi, word in enumerate(word_src):
    enc_list = []
    for c in word:
        if c == 0:
            enc_list.append((0, None))
        else:
            enc_list.append((c, ki % KEY_LEN))
            ki += 1
    plain = tuple((c - corrected_key[kp]) % N if kp is not None else 0 for c, kp in enc_list)
    word_text = gp_to_text(plain)
    is_lp = plain in LP_VOCAB
    mark = " ✓" if is_lp else ""
    full_words.append(word_text)
    print(f"  w{wi+1:2d}: {word_text:24s}{mark}")

print()
print("Full text:", ' '.join(full_words))

# Show word 4 cipher values (kp 5-11)
print("\n" + "=" * 70)
print("WORD 4 CIPHER VALUES (kp 5-11):")
print("=" * 70)
w4 = word_src[3]
print(f"  Cipher runes: {w4}")
print(f"  Cipher values: {[RUNE_TO_IDX[chr(0)] if False else c for c in w4]}")
ki_at_w4 = sum(len(w) for w in word_src[:3])  # 2+1+2=5
print(f"  Key positions: {[ki_at_w4 + j for j in range(len(w4)) if w4[j] != 0]}")
for j, c in enumerate(w4):
    kp = (ki_at_w4 + j) % KEY_LEN
    plain_known = (c - KNOWN_KEY[kp]) % N
    print(f"    j={j}: cipher={c:2d}({IDX_TO_LATIN[c]:3s}), kp={kp:2d}, known_key={KNOWN_KEY[kp]:2d}({IDX_TO_LATIN[KNOWN_KEY[kp]]:3s}), plain={plain_known:2d}({IDX_TO_LATIN[plain_known]:3s})")

# Try finding a 7-char LP phrase from koan that matches w4
print("\n" + "=" * 70)
print("KOAN SEARCH: Find 7-GP-unit sequences that decode consistently from w4 cipher:")
print("=" * 70)
koan_text = """A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE 
MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD 
THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS JUST THE NAME YOUR PARENTS 
CALLED YOU THE STUDENT THOUGHT FOR A MOMENT THEN SAID I AM A HUMAN BEING THAT IS 
NOT WHAT YOU ARE EITHER THAT IS JUST THE SPECIES OF THE BODY YOU ARE INHABITING 
I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY OF THE SPECIES HOMO SAPIENS 
THE PROFESSOR STARTED I AM A REPLIED THE STUDENT BUT HE COULD NOT THINK OF 
ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A PAUSE THE MASTER TOLD THE STUDENT 
THAT IS THE CLOSEST ANYONE HAS COME TO ANSWERING THAT QUESTION CORRECTLY YOU ARE 
WELCOME TO COME STUDY HERE"""

koan_gp = latin_to_gp(koan_text.replace('\n', ' '))
w4_cipher = list(word_src[3])  # cipher runes for word 4
target_len = len(w4_cipher)  # should be 7

print(f"  Word 4 length: {target_len} runes")
found_matches = []
for start in range(len(koan_gp) - target_len + 1):
    segment = koan_gp[start:start+target_len]
    # Derive key for each position
    kps = [ki_at_w4 + j for j in range(target_len)]
    derived_key = {}
    consistent = True
    for j, (c, p) in enumerate(zip(w4_cipher, segment)):
        kp = kps[j] % KEY_LEN
        kv = (c - p) % N
        # Must match confirmed anchors AT those positions
        if kp == 12 and kv != 26: consistent = False; break
        if kp == 13 and kv != 9:  consistent = False; break
        if kp == 14 and kv != 1:  consistent = False; break
        if kp in derived_key and derived_key[kp] != kv:
            consistent = False; break
        derived_key[kp] = kv
    if consistent:
        # Score: how many kp values match KNOWN_KEY
        match_score = sum(1 for kp, kv in derived_key.items() if KNOWN_KEY[kp] == kv)
        text = gp_to_text(segment)
        found_matches.append((match_score, start, text, dict(derived_key)))

found_matches.sort(reverse=True)
for score, start, text, dkey in found_matches[:10]:
    agreement = ", ".join(f"kp{kp}={IDX_TO_LATIN[kv]}" for kp, kv in sorted(dkey.items()))
    print(f"  [{score}/7 match] pos={start:3d}: '{text}' → key: {agreement}")
