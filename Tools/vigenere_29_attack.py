"""
VIGENÈRE KEY LENGTH 29 ATTACK
Stride analysis showed high IoC at stride=29 for multiple unsolved pages.
29 = GP alphabet size → each position mod 29 has independent Caesar shift.

Attack: split into 29 columns, find optimal shift per column using frequency matching.
"""
import os
from collections import Counter
import math

RUNE_TO_INDEX = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,'\u16C7':12,'\u16C8':13,'\u16C9':14,
    '\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,
    '\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28
}
GP = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
      'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
BASE = r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages"

def load_page(pn):
    path = os.path.join(BASE, f"page_{pn:02d}", "runes.txt")
    if not os.path.exists(path): return []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    rune_text = ''.join(line for line in lines if not (line.strip() and line.strip()[0].isascii() and line.strip()[0].isalpha()))
    return [RUNE_TO_INDEX[c] for c in rune_text if c in RUNE_TO_INDEX]

def ioc29(vals):
    if len(vals) < 2: return 0
    ct = Counter(vals); n = len(vals)
    return 29 * sum(c*(c-1) for c in ct.values()) / (n*(n-1))

def text(vals): return ''.join(GP[v] for v in vals)

# ===== COMPUTE ENGLISH FREQUENCY FROM SOLVED PAGES =====
# Solved pages plaintext (from SOLVED_PLAINTEXT_COLLECTION.md)
SOLVED_TEXT = """
LIBER PRIMUS
A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED
CHAPTER I INTUS
WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE
YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE
LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE
WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY
AN INSTRUCTION COMMAND YOUR OWN SELF
SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER
HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE
ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME
THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED
WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN
THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR
THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER
WHO ARE YOU WHO WISHES TO STUDY HERE
CONFUSED THE MAN THOUGHT SOME MORE
FINALLY HE ANSWERED I AM A HUMAN BEING
THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN
AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED
I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY
THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE
WHO ARE YOU WHO WISHES TO STUDY HERE
THE MAN WAS GETTING IRRITATED I AM HE STARTED
BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF
AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY
AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY
THE LOSS OF DIVINITY
THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS
WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH
WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER
TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING
PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK
IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN
THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING
ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT
OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT
THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH
IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE
THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY
SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN
AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY
A KOAN DURING A LESSON THE MASTER EXPLAINED THE I
THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID
IT IS A VOICE INSIDE YOUR HEAD
I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT
AND HE RAISED HIS HAND TO TELL THE MASTER
THE MASTER STOPPED THE STUDENT AND SAID
THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I
AND THE STUDENTS WERE ENLIGHTENED
AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF
FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS
AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE
PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE
WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE
""".upper()

def text_to_gp(text):
    """Convert English text to GP indices"""
    result = []; i = 0
    while i < len(text):
        if i+1 < len(text):
            di = text[i:i+2]
            dmap = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
            if di in dmap:
                result.append(dmap[di]); i += 2; continue
        smap = {'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
                'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,'T':16,'B':17,'E':18,'M':19,
                'L':20,'D':23,'A':24,'Y':26}
        if text[i] in smap:
            result.append(smap[text[i]])
        i += 1
    return result

# Compute GP frequency distribution from solved text
solved_gp = text_to_gp(SOLVED_TEXT)
freq = Counter(solved_gp)
total = len(solved_gp)
ENGLISH_FREQ = {}
for i in range(29):
    ENGLISH_FREQ[i] = freq.get(i, 0) / total
print("English GP frequency distribution (from solved pages):")
for i in range(29):
    bar = '#' * int(ENGLISH_FREQ[i] * 200)
    print(f"  {GP[i]:3s} ({i:2d}): {ENGLISH_FREQ[i]:.4f} {bar}")

def chi_squared(observed_counts, expected_freq, n):
    """Chi-squared statistic for goodness of fit"""
    chi2 = 0
    for i in range(29):
        expected = expected_freq.get(i, 1e-10) * n
        if expected < 0.001: expected = 0.001
        chi2 += (observed_counts.get(i, 0) - expected)**2 / expected
    return chi2

def find_best_shift(column):
    """Find the Caesar shift that best matches English frequency"""
    n = len(column)
    if n < 3: return 0, 999
    
    best_shift = 0
    best_chi2 = float('inf')
    
    for shift in range(29):
        shifted = [(c - shift) % 29 for c in column]
        counts = Counter(shifted)
        chi2 = chi_squared(counts, ENGLISH_FREQ, n)
        if chi2 < best_chi2:
            best_chi2 = chi2
            best_shift = shift
    
    return best_shift, best_chi2

def score_english(vals):
    t = text(vals).upper()
    score = 0
    for w in ['THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS',
              'ONE','OUR','OUT','HIS','HAS','ITS','WHO','OWN','SAY','SHE','LET']:
        score += t.count(w) * 3
    for w in ['OF','TO','IN','IS','IT','AN','OR','IF','NO','SO','BY','AS','AT','WE','BE']:
        score += t.count(w) * 2
    for w in ['THAT','THIS','WITH','FROM','THEY','HAVE','BEEN','EACH','WILL',
              'YOUR','WHAT','WHEN','THEM','SOME','INTO','THAN','ONLY','SELF',
              'FIND','MAKE','JUST','KNOW','TRUTH','SACRED','WISDOM']:
        score += t.count(w) * 5
    return score

# ===== ATTACK EACH UNSOLVED PAGE =====
print(f"\n{'='*80}")
print("VIGENÈRE KEY LENGTH 29 ATTACK ON ALL UNSOLVED PAGES")
print("=" * 80)

for pn in list(range(17, 55)) + [57, 71]:
    d = load_page(pn)
    if not d or len(d) < 50: continue
    
    # Test key lengths 29, and neighboring values for comparison
    for kl in [29]:
        # Split into columns
        columns = [[] for _ in range(kl)]
        for i, c in enumerate(d):
            columns[i % kl].append(c)
        
        # Find best shift per column
        key = []
        total_chi2 = 0
        for col_idx in range(kl):
            shift, chi2 = find_best_shift(columns[col_idx])
            key.append(shift)
            total_chi2 += chi2
        
        # Decrypt
        dec = [(d[i] - key[i % kl]) % 29 for i in range(len(d))]
        ic = ioc29(dec)
        sc = score_english(dec)
        t = text(dec)
        
        # Also try BEAU mode
        dec_beau = [(key[i % kl] - d[i]) % 29 for i in range(len(d))]
        ic_beau = ioc29(dec_beau)
        sc_beau = score_english(dec_beau)
        
        # Also try ADD mode  
        dec_add = [(d[i] + key[i % kl]) % 29 for i in range(len(d))]
        ic_add = ioc29(dec_add)
        sc_add = score_english(dec_add)
        
        # Pick best mode
        modes = [('SUB', dec, ic, sc), ('BEAU', dec_beau, ic_beau, sc_beau), ('ADD', dec_add, ic_add, sc_add)]
        modes.sort(key=lambda x: x[3], reverse=True)
        best_mode, best_dec, best_ic, best_sc = modes[0]
        
        if best_ic > 1.2 or best_sc > 10:
            result_text = text(best_dec)
            print(f"\n  P{pn:02d} (kl={kl}, {len(d)} runes): IoC={best_ic:.4f}, score={best_sc}, mode={best_mode}")
            print(f"  Key: {key}")
            # Pretty word-split attempt
            print(f"  Text: {result_text[:200]}")

# ===== ALSO TRY KEY LENGTHS 26, 27, 28 FOR COMPARISON =====
print(f"\n{'='*80}")
print("COMPARISON: KEY LENGTHS 26, 27, 28 (to verify 29 is optimal)")
print("=" * 80)

for kl in [26, 27, 28, 29]:
    results = []
    for pn in [17, 20, 32, 40, 44, 50]:
        d = load_page(pn)
        if not d: continue
        columns = [[] for _ in range(kl)]
        for i, c in enumerate(d):
            columns[i % kl].append(c)
        key = [find_best_shift(col)[0] for col in columns]
        dec = [(d[i] - key[i % kl]) % 29 for i in range(len(d))]
        ic = ioc29(dec)
        sc = score_english(dec)
        results.append((pn, ic, sc))
    
    avg_ic = sum(r[1] for r in results) / len(results)
    avg_sc = sum(r[2] for r in results) / len(results)
    detail = ', '.join(f'P{r[0]}:{r[1]:.2f}/{r[2]}' for r in results)
    print(f"  kl={kl}: avg IoC={avg_ic:.4f}, avg score={avg_sc:.1f} | {detail}")

# ===== DEEP DIVE ON BEST PAGES =====
print(f"\n{'='*80}")
print("DEEP DIVE: P20, P17, P40 with key length 29")
print("=" * 80)

for pn in [20, 17, 40, 32, 25, 50, 44]:
    d = load_page(pn)
    if not d: continue
    
    # Key length 29
    kl = 29
    columns = [[] for _ in range(kl)]
    for i, c in enumerate(d):
        columns[i % kl].append(c)
    
    # Find best shift per column with detailed info
    key = []
    for col_idx in range(kl):
        shift, chi2 = find_best_shift(columns[col_idx])
        key.append(shift)
    
    # Decrypt best + 2 alternatives
    for mode_name, decrypt_fn in [
        ('SUB', lambda d,k,kl: [(d[i]-k[i%kl])%29 for i in range(len(d))]),
        ('BEAU', lambda d,k,kl: [(k[i%kl]-d[i])%29 for i in range(len(d))]),
        ('ADD', lambda d,k,kl: [(d[i]+k[i%kl])%29 for i in range(len(d))])
    ]:
        dec = decrypt_fn(d, key, kl)
        ic = ioc29(dec)
        sc = score_english(dec)
        if sc > 15 or ic > 1.3:
            result_text = text(dec)
            print(f"\n  P{pn:02d} {mode_name}: IoC={ic:.4f}, score={sc}")
            print(f"  Key: {key}")
            print(f"  Text: {result_text[:300]}")
