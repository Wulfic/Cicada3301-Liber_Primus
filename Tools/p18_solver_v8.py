"""
P18 SOLVER v8 - Staged exhaustive search exploiting word pair constraints
Key insight: w15 determines {52,0,1}, w2 determines {9,10,11,12}, leaving
only {7,8,45,49} for brute-force (29^4 = 707k, fast!)
Also cross-checks w18, w42, w30, w58 against dictionary.
"""
import os, sys, random
from collections import Counter, defaultdict
from itertools import product

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
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

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

def english_to_gp_all(word):
    word = word.upper()
    results = []
    def recurse(pos, acc):
        if pos >= len(word):
            results.append(tuple(acc))
            return
        if pos + 1 < len(word):
            d = word[pos:pos+2]
            if d in DIGRAPHS:
                recurse(pos + 2, acc + [DIGRAPHS[d]])
        if word[pos] in ENG2GP:
            recurse(pos + 1, acc + [ENG2GP[word[pos]]])
    recurse(0, [])
    return results

# Build comprehensive word list
_words = """
a about above across after again against ago ahead air all almost along already
also always am among an and another any anyone anything anyway are around as at
away back bad base be beautiful because become been before began begin behind
being believe below beneath beside best better between beyond big birth black
blood blue body bone book born both bottom boy break breath bridge bright bring
brother build burn busy but buy by call came can captain care carry catch cause
center certain chain chance change chief child children choose church circle
city class clean clear climb close coal coat cold come common complete concern
condition connect consider contain continue control cool corner could count
country couple courage course cover create cross crowd cry cup current custom
cut damage dance danger dare dark daughter day dead deal dear death decide deep
defeat demand depend describe desire destroy determine develop die difference
different difficult dinner direction discover display distance divide divine do
does dog done door doubt down draw dream drink drive drop dry during dust duty
each ear early earth ease east eat edge effect effort eight either elder else
empty end enemy enough enter escape even evening ever every everyone everything
evil exact example except exchange excite exist expect experience explain express
extend extreme eye face fact fail fair faith fall false familiar family famous
far fast fate father favor fear feast feed feel fellow few field fight fill
final find fine finger finish fire firm first fish fit five fix flat flee flesh
float floor flow flower fly follow food fool foot for force foreign forest
forever forget form former fortune forward found four free freedom fresh friend
from front fruit full further future gain garden gate gather general generation
gentle gift give glad glass glory go god gold gone good got govern grace grain
grand grass grave great green grew ground group grow growth guard guess guide
habit hair half hall hand hang happen happy hard harm has hat hate have he head
health hear heart heat heaven heavy height held help her here herself hidden
hide high hill him himself his history hit hold hole holy home honest honor hope
horse host hot hour house how however human hundred hunger hunt hurry husband
i if ill imagine important in include increase indeed influence inside instead
interest into iron island it its itself join joy judge just justice keen keep
key kill kind king kitchen knew knock know knowledge labor lack land language
large last late laugh law lay lead learn least leave left length less let liar
lie life light like line list listen little live long look lord lose lost lot
love low machine made main maintain make man many march mark master match matter
may me mean measure meet member men metal middle might mind mine miss moment
money month moon more morning most mother mount mountain mouth move much music
must my myself mystery name narrow nation nature near necessary need never new
next night nine no noble noise none nor north nose not nothing notice now number
obey observe ocean offer office often oh old on once one only open or order
other otherwise our out outside over own page pain pair part particular pass
past path pay peace people perhaps period person pick piece place plain plan
plant play please point poor position possible pour power prayer present press
pretty prince private prize probable problem produce product program promise
proper protect prove provide public pull purpose push put quarter queen
question quick quiet quite race rain raise ran rather reach read ready real
reason receive red remain remember reply report rest result return rich ride
right ring rise river road rock roll room round royal rule run sacred safe
said saint same sat save saw say scene sea season seat second secret see seek
seem self send sense separate serve set settle seven several shadow shall shape
share she ship short should show shut side sight sign silence silver simple
since sing single sir sister sit six size sleep small smell smile so soft
soldier some son song soon sort soul sound south speak special spend spirit
spring square stage stand star start state stay steal step still stone stood
stop storm strange street strength strike strong student subject such sudden
suffer suggest summer sun supply sure surprise sweet system table tail take talk
tall taste teach tell ten tend test than that the their them themselves then
there therefore these they thin thing think third this those though thought
thousand three through throw thus tie till time to today together told tomorrow
tonight too took top touch toward town trade tree trouble true trust truth try
turn twelve twenty two type uncle under understand unit united until up upon us
use usual valley value various very visit voice wait wake walk wall want war
warm was watch water way we weak wealth weather week welcome well went were west
what whatever when where whether which while white who whole whom whose why wide
wife wild will win wind window winter wise wish with within without woman wonder
wood word work world worth would write wrong wrote year yes yet you young your
yourself youth
able accept accomplish achieve acquire action active admit advance advice affair
affirm afraid agree allow alone already although always ancient announce appear
approach arrange arrive assist attempt attend authority avoid awake aware balance
battle beauty begin behave belief belong beneath benefit bind bitter blame bless
blind blow board bold border bother bound branch brave breath bride bright broad
broken burden calm capable capture careful cattle celebrate chain chamber
chapter charge cheap chief chimney claim class clever coach collapse collect
comfort command commit companion compare complaint compose concern conduct
confess confirm confuse connect conscious constant consume contain contest
continue contrast convince core correct council couple courage craft creature
criminal cross crowd cruel culture cure curious current curse custom cycle
daily damage dare declare decline defeat define delay deliberate deliver demand
deny depart deposit derive deserve design desire detail determine develop devote
differ dignity direct disappear discipline discover discuss dismiss display
distant distinct district disturb divide document domestic doubt draft drag
dress dust duty eager earn ease educate effort elaborate element embrace emerge
emotion employ empty enable encounter encourage endure engage enjoy enormous
enter entire entrance equal error escape especially establish estimate evaluate
even event evidence evil exact examine exceed excellent except exchange execute
exercise exhaust exhibit exist expand expect expense experience experiment
explain explore export expose extend extent extra extreme fabric factor
failure fair familiar fancy fashion fatal feature female fever fiber fierce
finance firm fit fix flame flash flat float flock fold forbid forge formal
former formula forth fortune foundation frame frequent frontier fruit fuel
function fund further gallery gather generous genius genuine giant glory govern
gradual grain grant grave grocery grip guarantee guard guide guilty
handle harvest hasty heal height heritage hesitate highlight hollow honor horror
humble hurry ideal identify ignorance illegal illustrate image imagine
immediate impact important impose impress improve include income increase
incredible indeed indicate individual infant inform initial injury inner
innocent insect insert insight inspect inspire institute instrument intend
interior interpret introduce invasion invest involve island issue ivory
journal journey joy judge juice junior keen key kingdom labor lane launch layer
leaf league leather legend lemon level liberal liberty limit list lively loan
local loose loss loyal luck luxury main major manage manner manufacture margin
mass massive material mayor measure medal memory mental mercy merely method
middle military minimum minor miracle mirror mission mistake mixture model
modern modest moral mount murder mutual native neglect nerve noble normal
notion nuclear object obtain obvious occasion offense operate opinion oppose
oppose origin outcome overcome owe pace panic pardon passage passion patience
pattern pause penalty perceive permit personal phrase physical pilot plain
platform pleasure plenty poem policy polite popular possess potential poverty
prayer precise predict prefer prepare pretend prevent principle priority prison
procedure profession profit prompt proof propose protest proud provision pursue
qualify quantity quest quote rapid reaction realize recover reflect reform
refuse regard region regret reject relate release relief rely remark remedy
remote remove repair repeat replace request require research reserve resident
resist resolve resource respect respond restore result retain retire reveal
reverse revolt reward rhythm ritual rival rough routine sacred sacrifice saint
sake sample satisfaction scale scatter scheme scholar scope scream seal section
secure seize selection sensitive sequence session settle severe shadow shallow
shelter shift shock signal silence silly sincere site sketch slave slip slope
smooth soldier solution somehow somewhat source spare stable staff standard
steady steel steep stem stiff stock strain stray stretch strip stroke struggle
studio style submit substance succeed sufficient sum surface survive suspect
sustain swing symbol sympathy talent target temple tend terms territory theme
till title topic total tough tradition transfer transform treasure
trend tribe trick triumph troop trust tube vast venture version victim virtue
visible vision vital volume volunteer voyage wage wander warn waste wealth weapon
weave weed welcome welfare wheat whisper wicked widespread willing witness
witness worthy wound wrap yield zone
defeat destroy divine eternal flame fragment gather grace hollow honor hunger
imagine infinite inspire journey liberty master mortal noble perceive pilgrim
primal profound pure reveal sacred secret shadow solemn spirit strength temple
truth vessel wisdom wonder
hath doth unto thine thee thou shalt thy wilt hast canst shall
wouldst shouldst couldst mayest mightest whilst betwixt whence herein thereof
amongst toward forward backward inward outward onward upward downward
liar length third public learn
""".strip()

WORDLIST = set()
for line in _words.split('\n'):
    for w in line.split():
        WORDLIST.add(w.strip().upper())

print(f"Dictionary: {len(WORDLIST)} words")

# Pre-compute GP encodings
gp_by_runelen = defaultdict(list)
gp_set_by_runelen = defaultdict(set)  # for fast lookup: runelen -> set of tuples
for w in WORDLIST:
    for enc in english_to_gp_all(w):
        gp_by_runelen[len(enc)].append((w, enc))
        gp_set_by_runelen[len(enc)].add(enc)

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

# Confirmed key values
confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

# Component B: SOLVED
confirmed[23] = 2
confirmed[24] = 5
confirmed[25] = 5

# Build base key
base_key = [0] * KLEN
for b, v in confirmed.items():
    base_key[b] = v

# Pre-compute cipher values at each word position
word_ciphers = {}
for wi, (start, wrunes) in enumerate(words):
    word_ciphers[wi] = [cipher[start + j] for j in range(len(wrunes))]

def get_word_buckets(wi):
    start, wrunes = words[wi]
    return [(start + j) % KLEN for j in range(len(wrunes))]

def decrypt_word(wi, k):
    """Decrypt word wi with key k, return GP values."""
    start, wrunes = words[wi]
    return [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]

def word_to_text(gp_vals):
    return ''.join(LAT[v] for v in gp_vals)

def is_english(gp_vals):
    txt = ''.join(LAT[v] for v in gp_vals).upper()
    return txt in WORDLIST

def count_all_words(k):
    count = 0
    matched = []
    for wi in range(len(words)):
        vals = decrypt_word(wi, k)
        txt = word_to_text(vals).upper()
        if txt in WORDLIST:
            count += 1
            matched.append((wi, txt))
    return count, matched

# Get cipher values for key words
# w2 at positions [9,10,11,12] (4 runes)
# w15 at positions [52,0,1,2] (4 runes)
# w18 at positions [9,10,11,12,13] (5 runes) -- shares {9,10,11,12} with w2
# w42 at positions [8,9,10,11,12] (5 runes) -- shares {9,10,11,12} with w2

# Verify word positions
for wi in [2, 15, 18, 42, 30, 58]:
    buckets = get_word_buckets(wi)
    ciph = word_ciphers[wi]
    print(f"  w{wi}: {len(words[wi][1])}r, buckets={buckets}, cipher={ciph}")

print(f"\n{'='*80}")
print(f"Phase 1: Find compatible (w15, w2) pairs where w18 is also English")
print(f"{'='*80}")

# Generate w15 candidates (determines {52, 0, 1})
w15_buckets = get_word_buckets(15)
w15_cipher = word_ciphers[15]
w15_cands = []
for eng, gp in gp_by_runelen.get(len(words[15][1]), []):
    match = True
    kreq = {}
    for j in range(len(gp)):
        b = w15_buckets[j]
        if b in confirmed:
            expected = (w15_cipher[j] - confirmed[b]) % MOD
            if gp[j] != expected:
                match = False
                break
        else:
            kreq[b] = (w15_cipher[j] - gp[j]) % MOD
    if match:
        w15_cands.append((eng, gp, kreq))
print(f"w15 candidates: {len(w15_cands)}")
for eng, gp, kreq in w15_cands:
    print(f"  '{eng}': {kreq}")

# Generate w2 candidates (determines {9, 10, 11, 12})
w2_buckets = get_word_buckets(2)
w2_cipher = word_ciphers[2]
w2_cands = []
for eng, gp in gp_by_runelen.get(len(words[2][1]), []):
    kreq = {}
    for j in range(len(gp)):
        b = w2_buckets[j]
        kreq[b] = (w2_cipher[j] - gp[j]) % MOD
    w2_cands.append((eng, gp, kreq))
print(f"\nw2 candidates: {len(w2_cands)}")

# For EACH (w15, w2) pair, check if w18 is also English
# w18 at buckets [9,10,11,12,13]: 13 is confirmed=18, so 9-12 from w2
w18_buckets = get_word_buckets(18)
w18_cipher = word_ciphers[18]
w18_len = len(words[18][1])

# Also check w42 at buckets [8,9,10,11,12]: 9-12 from w2, 8 free
w42_buckets = get_word_buckets(42)
w42_cipher = word_ciphers[42]
w42_len = len(words[42][1])

good_pairs = []

for w15_eng, w15_gp, w15_kreq in w15_cands:
    for w2_eng, w2_gp, w2_kreq in w2_cands:
        # Build temporary key
        k = list(base_key)
        for b, v in w15_kreq.items():
            k[b] = v
        for b, v in w2_kreq.items():
            k[b] = v
        
        # Check w18
        w18_vals = decrypt_word(18, k)
        w18_english = is_english(w18_vals)
        w18_text = word_to_text(w18_vals)
        
        # Check w42 (still has bucket 8 free, try all 29)
        w42_english = False
        w42_text = ""
        w42_best_k8 = None
        for k8 in range(MOD):
            k[8] = k8
            v42 = decrypt_word(42, k)
            if is_english(v42):
                w42_english = True
                w42_text = word_to_text(v42)
                w42_best_k8 = k8
                break
        
        if w18_english or w42_english:
            score = int(w18_english) + int(w42_english)
            good_pairs.append((w15_eng, w2_eng, w18_text, w42_text, w42_best_k8, score,
                              dict(w15_kreq), dict(w2_kreq)))
            print(f"  w15='{w15_eng}' w2='{w2_eng}' -> w18='{w18_text}'{' MATCH!' if w18_english else ''}"
                  f"  w42='{w42_text}'{' MATCH!' if w42_english else ''}")

print(f"\n{len(good_pairs)} compatible pairs found")

# Sort by score (pairs where both w18 and w42 match first)
good_pairs.sort(key=lambda x: -x[5])

print(f"\n{'='*80}")
print(f"Phase 2: For top pairs, brute-force remaining buckets")
print(f"{'='*80}")

# After w15 determines {52,0,1} and w2 determines {9,10,11,12},
# remaining AEF = {7, 8, 45, 49}
# Also Component C+D = {30,31,32,33,34,35,36,37}

# For C+D, try the 4 alternatives from v7
cd_options = [
    ('SO/ILL/PUBLIC', {30:12, 31:18, 32:26, 33:28, 34:21, 35:1, 36:1, 37:24}),
    ('SEA/ITS/PUBLIC', {30:12, 31:22, 32:2, 33:28, 34:21, 35:1, 36:1, 37:24}),
    ('IT/CRY/PUBLIC', {30:17, 31:5, 32:20, 33:28, 34:21, 35:1, 36:1, 37:24}),
    ('EAT/DRY/PUBLIC', {30:28, 31:5, 32:20, 33:28, 34:21, 35:1, 36:1, 37:24}),
]

overall_best_count = 0
overall_best_key = None
overall_best_info = ""

for pair_idx, (w15e, w2e, w18t, w42t, k8_42, score, w15k, w2k) in enumerate(good_pairs[:50]):
    for cd_name, cd_keys in cd_options:
        # Build key with all constraints
        k = list(base_key)
        for b, v in w15k.items(): k[b] = v
        for b, v in w2k.items(): k[b] = v
        for b, v in cd_keys.items(): k[b] = v
        
        # Remaining: {7, 8, 45, 49}
        best_count = 0
        best_remaining = None
        
        for v7, v8, v45, v49 in product(range(MOD), repeat=4):
            k[7] = v7; k[8] = v8; k[45] = v45; k[49] = v49
            
            # Quick count - only check words with undetermined buckets
            count = 0
            for wi in range(len(words)):
                vals = decrypt_word(wi, k)
                txt = word_to_text(vals).upper()
                if txt in WORDLIST:
                    count += 1
            
            if count > best_count:
                best_count = count
                best_remaining = (v7, v8, v45, v49)
        
        if best_count > overall_best_count:
            overall_best_count = best_count
            k[7], k[8], k[45], k[49] = best_remaining
            overall_best_key = list(k)
            overall_best_info = f"w15='{w15e}' w2='{w2e}' cd='{cd_name}' rest={best_remaining}"
            
            # Show details
            _, matched = count_all_words(k)
            print(f"\n  NEW BEST: {best_count}/68 words")
            print(f"    {overall_best_info}")
            print(f"    Matched: {[(wi, txt) for wi, txt in matched]}")
    
    # Progress
    if pair_idx % 10 == 0 and pair_idx > 0:
        print(f"  ... processed {pair_idx}/{min(50, len(good_pairs))} pairs, best={overall_best_count}")

# Also try WITHOUT w2 constraint (let w2 be free via brute force of 7,8,9,10,11,12,45,49)
# This is 29^8 which is too much, but we can do hill-climbing
print(f"\n{'='*80}")
print(f"Phase 3: Hill-climbing refinement")
print(f"{'='*80}")

if overall_best_key:
    k = list(overall_best_key)
else:
    k = list(base_key)

remaining_all = [b for b in range(KLEN) if b not in confirmed]

# Hill-climb on ALL undetermined buckets (not just AEF)
for restart in range(500):
    kk = list(k)
    if restart > 0:
        n_perturb = random.randint(1, len(remaining_all))
        for b in random.sample(remaining_all, n_perturb):
            kk[b] = random.randint(0, MOD-1)
    
    improved = True
    while improved:
        improved = False
        random.shuffle(remaining_all)
        for b in remaining_all:
            best_v = kk[b]
            best_c = 0
            for v in range(MOD):
                kk[b] = v
                c = 0
                for wi in range(len(words)):
                    vals = decrypt_word(wi, kk)
                    txt = word_to_text(vals).upper()
                    if txt in WORDLIST:
                        c += 1
                if c > best_c:
                    best_c = c
                    best_v = v
                elif c == best_c:
                    # Tie-break: prefer value that matches more bigram patterns
                    pass
            if best_v != kk[b]:
                improved = True
            kk[b] = best_v
    
    c, matched = count_all_words(kk)
    if c > overall_best_count:
        overall_best_count = c
        overall_best_key = list(kk)
        print(f"  Restart {restart}: {c}/68 words")
        print(f"    Matched: {[(wi,txt) for wi, txt in matched]}")

print(f"\n{'='*80}")
print(f"FINAL RESULT")
print(f"{'='*80}")

k = overall_best_key if overall_best_key else base_key
c, matched = count_all_words(k)
dec = [(cipher[i] - k[i%KLEN]) % MOD for i in range(N)]
full_text = ''.join(LAT[v] for v in dec)

print(f"Words matched: {c}/{len(words)}")
counts = Counter(dec)
ioc = sum(c2*(c2-1) for c2 in counts.values()) / (N*(N-1)) * MOD
print(f"IoC*29: {ioc:.3f}")
print(f"Key: {k}")
print(f"Key (LAT): {''.join(LAT[v] for v in k)}")
print(f"\nFull text:\n{full_text}")

print(f"\nWord-by-word:")
matched_set = {wi for wi, _ in matched}
for wi, (start, wrunes) in enumerate(words):
    vals = dec[start:start+len(wrunes)]
    txt = word_to_text(vals)
    marker = "Y" if wi in matched_set else " "
    print(f"  {marker} w{wi}: '{txt}'")

print(f"\n=== DONE ===")
