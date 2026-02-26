"""
P18 Word-Matching Solver.
Uses known word boundaries (hyphens) to score decryptions by 
counting how many decoded words match a dictionary of English words
encoded in Gematria Primus.

Key insight: with only 260 runes and 53-length key, n-gram scoring
has too little signal. But word matching with known boundaries is
much more discriminative.
"""
import sys, io, os, random, math, time
from collections import Counter, defaultdict

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

# ===== BUILD WORD DICTIONARY =====
# All English words that could appear in LP, organized by GP-length
english_words = set()

# Common English words
common_words = """
A I OF TO IN IS IT OR AN AT BE BY DO GO HE IF ME MY NO ON SO UP US WE
THE AND FOR ARE BUT NOT YOU ALL CAN HER WAS ONE OUR HAS HIS HOW MAN NEW NOW OLD SEE
WAY WHO DID GET HAS HIM HIS HOW ITS LET MAY OWN SAY SHE USE HER WAY HIM DID
THAT THIS WILL YOUR HAVE FROM THEY BEEN WITH SOME WHAT WHEN THEM EACH MAKE
LIKE LONG LOOK MANY FIND KNOW WANT GIVE COME TAKE MOST ONLY OVER SUCH ALSO
BACK INTO YEAR JUST THAN TELL VERY MANY EVEN HAND HIGH KEEP LAST NEED NEXT
THROUGH WITHIN WITHOUT SHOULD BEFORE BETWEEN ALWAYS AROUND BECOME BEHIND
ENOUGH FOLLOW ITSELF NUMBER OTHERS PEOPLE THINGS WITHIN RETURN SACRED
EVERY WHERE AFTER NEVER UNDER STILL THOSE THREE BEING THESE OTHER WHICH THEIR
THERE WOULD ABOUT COULD GOING WORLD GREAT SMALL TRUTH SHAPE FOUND ALONG
NOTHING BECAUSE BELIEVE ANOTHER BETWEEN WHETHER THOUGHT WITHOUT AGAINST
ALTHOUGH HOWEVER ALREADY CERTAIN PERHAPS GENERAL HIMSELF HIMSELF FURTHER
ALL THINGS ARE NOT WORTH CONSUMING PRESERVING
THE WAY THE TRUTH THE LIFE THE LIGHT THE DARK THE SOUL THE PATH THE MIND
THE SELF THE FIRE THE WORD THE WILL THE BODY THE DOOR THE HAND THE HEAD
THE VOID THE SEED THE TREE THE BIRD THE DEEP THE VEIL THE LOSS THE END
AN END AN EASY AN ARBITRARY A BEING A LAW A KOAN A MAN A MASTER A LESSON
A PROFESSOR A STUDENT A CONSCIOUSNESS A HUMAN A VOICE A WARNING A FLAME
A SWORD A TOOL A GIFT A PLACE A STATE A SINGLE A MIGHTY A GREAT A SMALL
A PATTERN A SHADOW A PAGE A BOOK A MESSAGE A PILGRIMAGE A NECESSARY
SACRED TOTIENT FUNCTION PRIMES ENCRYPTED PILGRIM DIVINITY JOURNEY
INNOCENCE ILLUSIONS CERTAINTY REALITY REALITIES DISCOVER DISCOVER
STRUGGLE SUFFERING PILGRIMAGE CIRCUMFERENCE CONSUMPTION PRESERVATION
ADHERENCE BEHAVIORS PRIMALITY ATTACHED PREPARED DESTROY PROGRAM
INTELLIGENCE ENLIGHTENED INSTRUCTION UNREASONABLE DECEPTION
WELCOME TOWARD ULTIMATELY OURSELVES OUTSIDE INSTAR EMERGE COMMAND
QUESTION IMPOSE NOTHING FOLLOW WANDER MASTER STUDENT VOICE
DEATH TRUTH FAITH TRUST FIND SEEK LEARN KNOW GROW LIVE LOVE GIVE
UNDERSTANDING KNOWLEDGE EXPERIENCE CONSCIOUSNESS AWARENESS EXISTENCE
WISDOM SILENCE STILLNESS DARKNESS BRIGHTNESS ETERNALLY MYSTERIOUS
DEEP WITHIN THE UPON EACH THEIR THERE THOSE THREE WHILE WHERE WHICH
CANNOT SHOULD WOULD COULD THROUGH AGAINST BETWEEN WITHOUT BECAUSE
BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT KNOW TRUE TEST KNOWLEDGE
FIND YOUR EXPERIENCE EDIT CHANGE MESSAGE CONTAINED EITHER WORDS NUMBERS
TRIP THOSE HERE NECESSARY ALONG STRUGGLE AND SUFFERING WILL ARRIVE
ONLY GOING MAY UNTO YOURSELF LIVES HOLY OWN SHOULD ENCRYPTED
DECIDED STUDY WENT DOOR WISHES ASKED TOLD NAME CALLED REPLIED AGAIN
WHAT MERELY CONFUSED THOUGHT SOME MORE FINALLY ANSWERED SPECIES
INHABITING ARBITRARY MERELY IRRITATED COULD THINK ANYTHING ELSE
TRAILED PAUSE FOUR PRACTICES WHICH CAUSE LOSS CONSUME MUCH FOLLOWING
ERRORS ENOUGH LUCK STRONG LATER OBTAIN NEED MOST THINGS WORTH
PRESERVE WEAK LOSE GAIN AGAIN MOST THINGS WORTH DOGMA BELONG RIGHT
REASON ABOUT DEATH LOSE PRIMALITY THUS AMASS WEALTH NEVER BECOME
ATTACHED OWN PREPARED DESTROY PROGRAM MIND REALITY DURING EXPLAINED
VOICE INSIDE HEAD DONT HAVE RAISED HAND TELL STOPPED SAID JUST
NO STUDENTS WERE QUESTION DISCOVER INSIDE YOURSELF FOLLOW IMPOSE OTHERS
DUTY EVERY PILGRIM SEEK PAGE TUNNELING SURFACE MUST SHED CIRCUMFERENCES
REARRANGING NUMBERS SHOW PATH DEOR
BURN FIRE FLAME LIGHT DARK SHADOW NIGHT DAY DAWN DUSK STAR MOON SUN
EARTH WATER WIND STONE BONE BLOOD FLESH SKIN HEART SPIRIT BREATH
WALK RUN FLY SWIM FALL RISE TURN MOVE STOP REST WAIT STAY LEAVE COME
OPEN CLOSE LOCK UNLOCK BREAK BUILD MAKE CREATE FORM SHAPE CARVE CUT
READ WRITE SPEAK HEAR LISTEN WATCH OBSERVE THINK FEEL SENSE TOUCH
KING QUEEN LORD LADY KNIGHT WIZARD SAGE MONK PRIEST SCHOLAR SOLDIER
ANCIENT MODERN FIRST SECOND THIRD FOURTH FIFTH PAST PRESENT FUTURE
POWER STRENGTH WISDOM COURAGE HONOR GLORY MERCY GRACE VIRTUE VICE
FRIEND ENEMY BROTHER SISTER FATHER MOTHER CHILD FAMILY PEOPLE NATION
LAND SEA SKY MOUNTAIN VALLEY RIVER LAKE OCEAN FOREST DESERT ISLAND
GOOD EVIL PURE CORRUPT TRUE FALSE RIGHT WRONG JUST UNJUST FAIR UNFAIR
SIMPLE COMPLEX EASY HARD FAST SLOW NEAR FAR SHORT TALL WIDE NARROW
BEGIN MIDDLE ENDING START FINISH COMPLETE WHOLE PART HALF QUARTER
ABOVE BELOW INSIDE OUTSIDE BEYOND BEFORE AFTER DURING UNTIL SINCE
""".split()

# Add LP-specific words
lp_words = """
LIBER PRIMUS CHAPTER INTUS KOAN PARABLE INSTRUCTION VERSE PSALM
INSTAR CICADA EMERGENCE CABAL SHADOWS VOID OBSCURA MOBIUS AETHEREAL
CARNAL ANALOG FORM BUFFERS MOURNFUL CIRCUMFERENCE PRIMALITY
TOTIENT FIBONACCI GEMATRIA ENCRYPTION DECRYPTION CIPHER DECODE
""".split()

# Build GP-encoded dictionary indexed by GP-tuple length
word_dict = defaultdict(set)  # length -> set of tuples
word_text = {}  # tuple -> english word

for w in set(common_words + lp_words):
    if len(w) < 1:
        continue
    gp = tuple(eng_to_gp(w))
    if len(gp) > 0:
        word_dict[len(gp)].add(gp)
        word_text[gp] = w

print(f"Dictionary: {sum(len(v) for v in word_dict.values())} words", flush=True)
for length in sorted(word_dict.keys()):
    print(f"  Length {length}: {len(word_dict[length])} words", flush=True)

# Read cipher
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

# Parse words (sequences of runes between separators)
words = []  # list of lists of cipher positions
current_word = []
rune_idx = 0
for ch in raw:
    if ch in GP:
        current_word.append(rune_idx)
        rune_idx += 1
    elif ch in '-.\n':
        if current_word:
            words.append(list(current_word))
            current_word = []
if current_word:
    words.append(list(current_word))

print(f"Total words: {len(words)}", flush=True)
print(f"Word length distribution:", flush=True)
wl_dist = Counter(len(w) for w in words)
for l in sorted(wl_dist.keys()):
    print(f"  Length {l}: {wl_dist[l]} words", flush=True)

# Confirmed key
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

hc_key = [28, 24, 21, 6, 19, 6, 6, 5, 11, 15, 8, 2, 18, 18, 25, 25, 15, 10, 16, 24, 
13, 11, 20, 2, 5, 5, 27, 3, 12, 19, 14, 17, 5, 18, 4, 25, 27, 26, 24, 16, 5, 8, 
23, 26, 21, 25, 7, 25, 24, 28, 1, 21, 27]

def decrypt(key):
    return [(cipher[i] - key[i%KLEN]) % MOD for i in range(N)]

def word_score(key):
    """Score based on dictionary word matching + length bonus."""
    dec = decrypt(key)
    score = 0.0
    for word_pos in words:
        word_gp = tuple(dec[i] for i in word_pos)
        wlen = len(word_gp)
        if word_gp in word_text:
            # Matched! Score based on word length (longer matches are more valuable)
            score += wlen * wlen  # quadratic bonus for length
        else:
            # Partial credit: check if any prefix/suffix matches
            pass
    return score

# Also build n-gram scorer for tiebreaking
corpus = eng_to_gp("""A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE
TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH
DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN
EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED
WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS
IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE
ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING
YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY
ULTIMATELY YOU WILL DISCOVER AN END TO SELF
IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES
JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE
LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE
YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY
COMMAND YOUR OWN SELF THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED
ALL THINGS SHOULD BE ENCRYPTED
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
AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN
BE PREPARED TO DESTROY ALL THAT YOU OWN PROGRAM YOUR MIND PROGRAM REALITY
DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE
QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS
WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO
LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES
FIND THE DIVINITY WITHIN AND EMERGE REARRANGING THE PRIMES NUMBERS WILL SHOW A PATH TO THE DEOR""")

bg_counts = defaultdict(int)
for i in range(len(corpus)-1):
    bg_counts[(corpus[i], corpus[i+1])] += 1
total_bg = len(corpus) - 1
FLOOR_BG = math.log10(0.01 / total_bg)
bg_logp = {}
for bg, cnt in bg_counts.items():
    bg_logp[bg] = math.log10(cnt / total_bg)

def bg_score(dec):
    s = 0.0
    for i in range(len(dec)-1):
        s += bg_logp.get((dec[i], dec[i+1]), FLOOR_BG)
    return s

def combined_score(key):
    dec = decrypt(key)
    ws = word_score(key)
    bs = bg_score(dec)
    # Word matching is dominant, bigram is tiebreaker
    return ws * 100 + bs

# ===== Show which words already match with HC key =====
print(f"\n{'='*70}", flush=True)
print("MATCHED WORDS WITH HC KEY:", flush=True)
print(f"{'='*70}", flush=True)
dec = decrypt(hc_key)
total_matched = 0
total_runes_matched = 0
for wi, word_pos in enumerate(words):
    word_gp = tuple(dec[i] for i in word_pos)
    word_lat = ''.join(LAT[v] for v in word_gp)
    if word_gp in word_text:
        total_matched += 1
        total_runes_matched += len(word_pos)
        # Check if word uses any unknown key positions
        uses_unknown = any((pos % KLEN) in unknown for pos in word_pos)
        marker = " [uses unknown keys]" if uses_unknown else ""
        print(f"  Word {wi:3d}: {word_lat:20s} = '{word_text[word_gp]}'{marker}", flush=True)

print(f"\nTotal matched: {total_matched}/{len(words)} words ({total_runes_matched}/{N} runes)", flush=True)
print(f"Word score: {word_score(hc_key):.0f}", flush=True)

# ===== For each unknown key position, find which words it affects =====
print(f"\n{'='*70}", flush=True)
print("UNKNOWN KEY POSITIONS AND AFFECTED WORDS:", flush=True)
print(f"{'='*70}", flush=True)
for kp in unknown:
    affected = []
    for wi, word_pos in enumerate(words):
        if any(pos % KLEN == kp for pos in word_pos):
            affected.append(wi)
    word_gps = []
    for wi in affected:
        word_gp = tuple(dec[i] for i in words[wi])
        word_lat = ''.join(LAT[v] for v in word_gp)
        word_gps.append((wi, word_lat))
    print(f"  key[{kp:2d}] affects words: {', '.join(f'{wi}({lat})' for wi, lat in word_gps)}", flush=True)

# ===== HILL CLIMBING WITH WORD MATCHING =====
print(f"\n{'='*70}", flush=True)
print("HILL CLIMBING WITH WORD MATCHING:", flush=True)
print(f"{'='*70}", flush=True)

t0 = time.time()
best_score = -float('inf')
best_key = None
NUM_RESTARTS = 5000

for restart in range(NUM_RESTARTS):
    key = list(hc_key)
    if restart > 0:
        # Random perturbation of unknown positions
        for b in unknown:
            key[b] = random.randint(0, MOD-1)
    
    dec_val = decrypt(key)
    score = combined_score(key)
    
    improved = True
    while improved:
        improved = False
        for b in unknown:
            best_val = key[b]
            best_s = score
            for v in range(MOD):
                if v == key[b]: continue
                key[b] = v
                s = combined_score(key)
                if s > best_s:
                    best_s = s
                    best_val = v
            key[b] = best_val
            if best_s > score:
                score = best_s
                improved = True
    
    if score > best_score:
        best_score = score
        best_key = list(key)
        
        # Count matched words
        dec_val = decrypt(key)
        matched = 0
        for word_pos in words:
            if tuple(dec_val[i] for i in word_pos) in word_text:
                matched += 1
        
        elapsed = time.time() - t0
        print(f"\n[{restart+1:4d}] score={score:.2f} matched={matched}/{len(words)} ({elapsed:.0f}s)", flush=True)
        
        # Show text
        result = []
        rune_i = 0
        word_buf = []
        for ch in raw:
            if ch in GP:
                d = (cipher[rune_i] - key[rune_i % KLEN]) % MOD
                word_buf.append(LAT[d])
                rune_i += 1
            elif ch in '-.\n':
                if word_buf:
                    result.append(''.join(word_buf))
                    word_buf = []
                if ch == '\n':
                    result.append('\n')
                elif ch == '.':
                    result.append('. ')
                else:
                    result.append(' ')
        if word_buf:
            result.append(''.join(word_buf))
        print(f"  {''.join(result)[:200]}", flush=True)
    
    if (restart+1) % 1000 == 0:
        elapsed = time.time() - t0
        print(f"--- {restart+1}/{NUM_RESTARTS} ({elapsed:.0f}s) best={best_score:.2f} ---", flush=True)

# ===== FINAL RESULT =====
print(f"\n{'='*70}", flush=True)
print("FINAL RESULT:", flush=True)
print(f"{'='*70}", flush=True)

dec_final = decrypt(best_key)
print(f"Key: {best_key}", flush=True)
print(f"Key (LAT): {[LAT[k] for k in best_key]}", flush=True)
print(flush=True)

# Full text with word boundaries
result = []
rune_i = 0
word_buf = []
for ch in raw:
    if ch in GP:
        d = (cipher[rune_i] - best_key[rune_i % KLEN]) % MOD
        word_buf.append(LAT[d])
        rune_i += 1
    elif ch in '-.\n':
        if word_buf:
            result.append(''.join(word_buf))
            word_buf = []
        if ch == '\n':
            result.append('\n')
        elif ch == '.':
            result.append('. ')
        else:
            result.append(' ')
if word_buf:
    result.append(''.join(word_buf))
print(''.join(result), flush=True)

print(flush=True)
print("Matched words:", flush=True)
for wi, word_pos in enumerate(words):
    word_gp = tuple(dec_final[i] for i in word_pos)
    word_lat = ''.join(LAT[v] for v in word_gp)
    if word_gp in word_text:
        print(f"  Word {wi:3d}: {word_lat:20s} = '{word_text[word_gp]}'", flush=True)

# Changes from HC key
print(flush=True)
print("Changes from HC key:", flush=True)
for kp in unknown:
    old = hc_key[kp]
    new = best_key[kp]
    changed = " *** CHANGED ***" if old != new else ""
    print(f"  key[{kp:2d}] = {new:2d} ({LAT[new]:3s}) [was {old}({LAT[old]}){changed}]", flush=True)

# IoC
c = Counter(dec_final)
n = len(dec_final)
ic = sum(v*(v-1) for v in c.values()) / (n*(n-1)) * MOD
print(f"\nIoC: {ic:.3f}", flush=True)
print(f"Time: {time.time()-t0:.0f}s", flush=True)
