"""
P18 SOLVER v6 - Dictionary-based Constraint Propagation
For each word slot, enumerate ALL possible English words from a large dictionary.
Use constraint propagation to determine undetermined key buckets.
"""
import os, sys, random, itertools
from collections import Counter, defaultdict

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
    """Convert English word to ALL possible GP rune sequences (considering digraph choices).
    Returns list of tuples, each tuple is a valid GP encoding."""
    word = word.upper()
    results = []
    
    def recurse(pos, acc):
        if pos >= len(word):
            results.append(tuple(acc))
            return
        # Try digraph first (if 2+ chars remain)
        if pos + 1 < len(word):
            digraph = word[pos:pos+2]
            if digraph in DIGRAPHS:
                recurse(pos + 2, acc + [DIGRAPHS[digraph]])
        # Single character
        ch = word[pos]
        if ch in ENG2GP:
            recurse(pos + 1, acc + [ENG2GP[ch]])
    
    recurse(0, [])
    return results

# Large English word list - common words + LP vocabulary
WORDLIST = set()

# Top ~3000 English words covering most written text
_words_raw = """
a about above after again against all am an and any are as at be because been
before being below between both but by can could did do does doing down during
each few for from further get got had has have having he her here hers herself
him himself his how i if in into is it its itself just know let like make me
might more most my myself no nor not now of off on once only or other our ours
ourselves out over own same she should so some such than that the their theirs
them themselves then there these they this those through to too under until up
us very was we were what when where which while who whom why will with would
you your yours yourself yourselves

about above across actually after afternoon again against ago ahead almost
already also always among amount another answer any anyone anything anyway
appear area around arrive ask attention away back bad base beautiful became
become bed been before began begin behind believe below beside best better
between beyond big black blood blue board body book born both bottom bring
brother build burn busy but buy call came care carry case catch caught cause
center certain chance change child children choose city class clear close cold
come common complete consider contain continue control could country course
cover cross cry cut dark daughter day dead dear decide deep depend describe
develop did die different difficult dinner direction discover do does dog
done door doubt down draw dream drink drive drop dry during each early earth
east eat edge effect egg eight else end enough even evening ever every example
experience explain eye face fact fall family far fast father feel feet few
field fight fill final find fine finger finish fire first five floor fly
follow food foot for force foreign forget form found four free friend from
front full further game garden gave general get girl give glad glass go god
gold gone good got great green grew ground group grow guess had hair half hall
hand happen happy hard has hat have he head hear heart heavy held help her here
herself high hill him himself his hit hold hole home hope horse hot hour house
how however hundred hunt hurry husband idea if important in include increase
inside instead interest into iron island it its just keep kind king knew know
land language large last late laugh lay lead learn least leave left less let
life light like line list listen little live long look lose lot love low
machine made main make man many mark matter may me mean meet member men might
mind miss moment money month moon more morning most mother mountain mouth move
much music must my name near necessary need never new next night nine no noise
none nor north nose not note nothing notice now number of off offer office
often oh old on once one only open or order other our out outside over own
page pair part pass past people perhaps period person picture piece place plan
plant play please point position possible power prepare present president
pretty print probably problem produce product program provide public pull
purpose push put question quite ran rather reach read ready real receive
remember report rest result return right river road room round run said same
sat save saw say sea second see seem self send serve set seven several shall
shape she short should show side since sit six sleep small smell so some son
soon sort sound south speak special spring stand star start state stay step
still stood stop story street strong student such sudden summer sun sure
system table take talk tell ten test than that the their them then there
these they thing think third this those though thought thousand three through
throw tie time to today together told tomorrow tonight too took top toward
town trade tree trouble true turn twelve two type under understand united
until up upon us use usual valley very voice walk wall want war warm was
watch water way we weather well went were west what when where while white
who whole why wide will win wind window wish with without woman wonder
won word work world would write wrong wrote year yes yet you young

able accept across add admit afraid age along already anger animal appear
arm army art baby bank battle bear beat beauty bed believe bird bit
bite bone born bottom box break breakfast bright broke broken brown build
burn business buy captain care certain chair chief choice claim clean clear
climb close clothe coat coin collect color comfort command company compare
complete concern condition connect consider continue corner cost cotton count
country courage course cover cross cup danger dare deal death die
difference dinner direction dirty divide doctor door drink drive dust
duty ear earn eat eleven else enemy enjoy enough entrance equal escape
evening event ever example except face fail fairly fall false family
father fear feed fight form forward foundation fresh friend full
garden gate gather gift glad gold govern grain grass guard
hall hang happy hate hear heart heat heavy hide hill hold
honest hope horse house human hungry hurt idea imagine include iron

above accept across act add afraid agree air allow almost along
already always among amount ancient anger animal appear arm army
arrive art attack attempt august aware battle beauty began begin belong
beneath beyond bite bless blood blow boil bone born bottom break breath
bride bright bring build burn calm capture care cattle cause chain
chance change charge cheap chief choice claim cloth cloud collect
command common compare concern condition connect conquer conscious
corner count couple courage crowd crush cure current curse damage
dance danger dark dead deal death decide declare deep defeat desert
desire destroy determine develop die discover disease display distance
divine doubt drag draw drink drop ear earn eat eight either
else empty end enemy enter escape even evil exact example exchange
exist expect experience explain express extend extreme face fail faith
fall false fast fear figure fill final fire flesh flow flower
follow fool force forest forget form forward found free fresh
friend fruit gain garden gate gather gentle gift glad glory gold
gone good govern grace grain grand grass greed green grew
ground grow guard guess guide half hang hate hear heart heat
held help hide hill hold hollow honor hope horse hour house
hunger hunt hurry idea imagine increase inside instead iron island

absolute accept accomplish achieve acquire action advance advantage advice
affair agree allow ancient announce appearance approach arrange arrive
assist attach attack attempt attention authority avoid awake aware
balance base battle beauty begin behave belief belong beneath benefit
birth blame blood body bound brain branch brave breath bridge bright
broad build burden busy calm capable capture careful cause center
chain chance character charge chief church circle claim class clean
clear climb close collect colour combine comfort command common
communicate company compare complete compose concern condition conduct
connect conscious consider contain continue control convenient
conversation cool correct cost council count courage cover create
creature criminal cross crowd cry current custom damage danger dare
dark daughter deal death debt decay decide declare deep defeat
definite degree delay deliberate demand department depend describe
desert desire destroy detail develop device devote die difference
difficult dinner direct direction disappear discover discuss disease
dismiss distance distinct district disturb divine division doctor
doubt drag draw dress drink drive drop dry dust duty

each ear early earth ease east easy eat edge education effect
efficient effort eight either election else embrace emerge emotion
employ empty encourage end enemy energy engage engine enjoy enormous
enough enter entire entrance equal escape especially establish
even evening event ever every evidence evil exact examine example
excellent except exchange excite exercise exist expect expense
experience experiment explain express extend extreme

faith false familiar family famous far fast fate father favor fear
feed feel fellow field fight figure fill final find fine finger
finish fire firm first fish fit five fix flat flesh float floor
flow flower fly follow food fool foot force foreign forest forget
form former fortune forward found foundation four free freedom fresh
friend from front fruit full fundamental future

gain gather general generation gentle gift give glad glass glory go
god gold gone good govern grace grain grand grass great green
grew ground group grow growth guard guess guide

habit hair half hall hand hang happen happy hard harm hat hate have
head health hear heart heat heaven heavy height help here herself
hide high hill history hold hole hollow holy home honest honour hope
horse host hot hour house however human hundred hunger hunt hurry

dream light dark open close find seek truth knowledge wisdom
consciousness reality illusion perception awareness enlightenment
power strength weakness destruction creation existence void
nothing everything something anything
sacred profane divine mortal eternal temporal infinite finite
cipher key code rune secret mystery hidden reveal
journey path way road direction north south east west
spirit soul mind body flesh bone blood heart
ancient modern past present future moment always never before
silence sound voice word language speech
fire water earth air
freedom prison chain bond
question answer riddle puzzle
shadow light darkness brightness
thought think believe know understand comprehend wisdom
one two three four five six seven eight nine ten
pilgrim master teacher student
watch observe notice see look gaze
hidden reveal show display manifest
become transform change shift alter
shall will must can may might should would could
together alone single whole part piece fragment
order chaos harmony balance pattern structure
work labor toil effort struggle strive
among within without between beyond above below upon beneath
begin end start finish complete accomplish
own self same other another different new old
already yet still even also too enough rather quite very much
because since therefore thus hence although though whereas while
consume produce create destroy build break
consume devour eat feast hunger thirst
primal raw pure clean clear bright
follow lead guide direct instruct
attempt try effort endeavor strive
listen hear speak tell say ask answer
carry hold bear bring take give send
circle square triangle line point curve spiral
embrace reject accept deny confirm
gather scatter collect spread
narrow wide deep shallow high low
true false real fake genuine
sure certain positive likely probable
gain lose win fail succeed
raise lower lift drop rise fall
open close shut seal lock free
""".strip()

for line in _words_raw.split('\n'):
    for w in line.split():
        w = w.strip().upper()
        if len(w) >= 1:
            WORDLIST.add(w)

# Add LP/Cicada-specific vocabulary
_lp_words = """
DIVINITY PRIMES PRIME INTELLIGENCE CIRCUMFERENCE CONSUMPTION PARABLE
INSTRUCTION INTERCONNECTED UNDERSTANDING ILLUMINATION AWAKENING
REARRANGING NUMBERS PROGRAM GEMATRIA PRIMUS TOTIENT FIBONACCI
EMERGENCE EVOLUTION TRANSCENDENCE TRANSFORMATION LIBERATION ENCRYPTION
DECRYPTION BEAUTIFUL DANGEROUS IMPOSSIBLE IMPERFECT PERFECTION
IRRELEVANT IRREVERSIBLE UNSEEN UNFOLD UNTO THEE THOU DOTH HATH
WHILST AMONGST BETWIXT THINE WHENCE UNTO THEREOF HEREIN THEREIN
WITHIN WITHOUT OURSELVES THEMSELVES YOURSELVES ITSELF HIMSELF HERSELF
MYSELF ANYONE EVERYONE SOMEONE NOWHERE SOMEWHERE EVERYWHERE NOTHING
EVERYTHING SOMETHING ANYTHING WHATSOEVER WHOSOEVER WHENEVER WHEREVER
WHATEVER HOWEVER WHICHEVER WHETHER NEITHER EITHER NOBODY SOMEBODY
EVERYBODY ANYBODY ANYWHERE SOMEWHERE BEHOLD FORSAKE BESTOW ENDURE
PERCEIVE CONCEIVE RECEIVE BELIEVE ACHIEVE DECEIVE RETRIEVE
CONSIDER DISCOVER REMEMBER TOGETHER ANOTHER PERHAPS ALREADY ALTHOUGH
AGAINST THROUGH BETWEEN BENEATH TOWARDS FORWARD BACKWARD INWARD
OUTWARD ONWARD UPWARD DOWNWARD WORSHIP PILGRIM PASSAGE COMMAND
CIPHER RIDDLE ENIGMA MYSTERY SECRET SACRED PROFANE MORTAL DIVINE
ANGEL DAEMON SPIRIT GHOST SHADOW VESSEL TEMPLE ALTAR SACRIFICE
OFFERING BLESSING CURSE PRAYER CHANT RITUAL CEREMONY DOCTRINE
PROPHECY JUDGEMENT JUSTICE MERCY GRACE TRUTH BEAUTY WONDER AWE
""".strip()
for w in _lp_words.split():
    WORDLIST.add(w.strip().upper())

print(f"Dictionary: {len(WORDLIST)} words")

# Pre-compute GP encodings for all dictionary words
# Group by rune count for fast lookup
gp_by_runelen = defaultdict(list)  # runelen -> [(word, gp_tuple), ...]
for w in WORDLIST:
    encodings = english_to_gp_all(w)
    for enc in encodings:
        gp_by_runelen[len(enc)].append((w, enc))

# Show encoding stats
for rlen in sorted(gp_by_runelen.keys()):
    if rlen <= 12:
        print(f"  {rlen}-rune words: {len(gp_by_runelen[rlen])} encodings")

cipher, words = load_page(18)
N = len(cipher)
print(f"\nP18: {N} runes, {len(words)} words")

# Show word length distribution
wlens = Counter(len(wr) for _, wr in words)
print(f"Word lengths: {dict(sorted(wlens.items()))}")

# 31 CONFIRMED key values
confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}
undetermined = sorted(set(range(KLEN)) - set(confirmed.keys()))

print(f"\n{'='*80}")
print(f"Phase 1: Dictionary-based candidate generation per word")
print(f"{'='*80}")

def get_word_candidates(wi):
    """For a word at index wi, find all dictionary words that match 
    given the confirmed key values."""
    start, wrunes = words[wi]
    nrunes = len(wrunes)
    
    # Get cipher values and bucket assignments
    positions = list(range(start, start + nrunes))
    buckets = [p % KLEN for p in positions]
    cipher_vals = [cipher[p] for p in positions]
    
    # For each rune position, determine if the plaintext value is known (bucket confirmed)
    # or free (bucket undetermined)
    known = {}  # position_in_word -> plaintext_value
    free_positions = []  # positions_in_word with undetermined buckets
    for j in range(nrunes):
        b = buckets[j]
        if b in confirmed:
            known[j] = (cipher_vals[j] - confirmed[b]) % MOD
        else:
            free_positions.append(j)
    
    # Find all dictionary words that could match
    candidates = []
    for eng_word, gp_enc in gp_by_runelen.get(nrunes, []):
        # Check if GP encoding matches at known positions
        match = True
        for j, val in known.items():
            if gp_enc[j] != val:
                match = False
                break
        if match:
            # Compute the KEY VALUES this candidate would require at free positions
            key_req = {}
            for j in free_positions:
                b = buckets[j]
                req_key = (cipher_vals[j] - gp_enc[j]) % MOD
                key_req[b] = req_key
            candidates.append((eng_word, gp_enc, key_req))
    
    return candidates, buckets, known, free_positions

# Phase 1: Generate candidates for all words
word_candidates = {}
for wi in range(len(words)):
    cands, buckets, known, free = get_word_candidates(wi)
    start, wrunes = words[wi]
    word_candidates[wi] = {
        'candidates': cands,
        'buckets': buckets,
        'known_vals': known,
        'free_positions': free,
        'nrunes': len(wrunes),
        'start': start
    }
    
    # Show info for interesting words
    n_free = len(free)
    n_cands = len(cands)
    
    if n_cands > 0 and n_cands <= 30:
        dec_current = [(cipher[start+j] - confirmed.get((start+j)%KLEN, 0)) % MOD for j in range(len(wrunes))]
        lat_current = ''.join(LAT[v] for v in dec_current)
        print(f"\n  w{wi} ({len(wrunes)}r, free={n_free}): current='{lat_current}'")
        print(f"    {n_cands} candidate(s):")
        for eng, gp, kreq in cands[:20]:
            lat = ''.join(LAT[v] for v in gp)
            print(f"      '{eng}' ({lat}) -> key_req: {kreq}")
    elif n_cands == 0 and n_free == 0:
        # Fully determined, no match - show for reference
        dec = [(cipher[start+j] - confirmed[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
        lat = ''.join(LAT[v] for v in dec)
        # Only show short ones
        if len(wrunes) <= 5:
            print(f"  w{wi} ({len(wrunes)}r, FIXED): '{lat}' -- NO DICT MATCH")

print(f"\n{'='*80}")
print(f"Phase 2: Constraint Propagation")
print(f"{'='*80}")

# Build constraint graph
# For each undetermined bucket, collect all constraints from word candidates
bucket_constraints = defaultdict(set)  # bucket -> set of possible values (from any word)
bucket_word_values = defaultdict(lambda: defaultdict(set))  # bucket -> word_idx -> set of possible values

for wi, info in word_candidates.items():
    if len(info['candidates']) == 0:
        continue
    for eng, gp, kreq in info['candidates']:
        for b, v in kreq.items():
            bucket_constraints[b].add(v)
            bucket_word_values[b][wi].add(v)

# Also, for buckets that appear in NO word candidates, they're completely free
for b in undetermined:
    if b not in bucket_constraints:
        bucket_constraints[b] = set(range(MOD))
        print(f"  Bucket {b}: NO constraints from any dictionary word")

# Show constraint summary
print("\nBucket constraint summary:")
for b in undetermined:
    values = bucket_constraints[b]
    n_words = len(bucket_word_values[b])
    if len(values) <= 10:
        print(f"  Bucket {b}: {len(values)} possible values {sorted(values)} from {n_words} words")
    else:
        print(f"  Bucket {b}: {len(values)} possible values from {n_words} words")

# Iterative constraint propagation
# Step 1: Find buckets with only 1 possible value across ALL word candidates
print("\n--- Propagation Round 1 ---")
new_confirmed = dict(confirmed)
changed = True
round_num = 1

while changed:
    changed = False
    
    # Regenerate candidates with current confirmed set
    for wi in range(len(words)):
        start, wrunes = words[wi]
        nrunes = len(wrunes)
        positions = list(range(start, start + nrunes))
        buckets = [p % KLEN for p in positions]
        cipher_vals = [cipher[p] for p in positions]
        
        known = {}
        free_positions = []
        for j in range(nrunes):
            b = buckets[j]
            if b in new_confirmed:
                known[j] = (cipher_vals[j] - new_confirmed[b]) % MOD
            else:
                free_positions.append(j)
        
        if not free_positions:
            continue
        
        # Find matching candidates
        new_cands = []
        for eng_word, gp_enc in gp_by_runelen.get(nrunes, []):
            match = True
            for j, val in known.items():
                if gp_enc[j] != val:
                    match = False
                    break
            if match:
                key_req = {}
                for j in free_positions:
                    b = buckets[j]
                    req_key = (cipher_vals[j] - gp_enc[j]) % MOD
                    key_req[b] = req_key
                new_cands.append((eng_word, gp_enc, key_req))
        
        word_candidates[wi]['candidates'] = new_cands
    
    # Rebuild bucket constraints
    bucket_constraints = defaultdict(set)
    bucket_word_values = defaultdict(lambda: defaultdict(set))
    
    for wi, info in word_candidates.items():
        for eng, gp, kreq in info['candidates']:
            for b, v in kreq.items():
                bucket_constraints[b].add(v)
                bucket_word_values[b][wi].add(v)
    
    # Find words with EXACTLY 1 candidate -> lock in those key values
    for wi, info in word_candidates.items():
        cands = info['candidates']
        if len(cands) == 1:
            eng, gp, kreq = cands[0]
            for b, v in kreq.items():
                if b not in new_confirmed:
                    print(f"  UNIQUE MATCH: w{wi} = '{eng}' -> bucket {b} = {v} ({LAT[v]})")
                    new_confirmed[b] = v
                    changed = True
    
    # Also check: if a bucket has only 1 possible value across ALL words that use it
    for b in list(set(range(KLEN)) - set(new_confirmed.keys())):
        if b in bucket_constraints and len(bucket_constraints[b]) == 1:
            v = list(bucket_constraints[b])[0]
            print(f"  UNIQUE VALUE: bucket {b} = {v} ({LAT[v]}) (all word candidates agree)")
            new_confirmed[b] = v
            changed = True
    
    if changed:
        round_num += 1
        print(f"\n--- Propagation Round {round_num} ---")

print(f"\nAfter propagation: {len(new_confirmed)}/53 buckets confirmed")
still_undet = sorted(set(range(KLEN)) - set(new_confirmed.keys()))
print(f"Still undetermined: {still_undet}")

print(f"\n{'='*80}")
print(f"Phase 3: Word-by-word analysis of remaining candidates")  
print(f"{'='*80}")

# For each word with remaining undetermined buckets, show candidate words
for wi in range(len(words)):
    info = word_candidates[wi]
    start = info['start']
    nrunes = info['nrunes']
    positions = list(range(start, start + nrunes))
    buckets = [p % KLEN for p in positions]
    has_undet = any(b not in new_confirmed for b in buckets)
    
    if not has_undet:
        continue
    
    cands = info['candidates']
    if len(cands) == 0:
        continue
    
    undet_buckets = [b for b in buckets if b not in new_confirmed]
    print(f"\n  w{wi} ({nrunes}r, undet_buckets={undet_buckets}):")
    if len(cands) <= 50:
        for eng, gp, kreq in cands[:50]:
            lat = ''.join(LAT[v] for v in gp)
            print(f"    '{eng}' ({lat}) -> {kreq}")
    else:
        print(f"    {len(cands)} candidates (too many to list)")
        # Show the most common key values per bucket
        for b in undet_buckets:
            vals = [kreq[b] for _, _, kreq in cands if b in kreq]
            vc = Counter(vals).most_common(5)
            print(f"      bucket {b}: top values = {vc}")

print(f"\n{'='*80}")
print(f"Phase 4: Greedy bucket optimization + Hill-climbing")
print(f"{'='*80}")

# Build the best key from confirmed + optimized undetermined
best_key = [0] * KLEN
for b, v in new_confirmed.items():
    best_key[b] = v

# For remaining undetermined, try each value and pick the one that maximizes word matches
remaining_undet = sorted(set(range(KLEN)) - set(new_confirmed.keys()))

# Scoring function
def score_key(k):
    """Score a key: (word_matches, ioc, bigram_score)"""
    dec = [(cipher[i] - k[i%KLEN]) % MOD for i in range(N)]
    matches = 0
    matched_words = []
    for wi, (start, wrunes) in enumerate(words):
        word_dec = dec[start:start+len(wrunes)]
        word_str = ''.join(LAT[v] for v in word_dec).upper()
        if word_str in WORDLIST:
            matches += 1
            matched_words.append((wi, word_str))
    
    # IoC
    counts = Counter(dec)
    n = len(dec)
    ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * MOD if n > 1 else 0
    
    return matches, ic, matched_words

# Greedy: for each undetermined bucket, try all 29 values
print(f"\nGreedy optimization of {len(remaining_undet)} undetermined buckets...")
for b in remaining_undet:
    best_val = 0
    best_matches = -1
    for v in range(MOD):
        best_key[b] = v
        m, _, _ = score_key(best_key)
        if m > best_matches:
            best_matches = m
            best_val = v
    best_key[b] = best_val

m, ic, mwords = score_key(best_key)
print(f"After greedy: {m} words matched, IoC*29={ic:.3f}")

# Hill-climbing with random restarts
print(f"\nHill-climbing (200 restarts)...")
overall_best_key = list(best_key)
overall_best_score = m
overall_best_ic = ic

for restart in range(200):
    k = list(best_key)  # Start from greedy solution
    # Randomly perturb undetermined buckets
    if restart > 0:
        n_perturb = random.randint(1, len(remaining_undet))
        perturbed = random.sample(remaining_undet, n_perturb)
        for b in perturbed:
            k[b] = random.randint(0, MOD-1)
    
    # Hill-climb
    improved = True
    while improved:
        improved = False
        random.shuffle(remaining_undet)
        for b in remaining_undet:
            current_m, _, _ = score_key(k)
            best_v = k[b]
            for v in range(MOD):
                k[b] = v
                m_test, _, _ = score_key(k)
                if m_test > current_m:
                    current_m = m_test
                    best_v = v
            k[b] = best_v
            if best_v != k[b]:
                improved = True
    
    m, ic, mwords = score_key(k)
    if m > overall_best_score or (m == overall_best_score and ic > overall_best_ic):
        overall_best_score = m
        overall_best_ic = ic
        overall_best_key = list(k)
        word_strs = {wi: ws for wi, ws in mwords}
        unmatched_strs = []
        for wi, (start, wrunes) in enumerate(words):
            if wi not in word_strs:
                dec = [(cipher[start+j] - k[(start+j)%KLEN]) % MOD for j in range(len(wrunes))]
                unmatched_strs.append((wi, ''.join(LAT[v] for v in dec)))
        
        print(f"  Restart {restart}: {m} words, IoC*29={ic:.3f}")
        print(f"    Matched: {[f'w{wi}={ws}' for wi, ws in mwords]}")

print(f"\n{'='*80}")
print(f"FINAL RESULT")
print(f"{'='*80}")

k = overall_best_key
m, ic, mwords = score_key(k)
print(f"Words matched: {m}/{len(words)}")
print(f"IoC*29: {ic:.3f}")
print(f"Key: {k}")
print(f"Key (LAT): {''.join(LAT[v] for v in k)}")

# Show full decryption
dec = [(cipher[i] - k[i%KLEN]) % MOD for i in range(N)]
full_text = ''.join(LAT[v] for v in dec)
print(f"\nFull text: {full_text}")

# Show word-by-word
print(f"\nWord-by-word:")
matched_set = {wi for wi, _ in mwords}
for wi, (start, wrunes) in enumerate(words):
    word_dec = dec[start:start+len(wrunes)]
    word_str = ''.join(LAT[v] for v in word_dec)
    b_list = [(start+j)%KLEN for j in range(len(wrunes))]
    undet = [b for b in b_list if b not in new_confirmed]
    marker = "✓" if wi in matched_set else " "
    print(f"  {marker} w{wi}: '{word_str}' (buckets={b_list}, undet={undet})")

# Show confirmed vs undetermined key
print(f"\nKey analysis:")
print(f"  Confirmed ({len(new_confirmed)}): ", end="")
for b in sorted(new_confirmed.keys()):
    print(f"{b}:{LAT[new_confirmed[b]]}", end=" ")
print()

still_undet = sorted(set(range(KLEN)) - set(new_confirmed.keys()))
print(f"  Optimized ({len(still_undet)}): ", end="")
for b in still_undet:
    print(f"{b}:{LAT[k[b]]}", end=" ")
print()

print(f"\n=== DONE ===")
