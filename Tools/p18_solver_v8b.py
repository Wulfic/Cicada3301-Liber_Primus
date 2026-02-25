"""
P18 SOLVER v8b - Fast staged search
Uses word pair constraints: w15 determines {52,0,1}, w2 determines {9,10,11,12}
Then hill-climbs remaining {7,8,45,49} for each valid pair.
"""
import os, sys, random
from collections import Counter, defaultdict

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29; KLEN = 53
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,
          'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

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

def eng_to_gp(word):
    word = word.upper(); results = []
    def rec(p, a):
        if p >= len(word): results.append(tuple(a)); return
        if p+1 < len(word):
            d = word[p:p+2]
            if d in DIGRAPHS: rec(p+2, a+[DIGRAPHS[d]])
        if word[p] in ENG2GP: rec(p+1, a+[ENG2GP[word[p]]])
    rec(0, []); return results

# Word list
_w = """a about above across after again against ago all almost along already also
always am among an and another any anyone anything are around as at away back
bad be beautiful because become been before began begin behind being believe
below beneath best better between beyond big birth black blood body bone book
born both bottom breath bright bring brother build burn but by call came can
care carry cause certain chain change child children choose church city class
clean clear climb close cold come common complete concern consider contain control
cool could count country course cover cross crowd cry cup current cut damage
dare dark daughter day dead deal dear death decide deep defeat demand depend
describe desire destroy determine develop die different difficult dinner direction
discover distance divine do does done door doubt down draw dream drink drive
drop dry during duty each ear early earth ease east eat edge effect effort
eight either else empty end enemy enough enter escape even evening ever every
everyone everything evil exact example except exchange exist expect experience
explain express extend extreme eye face fact fail fair faith fall false familiar
family famous far fast fate father favor fear feast feed feel fellow few field
fight fill final find fine finger finish fire firm first fish fit five flesh
float floor flower fly follow food fool foot force foreign forest forever forget
form former forward found four free freedom fresh friend from front fruit full
further future gain garden gate gather general gentle gift give glad glass glory
go god gold gone good govern grace grain grand grass grave great green grew
ground group grow growth guard guess guide guilt habit hair half hall hand hang
happen happy hard harm hat hate have he head health hear heart heat heaven heavy
height held help her here herself hidden hide high hill him himself his history
hit hold hole holy home honest honor hope horse host hot hour house human hundred
hunger hunt hurry husband i if ill imagine important in include increase indeed
influence inside instead interest into iron island it its itself join joy judge
just keen keep key kill kind king kitchen knee knew know knowledge labor lack land
language large last late laugh law lay lead learn least leave left length less let
liar lie life light like line list listen little live long look lord lose lost
lot love low machine main make man many march mark master match matter may me
mean measure meet member men might mind miss moment money month moon more morning
most mother mount mountain mouth move much music must my myself mystery name
narrow nation nature near necessary need never new next night nine no noble none
nor north nose not nothing notice now number obey observe ocean offer office often
oh old on once one only open or order other our out outside over own pain pair
part pass past path pay peace people perhaps period person piece place plan plant
play please point poor position possible power prayer present press prince
private produce program promise proper protect prove provide public pull purpose
push put question quick quiet quite race rain raise ran rather reach read ready
real reason receive remain remember reply report rest result return rich ride right
ring rise river road rock room round royal rule run sacred said saint same sat
save saw say scene sea season second secret see seek seem self send sense serve
set settle seven several shadow shall shape share she short should show shut side
sight sign silence silver simple since sir sit six size sleep small smell so
soft soldier some son song soon sort soul sound south speak special spend spirit
spring square stage stand star start state stay still stone stop storm strange
street strength strike strong student subject such sudden suffer suggest summer
sun supply sure sweet system table take talk taste tell ten test than that the
their them themselves then there these they thin thing think third this those
though thought thousand three through throw till time to today together told
tomorrow too took top touch toward town trade tree trouble true trust truth try
turn twelve two type uncle under understand until up upon us use usual valley
value very visit voice wait wake walk wall want war warm was watch water way we
weak wealth weather week well went were west what when where whether which while
white who whole whose why wide wife wild will win wind window winter wise wish
with within without woman wonder wood word work world worth would write wrong year
yes yet you young your yourself youth
able active admit advance afraid age agree alive alone already always ancient angle
animal answer appear arm army arrange arrive art attempt aware base battle beauty
begin behave belief belong beside bind bitter bless blind blow bold border bound
brain branch brave broad broken build burden calm capable capture careful cause
celebrate chain character chief circle claim clean clever close collect comfort
command commit compare complete compose concern conduct connect conscious consider
constant contain consume continue contest contrast convince correct council couple
courage craft creature crowd cruel cure curious custom cycle dare declare decline
defeat define deliver demand deny depart desert deserve design desire detail
determine develop devote dig direct disappear discover discuss display divide
document domestic doubt drag dress dust duty eager earn ease educate effort
element embrace emerge emotion employ empty encourage endure enemy energy engage
enjoy enormous entire entrance equal error escape establish even evidence evil
exact examine exceed except exchange exist expand explain explore express extend
extreme fact failure fall false fame familiar fashion feature female fewer field
fierce figure finance firm fit flame flat flesh float fold follow fool forbid
fortune forward foundation frame frequent friend frontier fruit fun furnish gain
gather generous gentle giant glory govern gradual grain grant grave growth guard
guide habit harsh heal heavy hero hide history honor horror humble hunt hurt ideal
identify ignorance ill imagine immediate impact impose improve include increase
indicate individual infant inform initial injury inner innocent inspect inspire
instrument intend interior introduce involve issue journey joy judge justice keen
kingdom labor lack lane launch leaf league length letter level liberty lift limit
liar line listener load local loss loyal luxury main major manage manner mass
material matter mayor mental mercy metal method middle military mirror mission
modern moral mount murder mutual native neglect nerve noble normal obey observe
occur ocean offend opinion oppose origin outcome own peace permit person phrase
physical pile pilot plain platform pleasure popular possess potential poverty
precious preserve prevent pride prison product profit project promise proof
proper protect prove provide pure pursue qualify quantity quest quote rapid react
realize recover reflect reform refuse regard region reject release relief rely
remark remedy remote repair repeat replace request require rescue research
reserve resist resolve resource respect respond retire reveal reverse revolt
reward ritual rival rough routine royal sacred sacrifice safe sake sample scale
scatter scheme season secure select separate sequence session settle severe
shadow shallow shelter shift shock sign sincere skip slow solemn solid solution
soul spirit stable staff standard steady steel steep stem stiff stock strain
strange stretch strip struggle style subject submit substance succeed suffer
supply surface survive suspect sustain symbol sympathy talent target temple tend
territory test theme title tone topic total touch tradition transfer transform
treasure trend tribe triumph troop trust truth tube unite vast version victim
virtue vision vital volume wage wander warn waste weapon weave welcome welfare
wide willing witness wound wrap yield zone
hath doth unto thine thee thou shalt thy wilt whilst betwixt amongst toward
behold forsake bestow endure perceive conceive enlighten"""

WORDLIST = set()
for line in _w.split('\n'):
    for w in line.split():
        WORDLIST.add(w.strip().upper())
print(f"Dict: {len(WORDLIST)} words")

gp_by_len = defaultdict(list)
for w in WORDLIST:
    for enc in eng_to_gp(w):
        gp_by_len[len(enc)].append((w, enc))

cipher, words = load_page(18)
N = len(cipher)
nw = len(words)

# Confirmed (including Component B solution)
confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,  # Component B
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24, 50:1, 51:21
}

def get_buckets(wi):
    s, wr = words[wi]
    return [(s+j)%KLEN for j in range(len(wr))]

def decrypt_word(wi, k):
    s, wr = words[wi]
    return [(cipher[s+j] - k[(s+j)%KLEN]) % MOD for j in range(len(wr))]

def word_text(gp): return ''.join(LAT[v] for v in gp)

def count_all(k):
    n = 0; m = []
    for wi in range(nw):
        t = word_text(decrypt_word(wi, k)).upper()
        if t in WORDLIST: n += 1; m.append((wi, t))
    return n, m

# Generate candidates for w15 (4 runes at buckets [52,0,1,2])
w15_cands = []
for eng, gp in gp_by_len.get(len(words[15][1]), []):
    s, wr = words[15]
    ok = True; kreq = {}
    for j in range(len(wr)):
        b = (s+j) % KLEN
        if b in confirmed:
            if (cipher[s+j] - confirmed[b]) % MOD != gp[j]: ok = False; break
        else:
            kreq[b] = (cipher[s+j] - gp[j]) % MOD
    if ok: w15_cands.append((eng, kreq))
print(f"w15 candidates: {len(w15_cands)}")

# Generate candidates for w2 (4 runes at buckets [9,10,11,12])
w2_cands = []
for eng, gp in gp_by_len.get(len(words[2][1]), []):
    s, wr = words[2]
    kreq = {}
    for j in range(len(wr)):
        b = (s+j) % KLEN
        kreq[b] = (cipher[s+j] - gp[j]) % MOD
    w2_cands.append((eng, kreq))
print(f"w2 candidates: {len(w2_cands)}")

# CD options from v7
cd_opts = [
    {30:12, 31:18, 32:26, 33:28, 34:21, 35:1, 36:1, 37:24},  # SO/ILL/PUBLIC
    {30:12, 31:22, 32:2, 33:28, 34:21, 35:1, 36:1, 37:24},   # SEA/ITS/PUBLIC
    {30:17, 31:5, 32:20, 33:28, 34:21, 35:1, 36:1, 37:24},   # IT/CRY/PUBLIC
    {30:28, 31:5, 32:20, 33:28, 34:21, 35:1, 36:1, 37:24},   # EAT/DRY/PUBLIC
]

print(f"\n{'='*80}")
print(f"Phase 1: (w15, w2) pairs with w18 cross-check")
print(f"{'='*80}")

# For each pair, check if result w18 is English
valid_pairs = []
for w15e, w15k in w15_cands:
    for w2e, w2k in w2_cands:
        k = [0]*KLEN
        for b,v in confirmed.items(): k[b]=v
        for b,v in w15k.items(): k[b]=v
        for b,v in w2k.items(): k[b]=v
        
        # w18 uses buckets [9,10,11,12,13] - all now determined
        w18v = decrypt_word(18, k)
        w18t = word_text(w18v).upper()
        
        if w18t in WORDLIST:
            valid_pairs.append((w15e, w2e, w18t, w15k, w2k))
            print(f"  w15='{w15e}' w2='{w2e}' -> w18='{w18t}'")

# Also check pairs where w42 matches (uses [8,9,10,11,12])
print(f"\n  Also checking w42 matches (bucket 8 sweep)...")
extra_pairs = []
for w15e, w15k in w15_cands:
    for w2e, w2k in w2_cands:
        k = [0]*KLEN
        for b,v in confirmed.items(): k[b]=v
        for b,v in w15k.items(): k[b]=v
        for b,v in w2k.items(): k[b]=v
        
        for k8 in range(MOD):
            k[8] = k8
            w42v = decrypt_word(42, k)
            w42t = word_text(w42v).upper()
            if w42t in WORDLIST:
                extra_pairs.append((w15e, w2e, w42t, k8, w15k, w2k))
                print(f"  w15='{w15e}' w2='{w2e}' k8={k8} -> w42='{w42t}'")
                break  # one per pair

print(f"\n{len(valid_pairs)} pairs with w18 match, {len(extra_pairs)} with w42 match")

# Combine all good pairs
all_pairs = []
for w15e, w2e, w18t, w15k, w2k in valid_pairs:
    all_pairs.append((w15e, w2e, 'w18='+w18t, w15k, w2k, None))
for w15e, w2e, w42t, k8, w15k, w2k in extra_pairs:
    all_pairs.append((w15e, w2e, 'w42='+w42t, w15k, w2k, k8))

# Remove duplicates (same w15, w2)
seen = set()
unique_pairs = []
for p in all_pairs:
    key = (p[0], p[1])
    if key not in seen:
        seen.add(key)
        unique_pairs.append(p)

print(f"\n{'='*80}")
print(f"Phase 2: Full evaluation of {len(unique_pairs)} unique pairs × 4 CD options")
print(f"{'='*80}")

overall_best = 0
overall_key = None

for pi, (w15e, w2e, extra, w15k, w2k, k8_hint) in enumerate(unique_pairs):
    for ci, cd in enumerate(cd_opts):
        k = [0]*KLEN
        for b,v in confirmed.items(): k[b]=v
        for b,v in w15k.items(): k[b]=v
        for b,v in w2k.items(): k[b]=v
        for b,v in cd.items(): k[b]=v
        
        # Remaining: {7, 8, 45, 49}
        remain = [7, 8, 45, 49]
        
        # Quick hill-climb on remaining (200 random restarts)
        best_local = 0
        best_local_k = None
        
        for restart in range(200):
            kk = list(k)
            if restart == 0 and k8_hint is not None:
                kk[8] = k8_hint
            else:
                for b in remain:
                    kk[b] = random.randint(0, MOD-1)
            
            improved = True
            while improved:
                improved = False
                for b in remain:
                    best_v = kk[b]
                    best_c = 0
                    for v in range(MOD):
                        kk[b] = v
                        c = 0
                        for wi in range(nw):
                            t = word_text(decrypt_word(wi, kk)).upper()
                            if t in WORDLIST: c += 1
                        if c > best_c: best_c = c; best_v = v
                    kk[b] = best_v
            
            c, _ = count_all(kk)
            if c > best_local:
                best_local = c
                best_local_k = list(kk)
        
        if best_local > overall_best:
            overall_best = best_local
            overall_key = list(best_local_k)
            c, matched = count_all(best_local_k)
            print(f"\n  NEW BEST: {c}/68 words")
            print(f"    w15='{w15e}' w2='{w2e}' {extra} cd#{ci}")
            print(f"    Matched: {matched}")
    
    if (pi+1) % 5 == 0:
        print(f"  ... processed {pi+1}/{len(unique_pairs)} pairs, best={overall_best}")

# Phase 3: Also try WITHOUT word constraints via hill-climbing on all undetermined
print(f"\n{'='*80}")
print(f"Phase 3: Free hill-climbing (500 restarts)")
print(f"{'='*80}")

remaining_all = [b for b in range(KLEN) if b not in confirmed]
k = list(overall_key) if overall_key else [0]*KLEN
for b,v in confirmed.items(): k[b]=v

for restart in range(500):
    kk = list(k)
    if restart > 0:
        for b in random.sample(remaining_all, random.randint(1, len(remaining_all))):
            kk[b] = random.randint(0, MOD-1)
    
    improved = True
    while improved:
        improved = False
        random.shuffle(remaining_all)
        for b in remaining_all:
            best_v = kk[b]; best_c = 0
            for v in range(MOD):
                kk[b] = v
                c = 0
                for wi in range(nw):
                    t = word_text(decrypt_word(wi, kk)).upper()
                    if t in WORDLIST: c += 1
                if c > best_c: best_c = c; best_v = v
            kk[b] = best_v
    
    c, matched = count_all(kk)
    if c > overall_best:
        overall_best = c
        overall_key = list(kk)
        print(f"  Restart {restart}: {c}/68 words")
        print(f"    Matched: {matched}")

print(f"\n{'='*80}")
print(f"FINAL RESULT")
print(f"{'='*80}")
k = overall_key
c, matched = count_all(k)
dec = [(cipher[i]-k[i%KLEN])%MOD for i in range(N)]
txt = ''.join(LAT[v] for v in dec)
cnts = Counter(dec)
ioc = sum(c2*(c2-1) for c2 in cnts.values())/(N*(N-1))*MOD

print(f"Words: {c}/{nw}, IoC*29: {ioc:.3f}")
print(f"Key: {k}")
print(f"Key (LAT): {''.join(LAT[v] for v in k)}")
print(f"Text:\n{txt}")
print(f"\nMatched: {matched}")

ms = {wi for wi,_ in matched}
print(f"\nWord-by-word:")
for wi,(s,wr) in enumerate(words):
    v = dec[s:s+len(wr)]
    t = word_text(v)
    m = "Y" if wi in ms else " "
    print(f"  {m} w{wi}: '{t}'")

print(f"\n=== DONE ===")
