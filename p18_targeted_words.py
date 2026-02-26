"""
P18 Targeted Word Solver.
For each word, count how many of its positions depend on unknown keys.
Words with only 1 unknown key position are the most constrainable.
"""
import sys, io, os
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

# Large word list
all_words_text = """
A I OF TO IN IS IT OR AN AT BE BY DO GO HE IF ME MY NO ON SO UP US WE
THE AND FOR ARE BUT NOT YOU ALL ANY CAN HER WAS ONE OUR HAS HIS HOW MAN NEW NOW OLD SEE
WAY WHO DID GET HAS HIM HIS HOW ITS LET MAY OWN SAY SHE TOO USE HER WAY HIM DID
THAT THIS WILL YOUR HAVE FROM THEY BEEN WITH SOME WHAT WHEN THEM EACH MAKE
LIKE LONG LOOK MANY FIND KNOW WANT GIVE COME TAKE MOST ONLY OVER SUCH ALSO
BACK INTO YEAR JUST THAN TELL VERY EVEN HAND HIGH KEEP LAST NEED NEXT
SAME SHOW SEEM TURN MUST MUCH MOVE HEAD JUST STILL HERE THEN WELL LEFT
WORK CALL LIFE DOWN MORE PART SAID GONE NAME DONE GOOD HELP BORN REAL
BORN USED MADE HELD TOLD CAME WENT TOOK GAVE FELT LOSE LOST UPON SURE
THROUGH WITHIN WITHOUT SHOULD BEFORE BETWEEN ALWAYS AROUND BECOME BEHIND
ENOUGH FOLLOW ITSELF NUMBER OTHERS PEOPLE THINGS RETURN SACRED TOWARD
EVERY WHERE AFTER NEVER UNDER STILL THOSE THREE BEING THESE OTHER WHICH THEIR
THERE WOULD ABOUT COULD GOING WORLD GREAT SMALL TRUTH SHAPE FOUND ALONG
NOTHING BECAUSE BELIEVE ANOTHER BETWEEN WHETHER THOUGHT WITHOUT AGAINST
ALTHOUGH HOWEVER ALREADY CERTAIN PERHAPS GENERAL FURTHER BELIEVE CONSUME
PILGRIM JOURNEY TOWARD SACRED WISDOM STRUGGLE SUFFERING DIVINITY COMMAND
PRIMES TOTIENT FUNCTION HOLY ENCRYPTED INTELLIGENCE YOURSELF INNOCENCE
ILLUSIONS CERTAINTY REALITY REALITIES DISCOVER PILGRIMAGE CIRCUMFERENCE
BEHAVIORS CONSUMPTION PRESERVATION ADHERENCE PRIMALITY DECEPTION WEALTH
ATTACHED PREPARED DESTROY PROGRAM ENLIGHTENED INSTRUCTION UNREASONABLE
WELCOME ULTIMATELY OURSELVES OUTSIDE INSTAR EMERGE QUESTION IMPOSE WANDER
DEATH TRUST LEARN VOICE STUDENT MASTER KNOWLEDGE EXPERIENCE CONSCIOUSNESS
AWARENESS EXISTENCE UNDERSTANDING DARKNESS BRIGHTNESS SILENCE STILLNESS
DEEP UPON EACH THEIR THOSE THREE WHILE WHICH CANNOT WOULD COULD THROUGH
BETWEEN WITHOUT AGAINST BELIEVE EXCEPT CHANGE MESSAGE CONTAINED EITHER
WORDS NUMBERS TRIP NECESSARY ALONG ARRIVE ONLY GOING UNTO LIVES SELF
DECIDED STUDY WENT DOOR WISHES ASKED TOLD NAME CALLED REPLIED AGAIN
MERELY CONFUSED ANSWERED SPECIES INHABITING ARBITRARY IRRITATED THINK
ANYTHING TRAILED PAUSE FOUR PRACTICES CAUSE LOSS CONSUME MUCH FOLLOWING
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
SAID BEEN HAVE BEEN TAKE LIKE KNOW MAKE WANT GIVE FIND TELL COME BACK
WORK CALL LIFE DOWN MORE PART GONE NAME DONE HELP BORN REAL USED MADE
HELD TOOK GAVE FELT SURE UPON ONCE BODY TOOK BOOK TEST EDIT EITHER OR
FEAR HOPE LOVE HATE CARE WILL WHAT THAT WITH THIS FROM ALSO OVER INTO
THEM THAN BEEN LIKE JUST ONLY SOME VERY EVEN MUCH MANY MORE MOST SUCH ANY
OWN OUR WAY SET TWO OUT HOW HAS ITS HAD DAY GOT GOD MAY SEE ASK NEW PUT OLD
HIS HER ONE ALL CAN RUN USE SHE HIM HER HAS BUT NOR YET RED RAN GOD MEN
BIG END WAS FAR TOO FEW AGO FEW BAD BIG CUT DRY DUE EAR FLY KEY LAY LET
LIE LOW MAP MIS MIX ODD PAY RUN SAD SIT TIE TIP TOP TRY WET WIN RAN SAT
BEING KNOWN WORLD FOUND POINT RIGHT MIGHT THINK PLACE STATE GROUP LARGE
ORDER LEVEL POWER EARLY YOUNG HOUSE OTHER GREAT GIVEN LOCAL SMALL HUMAN
WHERE SOCIAL ALONG WHOSE LATER SHALL ABOVE OFTEN UNDER THIRD UNTIL WHOLE
STILL FINAL TAKEN USING BEGAN WHITE SENSE COULD TIMES THREE YEARS WOULD
CLOSE SEVEN EIGHT BASED QUITE BEHIND BECOME AROUND NUMBER COURSE DURING
AMONG NATURE SYSTEM MEMBER WITHIN PEOPLE UNITED ACROSS SECOND FAMILY
RATHER TWELVE FORMER CHURCH SINGLE COMMON ALWAYS GROUND REASON SIMPLY
CALLED CHANGE BETTER ITSELF DURING ENOUGH OTHERS LONGER NEARLY RESULT
LIVING STRONG WOMEN TAKING COMING RETURN BEFORE PUBLIC COMING RETURN
AN END BEING DOING HAVING MAKING TAKING GOING GIVING FINDING
TELLING COMING GETTING SEEING KNOWING WANTING THINKING
BELIEVING FOLLOWING CONSUMING PRESERVING UNDERSTANDING
THE TRUTH THE PATH THE MIND THE SELF THE FIRE THE WORD THE WILL THE BODY
LIBER PRIMUS CHAPTER INTUS KOAN PARABLE VERSE PSALM SOME AN
INSTAR CICADA EMERGENCE CABAL SHADOWS VOID OBSCURA MOBIUS
CARNAL ANALOG FORM BUFFERS MOURNFUL
""".split()

# Build GP dictionary indexed by GP-tuple length
word_dict = defaultdict(set)
word_text = {}
for w in set(all_words_text):
    if len(w) < 1: continue
    gp = tuple(eng_to_gp(w))
    if len(gp) > 0:
        word_dict[len(gp)].add(gp)
        word_text[gp] = w

print(f"Dictionary: {sum(len(v) for v in word_dict.values())} unique GP-words")

# Read cipher
with open('LiberPrimus/pages/page_18/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()
cipher = [GP[c] for c in raw if c in GP]
N = len(cipher)

# Parse words
words = []
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

confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}
unknown_set = set(range(KLEN)) - set(confirmed.keys())

hc_key = [28, 24, 21, 6, 19, 6, 6, 5, 11, 15, 8, 2, 18, 18, 25, 25, 15, 10, 16, 24, 
13, 11, 20, 2, 5, 5, 27, 3, 12, 19, 14, 17, 5, 18, 4, 25, 27, 26, 24, 16, 5, 8, 
23, 26, 21, 25, 7, 25, 24, 28, 1, 21, 27]

# For each word, identify which key positions are unknown
print(f"\n{'='*70}")
print("WORD ANALYSIS BY NUMBER OF UNKNOWN POSITIONS:")
print(f"{'='*70}")

dec_hc = [(cipher[i] - hc_key[i%KLEN]) % MOD for i in range(N)]

for n_unk in range(8):
    words_with_n = []
    for wi, wpos in enumerate(words):
        unk_keys = set()
        for pos in wpos:
            kp = pos % KLEN
            if kp in unknown_set:
                unk_keys.add(kp)
        if len(unk_keys) == n_unk:
            word_lat = ''.join(LAT[dec_hc[i]] for i in wpos)
            matched = tuple(dec_hc[i] for i in wpos) in word_text
            words_with_n.append((wi, word_lat, matched, unk_keys))
    
    if words_with_n:
        print(f"\n--- Words with {n_unk} unknown key position(s): ---")
        for wi, lat, matched, unk_keys in words_with_n:
            match_str = "MATCHED" if matched else ""
            unk_str = f" [unknown keys: {sorted(unk_keys)}]" if unk_keys else ""
            print(f"  Word {wi:3d}: {lat:20s} {match_str:8s}{unk_str}")

# For words with exactly 1 unknown position, try all 29 values
print(f"\n{'='*70}")
print("WORDS WITH 1 UNKNOWN: EXHAUSTIVE SEARCH")
print(f"{'='*70}")

key_constraints = defaultdict(list)  # key_pos -> list of (value, word_text, word_idx)

for wi, wpos in enumerate(words):
    unk_keys = set()
    unk_positions = {}  # key_position -> list of (word_index, cipher_position)
    for pi, pos in enumerate(wpos):
        kp = pos % KLEN
        if kp in unknown_set:
            unk_keys.add(kp)
            if kp not in unk_positions:
                unk_positions[kp] = []
            unk_positions[kp].append((pi, pos))
    
    if len(unk_keys) != 1:
        continue
    
    unk_kp = list(unk_keys)[0]
    wlen = len(wpos)
    
    # Try all 29 values for the unknown key position
    candidates = []
    for v in range(MOD):
        # Decrypt this word with key[unk_kp] = v
        word_gp = []
        for pi, pos in enumerate(wpos):
            kp = pos % KLEN
            if kp == unk_kp:
                word_gp.append((cipher[pos] - v) % MOD)
            else:
                word_gp.append(dec_hc[pos])  # use confirmed key
        word_tuple = tuple(word_gp)
        if word_tuple in word_text:
            candidates.append((v, word_text[word_tuple]))
    
    word_lat = ''.join(LAT[dec_hc[i]] for i in wpos)
    if candidates:
        print(f"\n  Word {wi:3d} ({word_lat}), key[{unk_kp}] unknown:")
        for v, eng in candidates:
            print(f"    key[{unk_kp}] = {v:2d} ({LAT[v]:3s}) → '{eng}'")
            key_constraints[unk_kp].append((v, eng, wi))

# Cross-reference constraints
print(f"\n{'='*70}")
print("KEY POSITION CONSTRAINTS FROM 1-UNKNOWN WORDS:")
print(f"{'='*70}")

for kp in sorted(key_constraints.keys()):
    constraints = key_constraints[kp]
    print(f"\n  key[{kp}]:")
    
    # Count how many words each value satisfies
    value_counts = Counter()
    for v, eng, wi in constraints:
        value_counts[v] += 1
    
    for v, eng, wi in constraints:
        count = value_counts[v]
        print(f"    = {v:2d} ({LAT[v]:3s}) → Word {wi} = '{eng}'  (this value satisfies {count} word(s))")
    
    # Best values
    if value_counts:
        best_v, best_count = value_counts.most_common(1)[0]
        print(f"    ** BEST: key[{kp}] = {best_v} ({LAT[best_v]}) satisfies {best_count} word(s)")

# Now do 2-unknown words
print(f"\n{'='*70}")
print("WORDS WITH 2 UNKNOWNS: EXHAUSTIVE SEARCH")
print(f"{'='*70}")

for wi, wpos in enumerate(words):
    unk_keys = set()
    for pos in wpos:
        kp = pos % KLEN
        if kp in unknown_set:
            unk_keys.add(kp)
    
    if len(unk_keys) != 2:
        continue
    
    unk_list = sorted(unk_keys)
    wlen = len(wpos)
    
    candidates = []
    for v0 in range(MOD):
        for v1 in range(MOD):
            word_gp = []
            for pi, pos in enumerate(wpos):
                kp = pos % KLEN
                if kp == unk_list[0]:
                    word_gp.append((cipher[pos] - v0) % MOD)
                elif kp == unk_list[1]:
                    word_gp.append((cipher[pos] - v1) % MOD)
                else:
                    word_gp.append(dec_hc[pos])
            word_tuple = tuple(word_gp)
            if word_tuple in word_text:
                candidates.append((v0, v1, word_text[word_tuple]))
    
    if candidates:
        word_lat = ''.join(LAT[dec_hc[i]] for i in wpos)
        print(f"\n  Word {wi:3d} ({word_lat}), unknown keys [{unk_list[0]}, {unk_list[1]}]:")
        for v0, v1, eng in candidates[:30]:  # Limit output
            print(f"    key[{unk_list[0]}]={v0:2d}({LAT[v0]:3s}), key[{unk_list[1]}]={v1:2d}({LAT[v1]:3s}) → '{eng}'")
        if len(candidates) > 30:
            print(f"    ... and {len(candidates)-30} more")

# Summary
print(f"\n{'='*70}")
print("SUMMARY: Constrained key positions from word matching")
print(f"{'='*70}")
for kp in sorted(unknown_set):
    if kp in key_constraints:
        constraints = key_constraints[kp]
        values = set(v for v, _, _ in constraints)
        words_str = "; ".join(f"'{eng}'(={v})" for v, eng, wi in constraints)
        print(f"  key[{kp:2d}]: possible = {sorted(values)} from {words_str}")
    else:
        print(f"  key[{kp:2d}]: no 1-unknown word constraints")
