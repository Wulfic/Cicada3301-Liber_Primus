"""
P18 Comprehensive Analysis.
- Clean display of all words with unknown positions marked
- Cross-reference which key positions affect which words
- Show all feasible English words for each group of key positions
- Test AROUND crib propagation
"""
import sys, io, os
from collections import defaultdict, Counter
from itertools import product
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
    23:2, 24:5, 25:5, 26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24, 50:1, 51:21
}
unknown_set = set(range(KLEN)) - set(confirmed.keys())
# Unknown: {0,1,7,8,9,10,11,12,30,31,32,33,34,35,36,37,45,49,52}

hc_key = [28, 24, 21, 6, 19, 6, 6, 5, 11, 15, 8, 2, 18, 18, 25, 25, 15, 10, 16, 24, 
13, 11, 20, 2, 5, 5, 27, 3, 12, 19, 14, 17, 5, 18, 4, 25, 27, 26, 24, 16, 5, 8, 
23, 26, 21, 25, 7, 25, 24, 28, 1, 21, 27]

# Read cipher
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

# Parse words with structure (including separators for display)
words = []
current_word = []
rune_idx = 0
separators = []
current_sep = ''
for ch in raw:
    if ch in GP:
        if current_sep or (not current_word and not words):
            separators.append(current_sep)
            current_sep = ''
        current_word.append(rune_idx)
        rune_idx += 1
    elif ch in '-.\n':
        if current_word:
            words.append(list(current_word))
            current_word = []
        current_sep += ch
if current_word:
    words.append(list(current_word))

# Decrypt with HC key
dec_hc = [(cipher[i] - hc_key[i % KLEN]) % MOD for i in range(N)]

print("=" * 80)
print("P18 WORD-BY-WORD ANALYSIS")
print(f"Total runes: {N}, Total words: {len(words)}, Key length: {KLEN}")
print(f"Unknown key positions ({len(unknown_set)}): {sorted(unknown_set)}")
print("=" * 80)

# Group unknown positions into independent clusters
# Key positions 0,1,7,8,9,10,11,12 and 30,31,32,33,34,35,36,37 and 45,49,52
# Let's identify which words share unknown key positions
key_to_words = defaultdict(list)  # key_position -> [(word_index, position_in_word)]
word_unknowns = {}  # word_index -> set of unknown key positions

for wi, wpos in enumerate(words):
    unk = set()
    for pi, pos in enumerate(wpos):
        kp = pos % KLEN
        if kp in unknown_set:
            unk.add(kp)
            key_to_words[kp].append((wi, pi, pos))
    word_unknowns[wi] = unk

# Display each word
print("\n--- WORD TABLE ---")
print(f"{'Word':>4s} {'Len':>3s} {'#Unk':>4s} {'HC Decrypt':25s} {'Unk Keys':30s} {'Cipher Values':40s}")
for wi, wpos in enumerate(words):
    wlen = len(wpos)
    unk = word_unknowns[wi]
    
    # Build display string with unknowns highlighted
    display = ''
    for pi, pos in enumerate(wpos):
        kp = pos % KLEN
        lat = LAT[dec_hc[pos]]
        if kp in unknown_set:
            display += f'[{lat}]'
        else:
            display += lat
    
    cipher_vals = [cipher[pos] for pos in wpos]
    key_positions = [pos % KLEN for pos in wpos]
    
    print(f"{wi:4d} {wlen:3d} {len(unk):4d}  {display:25s} {str(sorted(unk)):30s} kp={key_positions}")

# Group analysis: what key positions form connected groups?
print("\n" + "=" * 80)
print("KEY POSITION GROUPS (independent clusters):")
print("=" * 80)

# Build adjacency: two key positions are connected if they appear in the same word
from collections import deque
adj = defaultdict(set)
for wi, wpos in enumerate(words):
    unk = [pos % KLEN for pos in wpos if pos % KLEN in unknown_set]
    for i in range(len(unk)):
        for j in range(i+1, len(unk)):
            adj[unk[i]].add(unk[j])
            adj[unk[j]].add(unk[i])

# Find connected components
visited = set()
groups = []
for kp in sorted(unknown_set):
    if kp in visited:
        continue
    group = set()
    queue = deque([kp])
    while queue:
        curr = queue.popleft()
        if curr in visited:
            continue
        visited.add(curr)
        group.add(curr)
        for nbr in adj[curr]:
            if nbr not in visited:
                queue.append(nbr)
    groups.append(sorted(group))

for gi, group in enumerate(groups):
    print(f"\n  Group {gi}: key positions {group}")
    # List all words affected
    affected_words = set()
    for kp in group:
        for wi, pi, pos in key_to_words[kp]:
            affected_words.add(wi)
    for wi in sorted(affected_words):
        wpos = words[wi]
        display = ''
        for pi, pos in enumerate(wpos):
            kp = pos % KLEN
            lat = LAT[dec_hc[pos]]
            if kp in unknown_set:
                display += f'[{lat}]'
            else:
                display += lat
        unk = sorted(word_unknowns[wi])
        print(f"    Word {wi:3d}: {display:25s} (unk keys: {unk})")

# Now let's try the AROUND crib
print("\n" + "=" * 80)
print("TESTING 'AROUND' CRIB (word 22)")
print("=" * 80)

# Word 22 position data
w22 = words[22]
print(f"Word 22 has {len(w22)} rune positions: {w22}")
print(f"Key positions: {[p % KLEN for p in w22]}")
print(f"Cipher values: {[cipher[p] for p in w22]}")
print(f"HC decryption: {''.join(LAT[dec_hc[p]] for p in w22)}")

# Try AROUND = A-R-O-U-N-D = GP [24, 4, 3, 1, 9, 23]
# But wait - "AROUND" might have digraphs... no, no digraphs in AROUND
around_gp = [24, 4, 3, 1, 9, 23]  # A R O U N D
if len(around_gp) == len(w22):
    around_key = {}
    print("\nIf word 22 = 'AROUND':")
    for pi, pos in enumerate(w22):
        kp = pos % KLEN
        needed_key = (cipher[pos] - around_gp[pi]) % MOD
        current = hc_key[kp]
        status = "CONFIRMED" if kp in confirmed else "CHANGE" if needed_key != current else "same"
        around_key[kp] = needed_key
        print(f"  pos {pos} (key[{kp}]): need {needed_key}({LAT[needed_key]}), HC has {current}({LAT[current]}) [{status}]")
    
    # Check if any confirmed positions conflict
    conflicts = False
    for kp, v in around_key.items():
        if kp in confirmed and confirmed[kp] != v:
            print(f"  *** CONFLICT at key[{kp}]: AROUND needs {v}, confirmed is {confirmed[kp]}")
            conflicts = True
    
    if not conflicts:
        print("\n  No conflicts with confirmed positions!")
        # Test propagation: what does the rest of the text look like with these key changes?
        test_key = list(hc_key)
        for kp, v in around_key.items():
            if kp not in confirmed:
                test_key[kp] = v
        
        dec_around = [(cipher[i] - test_key[i % KLEN]) % MOD for i in range(N)]
        
        print("\n  Decryption with AROUND key changes:")
        for wi, wpos in enumerate(words):
            unk = word_unknowns[wi]
            if any(kp in around_key for kp in unk):
                old_text = ''.join(LAT[dec_hc[p]] for p in wpos)
                new_text = ''.join(LAT[dec_around[p]] for p in wpos)
                changed_keys = sorted(unk & set(around_key.keys()))
                print(f"    Word {wi:3d}: {old_text:20s} → {new_text:20s} (changed keys: {changed_keys})")
else:
    print(f"  Length mismatch: 'AROUND' has {len(around_gp)} runes, word 22 has {len(w22)} positions")

# Try word-matching: for each word with 0 unknowns, check if it's a real English word
print("\n" + "=" * 80)
print("ALL-CONFIRMED WORDS (0 unknowns) - are they real words?")
print("=" * 80)

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

# Build dictionary organized by GP tuple
all_words = set()
try:
    with open('words_alpha.txt', 'r') as f:
        for line in f:
            w = line.strip().upper()
            if 1 <= len(w) <= 15:
                all_words.add(w)
except:
    pass

# Add LP-specific words
lp_words = """
A I OF TO IN IS IT OR AN AT BE BY DO GO HE IF ME MY NO ON SO UP US WE
THE AND FOR ARE BUT NOT YOU ALL ANY CAN HER WAS ONE OUR HAS HIS HOW MAN NEW NOW OLD SEE
WAY WHO DID GET HAS HIM HIS HOW ITS LET MAY OWN SAY SHE TOO USE HER
THAT THIS WILL YOUR HAVE FROM THEY BEEN WITH SOME WHAT WHEN THEM EACH MAKE
LIKE LONG LOOK MANY FIND KNOW WANT GIVE COME TAKE MOST ONLY OVER SUCH ALSO
BACK INTO YEAR JUST THAN TELL VERY EVEN HAND HIGH KEEP LAST NEED NEXT
SAME SHOW SEEM TURN MUST MUCH MOVE HEAD STILL HERE THEN WELL LEFT
WORK CALL LIFE DOWN MORE PART SAID GONE NAME DONE GOOD HELP BORN REAL
THROUGH WITHIN WITHOUT SHOULD BEFORE BETWEEN ALWAYS AROUND BECOME BEHIND
ENOUGH FOLLOW ITSELF NUMBER OTHERS PEOPLE THINGS RETURN SACRED TOWARD
EVERY WHERE AFTER NEVER UNDER STILL THOSE THREE BEING THESE OTHER WHICH THEIR
THERE WOULD ABOUT COULD GOING WORLD GREAT SMALL TRUTH SHAPE FOUND ALONG
NOTHING BECAUSE BELIEVE ANOTHER BETWEEN WHETHER THOUGHT WITHOUT AGAINST
CONSUME PILGRIM JOURNEY TOWARD SACRED WISDOM STRUGGLE SUFFERING DIVINITY COMMAND
PRIMES TOTIENT FUNCTION HOLY ENCRYPTED INTELLIGENCE YOURSELF INNOCENCE
ILLUSIONS CERTAINTY REALITY DISCOVER PILGRIMAGE CIRCUMFERENCE
CONSUMPTION PRESERVATION ADHERENCE PRIMALITY DECEPTION WEALTH
DESTROY PROGRAM ENLIGHTENED INSTRUCTION UNREASONABLE
WELCOME ULTIMATELY OURSELVES OUTSIDE INSTAR EMERGE QUESTION IMPOSE WANDER
DEATH TRUST LEARN VOICE STUDENT MASTER KNOWLEDGE EXPERIENCE CONSCIOUSNESS
AWARENESS EXISTENCE UNDERSTANDING DARKNESS BRIGHTNESS SILENCE STILLNESS
DEEP UPON EACH THEIR THOSE THREE WHILE WHICH CANNOT WOULD COULD THROUGH
WORDS NUMBERS NECESSARY ALONG ARRIVE ONLY GOING UNTO LIVES SELF
MERELY CONFUSED ANSWERED INHABITING ARBITRARY THINK
ANYTHING TRAILED PAUSE FOUR PRACTICES CAUSE LOSS CONSUME FOLLOWING
ERRORS ENOUGH LUCK STRONG LATER OBTAIN NEED MOST THINGS WORTH PRESERVE
WEAK LOSE GAIN DOGMA BELONG RIGHT REASON ABOUT AMASS NEVER BECOME MIND
LESSON EXPLAINED VOICE INSIDE HEAD DONT RAISED HAND TELL STOPPED JUST
STUDENTS WERE INSIDE OTHERS DUTY EVERY SEEK PAGE TUNNELING SURFACE MUST
SHED CIRCUMFERENCES REARRANGING PATH DEOR NUMBERS SHOW FIRE FLAME LIGHT
DARK SHADOW NIGHT DAWN DUSK STAR MOON EARTH WATER WIND STONE BONE BLOOD
FLESH SKIN HEART SPIRIT BREATH WALK FALL RISE TURN MOVE STOP REST WAIT
STAY LEAVE OPEN CLOSE LOCK BREAK BUILD CREATE FORM CARVE READ WRITE SPEAK
HEAR LISTEN WATCH OBSERVE FEEL SENSE TOUCH POWER STRENGTH COURAGE HONOR
GLORY MERCY GRACE VIRTUE FRIEND ENEMY BROTHER SISTER FATHER MOTHER CHILD
FAMILY LAND SEA SKY MOUNTAIN VALLEY RIVER LAKE OCEAN FOREST DESERT ISLAND
GOOD EVIL PURE TRUE FALSE RIGHT WRONG JUST FAIR SIMPLE COMPLEX EASY HARD
FAST SLOW NEAR SHORT TALL WIDE BEGIN MIDDLE START FINISH COMPLETE WHOLE
PART HALF ABOVE BELOW INSIDE BEYOND BEFORE AFTER DURING UNTIL SINCE WORD
FEAR HOPE LOVE HATE CARE WILL WHAT THAT WITH THIS FROM ALSO OVER INTO
LIAR PERHAPS GENERAL LAW LAWS FOOL FOOLS WISE WISDOM FOOLISH REASON
MORALS MORAL VALUE VALUES SERVICE SERVANT CONTROL CONTROLLED CONTROLLER
OBEY OBEDIENCE DISOBEY DISOBEDIENCE SERVE SERVITUDE CHAINS CHAINS FREE
FREEDOM LIBERTY LIBERATE LIBERATION SLAVE SLAVERY PROPERTY OWNER OWNED
OWNED POSSESS POSSESS POSSESSED POSSESSOR ATTACHMENT DETACHMENT DESIRE
ANGER GREED PRIDE ENVY SLOTH GLUTTONY LUST VIRTUE VIRTUES VICE VICES
SOCIETY CULTURE CIVILIZATION GOVERN GOVERNMENT RULE RULER RULER RULED
AUTHORITY POWER FORCE VIOLENCE WAR PEACE CONFLICT HARMONY ORDER CHAOS
SYSTEM STRUCTURE HIERARCHY EQUAL EQUALITY INEQUALITY JUSTICE INJUSTICE
TRUTH LIES LIE DECEIT DECEPTION HONEST HONESTY DISHONEST ILLUSION
REALITY PERCEPTION APPEARANCE SURFACE DEPTH SHALLOW PROFOUND MYSTERY
SECRECY SECRET HIDDEN REVEALED REVEAL CONCEAL CONCEALED OPEN CLOSED
KNOWN UNKNOWN CERTAIN UNCERTAIN DOUBT FAITH BELIEF UNBELIEF SKEPTIC
NATURAL NATURE ARTIFICIAL MACHINE ORGANIC MECHANICAL SPIRIT MATERIAL
MIND BODY SOUL CONSCIOUSNESS UNCONSCIOUS AWARE UNAWARE AWAKE ASLEEP
DREAM NIGHTMARE VISION SIGHT BLIND SEEING PATTERN RANDOM DESIGN CHANCE
FATE DESTINY CHOICE FREEWILL PREDESTINED DETERMINED DETERMINED
""".split()
for w in lp_words:
    all_words.add(w.upper())

# Build GP dictionary
gp_dict = defaultdict(set)  # length -> set of GP tuples
gp_text = {}  # GP tuple -> English word
for w in all_words:
    gp = tuple(eng_to_gp(w))
    if len(gp) >= 1:
        gp_dict[len(gp)].add(gp)
        gp_text[gp] = w

print(f"Total dictionary: {len(all_words)} words, {sum(len(v) for v in gp_dict.values())} unique GP encodings")

# Check each 0-unknown word
for wi, wpos in enumerate(words):
    if word_unknowns[wi]:
        continue
    wlen = len(wpos)
    word_gp = tuple(dec_hc[p] for p in wpos)
    word_lat = ''.join(LAT[v] for v in word_gp)
    matched = word_gp in gp_text
    match_str = f" = '{gp_text[word_gp]}'" if matched else ""
    
    # Also try to find close matches (1 letter off)
    close = []
    if not matched:
        for eng_gp in gp_dict.get(wlen, set()):
            diff = sum(1 for a, b in zip(word_gp, eng_gp) if a != b)
            if diff == 1:
                close.append(gp_text[eng_gp])
    close_str = f"  (close: {close[:5]})" if close else ""
    
    print(f"  Word {wi:3d} ({wlen}): {word_lat:20s} {'MATCH' if matched else 'NO MATCH':10s}{match_str}{close_str}")

# KEY INSIGHT: let's trace through what the KEY ITSELF might look like as a GP word/phrase
print("\n" + "=" * 80)
print("KEY AS GP TEXT (key values → rune → Latin)")
print("=" * 80)
key_text_confirmed = ''
key_text_hc = ''
for i in range(KLEN):
    if i in confirmed:
        key_text_confirmed += LAT[confirmed[i]]
        key_text_hc += LAT[confirmed[i]]
    else:
        key_text_confirmed += '?'
        key_text_hc += LAT[hc_key[i]]
print(f"Confirmed: {key_text_confirmed}")
print(f"HC guess:  {key_text_hc}")
print(f"  Key as values: {hc_key}")

# The key might be a meaningful phrase in GP/English
# Let's look for patterns
# Known: ??NGMGG??????EAEAESITAPJLTHCCIAOEOM????????ATCHDYNG?WAEA?UNG?
# That's 53 characters in GP

# Let's try common LP phrases as keys
print("\n" + "=" * 80)
print("TESTING LP PHRASES AS KEY")
print("=" * 80)

test_phrases = [
    "DIVINITY",
    "CIRCUMFERENCE",
    "CONSUMPTION",
    "SOME WISDOM IS NOT MEANT FOR FOOLS",
    "LIBER PRIMUS",
    "THE INSTAR EMERGENCE",
    "AN INSTRUCTION",
    "A PILGRIM ON A JOURNEY",
    "WELCOME PILGRIM TO THE GREAT JOURNEY",
    "THE LOSS OF DIVINITY",
    "COMMAND LINE",
    "WITHIN YOU WITHOUT YOU",
    "PARABLE",
    "KOAN",
    "INTUS",
    "MOBIUS",
    "THE CIRCUMFERENCE OF KNOWLEDGE",
    "ADHERENCE",
    "PRESERVATION",
    "PRIMALITY",
    "PRIMES",
    "KNOW THYSELF",
]

for phrase in test_phrases:
    gp_phrase = eng_to_gp(phrase)
    if len(gp_phrase) != KLEN:
        continue
    
    # Check if known key positions match
    matches = 0
    conflicts = 0
    for kp, v in confirmed.items():
        if kp < len(gp_phrase):
            if gp_phrase[kp] == v:
                matches += 1
            else:
                conflicts += 1
    
    if conflicts == 0:
        print(f"  PERFECT MATCH: '{phrase}' ({len(gp_phrase)} GP vals, {matches}/{len(confirmed)} confirmed match)")
    elif matches > 10:
        print(f"  Partial: '{phrase}' ({matches} match, {conflicts} conflict)")

# Also try: what 53-rune text has the confirmed values at the right positions?
# This is a cryptographic constraint satisfaction problem

# Let's try to identify common LP chapter/section headers and verse references
print("\n" + "=" * 80)
print("KEY LENGTH ANALYSIS")
print("=" * 80)
print(f"Key length = {KLEN} = prime")
print(f"N = {N} = {N} = 4 * 65 = 4 * 5 * 13 = 260")
print(f"N / KLEN = {N / KLEN:.4f} ≈ {N // KLEN} remainder {N % KLEN}")
print(f"53 is the 16th prime")

# Check: what are the ACTUAL rune counts per word?
print("\n" + "=" * 80)
print("WORD LENGTHS AND KEY POSITION MAPPING")  
print("=" * 80)

for wi, wpos in enumerate(words):
    wlen = len(wpos)
    kps = [p % KLEN for p in wpos]
    unk_kps = [kp for kp in kps if kp in unknown_set]
    conf_kps = [kp for kp in kps if kp not in unknown_set]
    word_lat = ''.join(LAT[dec_hc[p]] for p in wpos)
    print(f"  Word {wi:3d} ({wlen:2d} runes): {word_lat:25s} key_pos={kps}")

# Final: try global optimization where we simultaneously test 
# key[30-34] = values that make word 22 = AROUND
# and cross-check other words using those same positions
print("\n" + "=" * 80)
print("CROSS-VALIDATION: If word 22 = AROUND, what happens to other words?")
print("=" * 80)

# Word 22 rune positions
w22_pos = words[22]
w22_kps = [p % KLEN for p in w22_pos]
print(f"Word 22 positions: {w22_pos}, key positions: {w22_kps}")

# AROUND = [24, 4, 3, 1, 9, 23]
target_gp = [24, 4, 3, 1, 9, 23]
around_key_vals = {}
for pi, pos in enumerate(w22_pos):
    kp = pos % KLEN
    needed = (cipher[pos] - target_gp[pi]) % MOD
    around_key_vals[kp] = needed
    print(f"  key[{kp}] = {needed} ({LAT[needed]})")

# Apply to test key and decrypt
test_key = list(hc_key)
for kp, v in around_key_vals.items():
    if kp not in confirmed:
        test_key[kp] = v

dec_test = [(cipher[i] - test_key[i % KLEN]) % MOD for i in range(N)]

# Show all affected words
print("\nAll words affected by AROUND key changes:")
for wi, wpos in enumerate(words):
    unk = word_unknowns[wi]
    changed = unk & set(around_key_vals.keys())
    if not changed:
        continue
    
    old = ''.join(LAT[dec_hc[p]] for p in wpos)
    new = ''.join(LAT[dec_test[p]] for p in wpos)
    new_gp = tuple(dec_test[p] for p in wpos)
    match = f" = '{gp_text[new_gp]}'" if new_gp in gp_text else ""
    print(f"  Word {wi:3d}: {old:25s} → {new:25s}{match}")

# Try every combination for the group [30,31,32,33,34,35,36,37]
# That's 8 unknown positions, 29^8 is too many
# But we can use word constraints to narrow down

# Words that depend ONLY on group [30-37]:
# Word 9: PR (keys [30,31])
# Word 22: AIAEAND (keys [30,31,32,33,34]) -- 5 in this group
# Word 49: HNGEO (keys [30,31,32]) -- 3 in this group
# Word 63: NGNGEO (keys [30]) -- 1 in this group
# Word 64: GXFOE (keys [31,32,33,34]) -- 4 in this group
# Word 10: ESOWSU (keys [32,33,34,35,36,37]) -- 6 in this group
# Word 23: YO (keys [35,36]) -- 2 in this group
# Word 50: DEOEDHC (keys [33,34,35,36,37]) -- 5 in this group  
# Word 65: CLAREECNTH (keys [35,36,37]) -- 3 in this group
# Word 24: UWIETTHAAE (keys [37]) -- 1 in this group

# Strategy: enumerate key[30-34] (5 positions, 29^5 = 20M too much)
# Better: use word 22 (AROUND) to fix key[30-34], then enumerate [35-37]

print("\n" + "=" * 80)
print("ENUMERATE key[35,36,37] with AROUND fixing key[30-34]")
print("=" * 80)

# Fix key[30-34] from AROUND:
fixed_30_34 = {}
for kp, v in around_key_vals.items():
    if 30 <= kp <= 34:
        fixed_30_34[kp] = v
print(f"Fixed from AROUND: {fixed_30_34}")

# Now enumerate key[35], key[36], key[37] (29^3 = 24389 combos)
best_score = -1
best_combo = None
results = []

for v35 in range(MOD):
    for v36 in range(MOD):
        for v37 in range(MOD):
            trial_key = list(hc_key)
            for kp, v in fixed_30_34.items():
                trial_key[kp] = v
            trial_key[35] = v35
            trial_key[36] = v36
            trial_key[37] = v37
            
            # Score: count dictionary word matches for affected words
            score = 0
            matched_words = []
            for wi in [9, 10, 22, 23, 24, 49, 50, 63, 64, 65]:
                wpos = words[wi]
                word_gp = tuple((cipher[p] - trial_key[p % KLEN]) % MOD for p in wpos)
                if word_gp in gp_text:
                    score += len(wpos)  # weight by word length
                    matched_words.append((wi, gp_text[word_gp]))
            
            if score > best_score:
                best_score = score
                best_combo = (v35, v36, v37)
                best_matches = matched_words
            
            if len(matched_words) >= 3:
                results.append((score, v35, v36, v37, matched_words))

results.sort(reverse=True)
print(f"\nBest: key[35,36,37] = {best_combo}, score = {best_score}")
print(f"  Matches: {best_matches}")

print(f"\nTop results (3+ word matches):")
for score, v35, v36, v37, matches in results[:20]:
    print(f"  [{v35:2d},{v36:2d},{v37:2d}] score={score:3d}: {matches}")

# Now do the same for the [7-12] group
print("\n" + "=" * 80)  
print("ENUMERATE key[7-12] (6 positions, too many for brute force)")
print("=" * 80)

# Words affected by key[7-12]:
# Word 1: IAUR (keys [7,8]) - 2 unknowns
# Word 17: GIASLTH (keys [7,8]) - 2 unknowns  
# Word 30: EEJWWR (keys [7,8,9,10,11,12]) - 6 unknowns
# Word 41: FEONGFJYTH (keys [1,7]) - mixed with key[1]
# Word 42: ROUGH (keys [8,9,10,11,12]) - 5 unknowns
# Word 58: HOENGXIAE (keys [7,8,9,10,11,12]) - 6 unknowns

# Sub-enumerate key[7,8] first using words 1 and 17
print("\nEnumerating key[7,8] using words 1 (IAUR) and 17 (GIASLTH):")
w1_pos = words[1]
w17_pos = words[17]

for v7 in range(MOD):
    for v8 in range(MOD):
        trial = list(hc_key)
        trial[7] = v7
        trial[8] = v8
        
        w1_gp = tuple((cipher[p] - trial[p % KLEN]) % MOD for p in w1_pos)
        w17_gp = tuple((cipher[p] - trial[p % KLEN]) % MOD for p in w17_pos)
        
        w1_match = w1_gp in gp_text
        w17_match = w17_gp in gp_text
        
        if w1_match or w17_match:
            w1_text = gp_text.get(w1_gp, ''.join(LAT[v] for v in w1_gp))
            w17_text = gp_text.get(w17_gp, ''.join(LAT[v] for v in w17_gp))
            m1 = "✓" if w1_match else " "
            m17 = "✓" if w17_match else " "
            print(f"  key[7]={v7:2d}({LAT[v7]:3s}), key[8]={v8:2d}({LAT[v8]:3s}): w1={w1_text:15s}{m1} w17={w17_text:15s}{m17}")

# Try the [0,1,52] group with word constraints
print("\n" + "=" * 80)
print("ENUMERATE key[0,1,52] using affected words")
print("=" * 80)

# Words: 0 (FFMGNX, keys[0,1]), 15 (DISTH, keys[0,1,52]), 27 (THED, keys[0,1,52])
# Also: 40 (OEMIAUL, keys[0,49,52]), 54 (NGTHUMNGTHDF, keys[0,49,52])
# And: 41 (FEONGFJYTH, keys[1,7]), 55 (CIAJU, keys[1])

# Enumerate key[0,1,52] (29^3 = 24389 combos)
best_012 = None
best_012_score = -1
results_012 = []

for v0 in range(MOD):
    for v1 in range(MOD):
        for v52 in range(MOD):
            trial = list(hc_key)
            trial[0] = v0
            trial[1] = v1
            trial[52] = v52
            
            score = 0
            matched = []
            for wi in [0, 15, 27, 55]:
                wpos = words[wi]
                word_gp = tuple((cipher[p] - trial[p % KLEN]) % MOD for p in wpos)
                if word_gp in gp_text:
                    score += len(wpos)
                    matched.append((wi, gp_text[word_gp]))
            
            if score > best_012_score:
                best_012_score = score
                best_012 = (v0, v1, v52)
                best_012_matches = matched
            
            if len(matched) >= 2:
                results_012.append((score, v0, v1, v52, matched))

results_012.sort(reverse=True)
print(f"\nBest: key[0,1,52] = {best_012}, score = {best_012_score}")
print(f"  Matches: {best_012_matches}")

print(f"\nTop results (2+ word matches):")
for score, v0, v1, v52, matches in results_012[:20]:
    print(f"  [{v0:2d},{v1:2d},{v52:2d}] score={score:3d}: {matches}")

# Enumerate key[45,49] - these are tangled through many words
print("\n" + "=" * 80)
print("ENUMERATE key[45,49]")
print("=" * 80)

# Words affected: 13 (YARIN, [45,49]), 25 (NAEI, [45]), 26 (NGAUE, [49])
# 37 (GOEOERTHE, [45]), 40 (OEMIAUL, [0,49,52]), 53 (FC, [45])
# 54 (NGTHUMNGTHDF, [0,49,52]), 66 (ANGIA, [45])

for v45 in range(MOD):
    for v49 in range(MOD):
        trial = list(hc_key)
        trial[45] = v45
        trial[49] = v49
        
        score = 0
        matched = []
        for wi in [13, 25, 26, 37, 53, 66]:
            wpos = words[wi]
            word_gp = tuple((cipher[p] - trial[p % KLEN]) % MOD for p in wpos)
            if word_gp in gp_text:
                score += len(wpos)
                matched.append((wi, gp_text[word_gp]))
        
        if len(matched) >= 2:
            print(f"  key[45]={v45:2d}({LAT[v45]:3s}), key[49]={v49:2d}({LAT[v49]:3s}): score={score:3d} {matched}")

print("\nDONE")
