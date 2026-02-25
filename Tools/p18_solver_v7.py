"""
P18 SOLVER v7 - Component-wise exhaustive search
The 22 undetermined buckets form 3 INDEPENDENT components:
  B:   {23, 24, 25}              (3 buckets - brute-force 29^3)
  C+D: {30, 31, 32, 33, 34, 35, 36, 37}  (8 buckets - constrained search)
  A+E+F: {0, 1, 7, 8, 9, 10, 11, 12, 45, 49, 52} (11 buckets - constrained search)
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
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

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
    """All possible GP rune sequences for an English word."""
    word = word.upper()
    results = []
    def recurse(pos, acc):
        if pos >= len(word):
            results.append(tuple(acc))
            return
        if pos + 1 < len(word):
            digraph = word[pos:pos+2]
            if digraph in DIGRAPHS:
                recurse(pos + 2, acc + [DIGRAPHS[digraph]])
        ch = word[pos]
        if ch in ENG2GP:
            recurse(pos + 1, acc + [ENG2GP[ch]])
    recurse(0, [])
    return results

# MUCH larger word list
import urllib.request, io
try:
    # Try to get a large word list
    with open('Tools/english_words.txt', 'r') as f:
        big_words = set(w.strip().upper() for w in f if len(w.strip()) >= 1)
    print(f"Loaded {len(big_words)} words from file")
except FileNotFoundError:
    big_words = set()

# Comprehensive word list
_words_raw = """
a about above across after again against ago ahead air all almost along already
also always am among an and another any anyone anything anyway are around as at
away back bad base be beautiful because become been before began begin behind
being believe below beneath beside best better between beyond big black blood
body bone book born both bottom break breath bright bring brother build burn
but buy by call came can care carry cause certain change child children choose
church city class clean clear close cold come common complete concern consider
contain continue cool could country course cover cross cry current cut
dark daughter day dead deal dear death decide deep defeat depend describe
desire destroy determine develop did die different difficult dinner direction
discover distance divine do does dog done door doubt down draw dream drink
drive drop dry during
each ear early earth ease east eat edge effect effort eight either else
empty end enemy enough enter escape even evening ever every everyone everything
evil exact example except exchange exist expect experience explain express
extend extreme eye
face fact fail faith fall false familiar family famous far fast fate father
favor fear feed feel fellow few field fight fill final find fine finger finish
fire first fish five floor fly follow food fool foot for force foreign forest
forget form former forward found four free freedom fresh friend from front
fruit full further future
gain garden gate gather general generation gentle gift give glad glass glory go
god gold gone good got govern grace grain grand grass great green grew ground
group grow growth guard guess guide
habit hair half hall hand hang happen happy hard harm has hat hate have he head
health hear heart heat heaven heavy height held help her here herself hide
high hill him himself his history hit hold hole holy home honest honor hope
horse host hot hour house how however human hundred hunger hunt hurry husband
i if imagine important in include increase indeed influence inside instead
interest into iron island it its itself
join joy judge just justice
keep key kill kind king kitchen knew knock know knowledge
labor lack land language large last late laugh law lay lead learn least leave
left less let lie life light like line list listen little live long look
lord lose lost lot love low
machine made main make man many mark master matter may me mean measure meet
member men might mind miss moment money month moon more morning most mother
mount mountain mouth move much music must my myself mystery
name narrow nation nature near necessary need never new next night nine no
noble noise none nor north nose not nothing notice now number
of off offer office often oh old on once one only open or order other our out
outside over own
page pair part pass past path pay people period person pick piece place plain
plan plant play please point poor position possible power prayer present press
private prize probable problem produce product program promise proper protect
provide public pull purpose push put
question quick quiet quite
race rain raise ran rather reach read ready real reason receive red remain
remember reply report rest result return rich ride right ring rise river road
rock room round rule run
sacred said same sat save saw say sea season seat second secret see seek
seem self send sense serve set settle seven several shadow shall shape share
she ship short should show shut side sight sign silence silver simple since
sing sister sit six size sleep small smell smile so soft some son song soon
sort soul sound south speak special spend spirit spring square stage stand
star start state stay step still stone stood stop story strange street
strength strike strong student subject such sudden suffer suggest summer sun
supply sure surprise sweet system
table tail take talk tall tell ten tend test than that the their them
themselves then there therefore these they thin thing think third this
those though thought thousand three through throw thus tie till time to
today together told tomorrow tonight too took top touch toward town trade
tree trouble true trust truth try turn twelve two type
uncle under understand unit united until up upon us use usual
valley value very voice
wait wake walk wall want war warm was watch water way we weather week well
went were west what when where whether which while white who whole whom why
wide wife wild will win wind window winter wise wish with within without
woman wonder wood word work world would write wrong
year yes yet you young your yourself youth

able accept account achieve across act action active add address age agree
alive allow alone amount ancient anger angle animal answer apart appear
approach arm army arrange art attempt attention authority avoid
balance band bar battle bear beat beauty bed bell belong besides beyond
birth bite blame blank bless blind block blow board boat bold bone border
born borrow bottom box branch brave break bridge broad broken brown burn
burst bury
camp captain card cat cattle cause chain chair chance chief circle claim
climb clock coal coat collect column combine comfort command common
communicate compare complaint concentrate condition confess connect
conscious consider control convenient cool copy correct count couple
courage create creature crowd crush cure curious cushion custom cycle
damage dare deaf debt decay decide delay deliver demand depart
depend depth deserve detail develop device direct disappoint discover
discuss display distant divide doubt dozen draw dress dust duty
eager earn educate elder elect employ encourage engine equal especially
establish event evil examine exchange excuse exercise expand experience
express
fair fame fault feather female fetch fever firm flag flame flat float floor
fold follow forbid forgive form found frame freeze frequent fresh fruit fuel
furniture
garden gentle gift glory goat govern grass gray greed grieve growth guard
guilt
handle happiness harm harvest hate heal height hesitate hire hollow honest
honor horror humble hurry husband
ideal ignorance ill imagine immediate impress income increase independent
industry influence inquire inspect instant instrument intend introduce invent
invite island issue
jewel join journey judge juice jump junior
keen kill knee knife knock
label lack lamp large late lay leaf lean left length lesson liberty lift
limit line lip liquid loan local lone lord loose loud lover loyal luck
major manage manner march mass match meal mental mercy metal middle
military mistake modern moral motion mount mystery
nation native neat neighbor net noble nor normal notice noun nurse
obey observe occasion occur odd offer oil opinion oppose origin owner
pack paint patience pattern pause peculiar personal physical pile pitch
plain pleasure poem poison polish pool popular portion possess pour
pour praise prefer prepare president pride private prompt protect prove
pure purple
quality queen question

abroad abuse actual admit adult ahead alarm allow ancient approach artificial
ashamed associate attempt attend authority avenue
backward barely barrel behave beside bless boast bone boundary breath brief
brilliant bury
cabin calculate calm capable capture celebrate ceremony chapter chase chart
chief chimney claim clever coach collapse collect comfort commit companion
compete conduct confuse congress consist construct contain contrast convince
core council craft creature criminal crop current curve
dare decline defeat define delight demand deny department deposit deputy design
detect devote differ dismiss display divide domestic doubt draft dust
effort elaborate elder embrace emerge emotion employ endure engage enormous
entrance establish evaluate evidence examine exceed exclude exercise exist
expand explode explore expose extend external extreme
factor famous fatal fiber fierce finance firm flash fold foreign formal
fortune foundation frame frequent frontier furnish
gallery generous genuine glory govern gradual grant graphic grave grocery grip
guilty
harbor harsh headline heritage hesitate highlight honor horror humble
identical ignore illegal illustrate impact imply impose income incredible
indicate individual infant inform initial inner innocent insect insert
inspect instance institute intellectual intend interior interpret invasion
involve isolate
journal junior justice
kingdom

above another because before between children complete consider could different
difficult discover during enough everything experience following himself
hundred important interest itself knowledge language morning mountain number
people perhaps picture possible question remember several something sometimes
themselves therefore through together understand without

shall spirit power blood truth wisdom knowledge light dark
deep fire water earth air beauty death life void nothing
ever never always once silence word voice seek find
hidden reveal sacred profane divine mortal eternal temporal
infinite finite cipher secret mystery shadow
consciousness awareness perception reality illusion
creation destruction existence
ancient primal raw pure whole part
pilgrim master teacher
transform become unfold within beneath upon
consume devour thirst hunger feast
primal bestow behold forsake endure perceive conceive
sacrifice offering blessing curse prayer chant ritual AMONGST
fellowship brethren pilgrimage doctrine prophecy judgement
worship temple altar vessel angel daemon ghost
together alone single between amongst toward unto thee thou
thine whilst betwixt whence herein thereof therein

liar least learn listen lost lord leave level maybe might nature noble
notice ocean order outer paper peace person place please point power
prayer pride prince queen rather reach reason river royal saint
scene sense serve shape share short sight since single sleep small
smell spend stand steal storm strong sweet taste teach teeth throw
touch trade visit voice waste watch whole woman world worth write

beneath between beyond beside before behind below above aside along
after against among around about across apart ahead among

hath doth unto thine thee thou shalt thy wilt hast canst shall
wouldst shouldst couldst mayest mightest
"""

for line in _words_raw.split('\n'):
    for w in line.split():
        w = w.strip().upper()
        if len(w) >= 1:
            big_words.add(w)

WORDLIST = big_words
print(f"Total dictionary: {len(WORDLIST)} words")

# Pre-compute GP encodings by rune count
gp_by_runelen = defaultdict(list)
for w in WORDLIST:
    for enc in english_to_gp_all(w):
        gp_by_runelen[len(enc)].append((w, enc))

cipher, words = load_page(18)
N = len(cipher)
print(f"P18: {N} runes, {len(words)} words")

confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}

# Components
COMP_B = [23, 24, 25]
COMP_CD = [30, 31, 32, 33, 34, 35, 36, 37]
COMP_AEF = [0, 1, 7, 8, 9, 10, 11, 12, 45, 49, 52]

def decrypt_with_key(k):
    return [(cipher[i] - k[i % KLEN]) % MOD for i in range(N)]

def word_text(dec, wi):
    start, wrunes = words[wi]
    vals = dec[start:start+len(wrunes)]
    return ''.join(LAT[v] for v in vals)

def count_words(k):
    dec = decrypt_with_key(k)
    count = 0
    matched = []
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST:
            count += 1
            matched.append((wi, txt))
    return count, matched

def score_text(k):
    """Score combining word matches + frequency correlation + bigram."""
    dec = decrypt_with_key(k)
    
    eng_gp_freq = [0.022, 0.038, 0.035, 0.075, 0.060, 0.036, 0.020, 0.024,
                   0.061, 0.067, 0.070, 0.002, 0.005, 0.019, 0.002, 0.063,
                   0.056, 0.015, 0.127, 0.024, 0.040, 0.015, 0.003, 0.043,
                   0.082, 0.003, 0.020, 0.003, 0.003]
    tot = sum(eng_gp_freq)
    eng_gp_freq = [f/tot for f in eng_gp_freq]
    
    # Word score
    wscore = 0
    for wi, (start, wrunes) in enumerate(words):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST:
            wscore += len(wrunes) * 10  # Weight by word length
    
    # Mono score
    counts = Counter(dec)
    mono = sum(counts.get(i,0)/N * eng_gp_freq[i] for i in range(MOD)) * 1000
    
    # Bigram score
    common_bg = {(2,18):5,(8,18):4,(10,9):3,(18,4):3,(24,9):3,(4,18):3,(3,9):2.5,
                 (24,16):2.5,(18,9):2.5,(9,23):2.5,(16,10):2.5,(18,15):2.5,(3,4):2.5,
                 (16,18):2.5,(3,0):2.5,(18,23):2.5,(10,15):2.5,(10,16):2.5,(24,20):2.5,
                 (24,4):2.5,(15,16):2.5,(9,18):2.5,(2,24):2.5,(2,10):2.5}
    bg = sum(common_bg.get((dec[i],dec[i+1]),0) for i in range(N-1))
    
    return wscore + mono + bg

# Build base key
base_key = [0] * KLEN
for b, v in confirmed.items():
    base_key[b] = v

print(f"\n{'='*80}")
print(f"COMPONENT B: buckets {COMP_B} - Exhaustive search (29^3 = {29**3})")
print(f"{'='*80}")

# Words that depend on Component B
comp_b_words = []
for wi, (start, wrunes) in enumerate(words):
    buckets = [(start+j)%KLEN for j in range(len(wrunes))]
    if any(b in COMP_B for b in buckets):
        undet = [b for b in buckets if b not in confirmed]
        if any(b in COMP_B for b in undet):
            comp_b_words.append(wi)
print(f"Words depending on B: {comp_b_words}")

best_b = None
best_b_score = -1
best_b_words = 0

for v23, v24, v25 in product(range(MOD), repeat=3):
    k = list(base_key)
    k[23] = v23; k[24] = v24; k[25] = v25
    
    # Only check B-dependent words for speed
    wcount = 0
    for wi in comp_b_words:
        start, wrunes = words[wi]
        vals = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST:
            wcount += 1
    
    if wcount > best_b_words:
        best_b_words = wcount
        best_b = (v23, v24, v25)
        # Show details
        matched_b = []
        for wi in comp_b_words:
            start, wrunes = words[wi]
            vals = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
            txt = ''.join(LAT[v] for v in vals).upper()
            if txt in WORDLIST:
                matched_b.append(f"w{wi}='{txt}'")
        print(f"  B=({v23},{v24},{v25}) -> {wcount} words: {matched_b}")

print(f"\nBest B: {best_b} with {best_b_words} B-words")

# Apply best B
base_key[23] = best_b[0]
base_key[24] = best_b[1]
base_key[25] = best_b[2]

# Also show ALL solutions with best_b_words matches for B
print(f"\nAll B solutions with {best_b_words} matches:")
for v23, v24, v25 in product(range(MOD), repeat=3):
    k = list(base_key)
    k[23] = v23; k[24] = v24; k[25] = v25
    wcount = 0
    mlist = []
    for wi in comp_b_words:
        start, wrunes = words[wi]
        vals = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
        txt = ''.join(LAT[v] for v in vals).upper()
        if txt in WORDLIST:
            wcount += 1
            mlist.append(f"w{wi}='{txt}'")
    if wcount >= best_b_words:
        print(f"  ({v23},{v24},{v25}): {mlist}")

print(f"\n{'='*80}")
print(f"COMPONENT C+D: buckets {COMP_CD} - Constrained search")
print(f"{'='*80}")

comp_cd_words = []
for wi, (start, wrunes) in enumerate(words):
    buckets = [(start+j)%KLEN for j in range(len(wrunes))]
    undet = [b for b in buckets if b not in confirmed and b not in COMP_B]
    if any(b in COMP_CD for b in undet):
        comp_cd_words.append(wi)
print(f"Words depending on C+D: {comp_cd_words}")

# w50 has only 2 candidates for buckets {33,34,35,36,37}
# Try each w50 candidate, then brute-force remaining {30,31,32}
w50_candidates = [
    ('PUBLIC', {33: 28, 34: 21, 35: 1, 36: 1, 37: 24}),
    ('ATTACK', {33: 17, 34: 6, 35: 2, 36: 26, 37: 0}),
]

best_cd = None
best_cd_score = -1
best_cd_words = 0

for w50_name, w50_kreq in w50_candidates:
    print(f"\n  Testing w50='{w50_name}'...")
    for v30, v31, v32 in product(range(MOD), repeat=3):
        k = list(base_key)
        k[30] = v30; k[31] = v31; k[32] = v32
        for b, v in w50_kreq.items():
            k[b] = v
        
        wcount = 0
        mlist = []
        for wi in comp_cd_words:
            start, wrunes = words[wi]
            vals = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
            txt = ''.join(LAT[v] for v in vals).upper()
            if txt in WORDLIST:
                wcount += 1
                mlist.append(f"w{wi}='{txt}'")
        
        if wcount > best_cd_words:
            best_cd_words = wcount
            best_cd = (v30, v31, v32, w50_name, w50_kreq)
            print(f"    ({v30},{v31},{v32}) -> {wcount} words: {mlist}")

print(f"\nBest C+D: {best_cd[:3]} with w50='{best_cd[3]}', {best_cd_words} words")

# Apply best C+D to base_key
base_key[30] = best_cd[0]
base_key[31] = best_cd[1]
base_key[32] = best_cd[2]
for b, v in best_cd[4].items():
    base_key[b] = v

# Also: brute-force all 8 buckets without w50 constraint (29^3 for {30,31,32} with BOTH w50 choices)
# Show ALL top solutions with same word count
print(f"\nAll C+D solutions with {best_cd_words} matches:")
for w50_name, w50_kreq in w50_candidates:
    for v30, v31, v32 in product(range(MOD), repeat=3):
        k = list(base_key)
        k[30] = v30; k[31] = v31; k[32] = v32
        for b, v in w50_kreq.items():
            k[b] = v
        wcount = 0
        mlist = []
        for wi in comp_cd_words:
            start, wrunes = words[wi]
            vals = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
            txt = ''.join(LAT[v] for v in vals).upper()
            if txt in WORDLIST:
                wcount += 1
                mlist.append(f"w{wi}='{txt}'")
        if wcount >= best_cd_words:
            print(f"  w50={w50_name} ({v30},{v31},{v32}): {mlist}")

print(f"\n{'='*80}")
print(f"COMPONENT A+E+F: buckets {COMP_AEF} - Staged search")
print(f"{'='*80}")

comp_aef_words = []
for wi, (start, wrunes) in enumerate(words):
    buckets = [(start+j)%KLEN for j in range(len(wrunes))]
    undet = [b for b in buckets if b not in confirmed and b not in COMP_B and b not in COMP_CD]
    if any(b in COMP_AEF for b in undet):
        comp_aef_words.append(wi)
print(f"Words depending on A+E+F: {comp_aef_words}")

# w15 determines {52, 0, 1} -> 12 candidates from v6
# After w15, w27 shares {52, 0, 1} -> check consistency
# Then w41 uses {1, 7} -> bucket 1 known, determines bucket 7
# After that, {8, 9, 10, 11, 12} remain, and {45, 49}

# Generate w15 candidates
w15_start, w15_runes = words[15]  # w15 at word index 15 but let's verify
# Actually verify: which word index is the 4-rune word at buckets [52, 0, 1, 2]?
w15_cands = []
for eng, gp in gp_by_runelen.get(len(words[15][1]), []):
    start, wrunes = words[15]
    buckets = [(start+j)%KLEN for j in range(len(wrunes))]
    match = True
    kreq = {}
    for j in range(len(wrunes)):
        b = buckets[j]
        if b in confirmed:
            expected = (cipher[start+j] - confirmed[b]) % MOD
            if gp[j] != expected:
                match = False
                break
        else:
            kreq[b] = (cipher[start+j] - gp[j]) % MOD
    if match:
        w15_cands.append((eng, gp, kreq))

print(f"\nw15 candidates ({len(w15_cands)}):")
for eng, gp, kreq in w15_cands:
    print(f"  '{eng}': {kreq}")

# For each w15 candidate, determine {52, 0, 1}
# Then check all remaining words in AEF
best_aef = None
best_aef_words = 0

for w15_eng, w15_gp, w15_kreq in w15_cands:
    # Set buckets from w15
    k = list(base_key)
    for b, v in w15_kreq.items():
        if b in COMP_AEF:
            k[b] = v
    
    # Now brute-force the remaining AEF buckets: {7, 8, 9, 10, 11, 12, 45, 49}
    # That's 8 buckets -> 29^8 is too many. Need staged approach.
    # 
    # Stage 1: w17 uses {4,5,6,7,8} with 7,8 undetermined
    #          Try all 29^2 for (7,8)
    # Stage 2: For each (7,8), w2/w18/w42/w58 use {9,10,11,12} with all undetermined
    #          Try all 29^4 for (9,10,11,12)
    # Stage 3: w13 uses {45,49} -> try all 29^2
    # Total: 29^2 * 29^4 * 29^2 = 29^8 ≈ 2e11 -> TOO MANY!
    #
    # Better: for each (7,8), score the words that only use 7,8.
    # Then for the best (7,8) combos, try (9,10,11,12).
    # Finally try (45,49).
    
    # Actually, let's be smarter. (45, 49) only appear in a few words.
    # Let's use hill-climbing per w15 candidate.
    
    remaining_aef = [b for b in COMP_AEF if b not in w15_kreq]
    
    # Hill-climbing with 50 random restarts per w15 candidate
    local_best_wcount = 0
    local_best_k = None
    
    for restart in range(50):
        kk = list(k)
        for b in remaining_aef:
            kk[b] = random.randint(0, MOD-1)
        
        improved = True
        while improved:
            improved = False
            for b in remaining_aef:
                best_v = kk[b]
                best_wc = 0
                for v in range(MOD):
                    kk[b] = v
                    wc = 0
                    for wi in comp_aef_words:
                        start, wrunes = words[wi]
                        vals = [(cipher[start+j] - kk[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
                        txt = ''.join(LAT[v2] for v2 in vals).upper()
                        if txt in WORDLIST:
                            wc += 1
                    if wc > best_wc:
                        best_wc = wc
                        best_v = v
                kk[b] = best_v
        
        wc = 0
        mlist = []
        for wi in comp_aef_words:
            start, wrunes = words[wi]
            vals = [(cipher[start+j] - kk[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
            txt = ''.join(LAT[v2] for v2 in vals).upper()
            if txt in WORDLIST:
                wc += 1
                mlist.append(f"w{wi}='{txt}'")
        
        if wc > local_best_wcount:
            local_best_wcount = wc
            local_best_k = list(kk)
    
    if local_best_wcount > best_aef_words:
        best_aef_words = local_best_wcount
        best_aef = (w15_eng, local_best_k)
        mlist = []
        for wi in comp_aef_words:
            start, wrunes = words[wi]
            vals = [(cipher[start+j] - local_best_k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
            txt = ''.join(LAT[v2] for v2 in vals).upper()
            if txt in WORDLIST:
                mlist.append(f"w{wi}='{txt}'")
        print(f"  w15='{w15_eng}': {local_best_wcount} AEF-words: {mlist}")
        print(f"    key at remaining AEF: {[(b, local_best_k[b]) for b in remaining_aef]}")

print(f"\nBest A+E+F: w15='{best_aef[0]}' with {best_aef_words} matched words")

# Apply best AEF
final_key = list(best_aef[1])
# Make sure B and CD are applied too (they should be in base_key already)
# Actually, best_aef[1] was initialized from base_key which has B and CD. Good.

print(f"\n{'='*80}")
print(f"FINAL COMBINED RESULT")
print(f"{'='*80}")

k = final_key
wcount, matched = count_words(k)
dec = decrypt_with_key(k)
full_text = ''.join(LAT[v] for v in dec)

print(f"Total words matched: {wcount}/{len(words)}")

# Compute IoC
counts = Counter(dec)
ioc = sum(c*(c-1) for c in counts.values()) / (N*(N-1)) * MOD
print(f"IoC*29: {ioc:.3f}")
print(f"Key: {k}")
print(f"Key (LAT): {''.join(LAT[v] for v in k)}")
print(f"\nFull text:\n{full_text}")
print(f"\nMatched words: {matched}")

print(f"\nWord-by-word:")
matched_set = {wi for wi, _ in matched}
for wi, (start, wrunes) in enumerate(words):
    vals = dec[start:start+len(wrunes)]
    txt = ''.join(LAT[v] for v in vals)
    marker = "Y" if wi in matched_set else " "
    print(f"  {marker} w{wi}: '{txt}'")

# Show unmatched fully-determined words
print(f"\nNon-English fully-determined words:")
for wi, (start, wrunes) in enumerate(words):
    if wi in matched_set:
        continue
    buckets = [(start+j)%KLEN for j in range(len(wrunes))]
    if all(b in confirmed for b in buckets):
        vals = dec[start:start+len(wrunes)]
        txt = ''.join(LAT[v] for v in vals)
        print(f"  w{wi}: '{txt}' (buckets={buckets})")

print(f"\n=== DONE ===")
