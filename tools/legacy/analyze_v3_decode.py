"""
Full decode analysis of GPU hillclimber v3 checkpoint.
Decodes all P21-54 pages and analyzes quality per page and word slot.
"""
import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

# --- GP Alphabet ---
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
M = 29

def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return None, None
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return runes, words

# Load cipher
print('Loading cipher...', flush=True)
cipher_list = []; words_all_meta = []; cum = 0; page_offsets = {}
for pg in range(21, 55):
    runes, words = load_page(pg)
    if runes is None: continue
    page_offsets[pg] = cum
    cum += len(runes)
    cipher_list.extend(runes)
    words_all_meta.extend([(pg, len(runes), w) for w in words])

CIPHER = cipher_list
N_CIPHER = len(CIPHER)
print(f'Cipher: {N_CIPHER} runes, {len(words_all_meta)} words', flush=True)

# Load TTP link map
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]
LINK_MAP = list(range(N_CIPHER))
for src_s, dst_s, ln in TTP_CONSTRAINTS:
    for i in range(ln):
        LINK_MAP[dst_s + i] = LINK_MAP[src_s + i]

# Load LP vocabulary
LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}
def gp_encode(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return r

solved_pages = list(range(0, 21)) + list(range(55, 75))
LP_VOCAB = set()
for pg in solved_pages:
    _, swords = load_page(pg)
    if swords:
        for sw in swords:
            LP_VOCAB.add(''.join(IDX_TO[v] for v in sw))

# Add canonical LP words
LP_CANON = [
    'CONSUMPTION','PRESERUATION','PRESERVATION','ADHERENCE',
    'SOMEWISDOM','DIUINITY','DIVINITY','CIRCUMFERENCE',
    'THELOSSOF','THELOSSOFDIUINITY','PROGRAM','REALITY','MIND',
    'PRIMES','SACRED','ENCRYPTED','KNOWTHIS','KNOW','THIS',
    'WISDOM','AN','INSTRUCTION','BEHAVIORS','PRACTICES','LOSS',
    'PREPARED','DESTROY','FOLLOW','TRUTH','IMPOSE','NOTHING','OTHERS',
    'SEEK','WELCOME','PILGRIM','WITHIN','ALL','THE','THAT','WHICH',
    'CAUSE','THREE','AMASS','GREAT','WEALTH','NEUER','NEVER',
    'BECOME','ATTACHED','WHAT','YOU','OWN','QUESTION','DISCOVER',
    'YOURSELF','INSIDE','HOLY','BEING','EACH','FORM','EMERGE',
    'INSTAR','PARABLE','SHADOW','VOID','CARNAL','AETHEREAL',
    'DECEPTION','MOBIUS','OBSCURA','CABAL','INTELLIGENCE',
    'TOTIENT','PRIME','DIVINE','PATH','STRENGTH','PAIN',
    'THEM','AND','YOUR','HAVE','HAUE','SEEC','FUNCTION','LATER',
    'LOSE','CAUSE','ABOUT','SO','THEIR','SELF','JOURNEY','DEEP',
    'IS','IT','OF','TO','NOT','FOR','ARE','WITH','IN','AS',
    'THROUGH','GOING','WITHIN','LIKE','WILL','BUT','FIND','WAY',
    'HERE','END','ALONG','DISCOVER','ARRIVE','OUTSIDE',
]
for w in LP_CANON:
    LP_VOCAB.add(w.upper())

# Load checkpoint key
ck_file = Path('data/gpu_hill_checkpoint_gpu1_v3.json')
if not ck_file.exists():
    print('ERROR: checkpoint not found')
    sys.exit(1)
ck = json.loads(ck_file.read_text())
KEY = ck['key']
print(f'Checkpoint: score={ck["score"]:.1f}, step={ck["step"]:,}, singletons={ck["singletons"]}', flush=True)
print()

# Build word slots
WORD_SLOTS = []; ki = 0
for pg, total_runes, w in words_all_meta:
    WORD_SLOTS.append((pg, ki, len(w)))
    ki += len(w)

# Decode everything
def decode_word(wstart, wlen):
    return ''.join(IDX_TO[(CIPHER[wstart+i] - KEY[wstart+i]) % M] for i in range(wlen))

def ioc(seq):
    if len(seq) < 2: return 0
    c = Counter(seq); n = len(seq)
    return sum(v*(v-1) for v in c.values()) / (n*(n-1)) * M

# Per-page analysis
print('='*70)
print('PER-PAGE DECODE ANALYSIS')
print('='*70)
all_lp_words_found = []
page_lp_counts = {}
for pg in range(21, 55):
    if pg not in page_offsets: continue
    poff = page_offsets[pg]
    _, pw = load_page(pg)
    if not pw: continue
    total_runes = sum(len(w) for w in pw)
    
    decoded_words = []
    lp_hits = 0; total_slots = len(pw)
    ki = poff
    for w in pw:
        dec = decode_word(ki, len(w))
        decoded_words.append(dec)
        if dec in LP_VOCAB:
            lp_hits += 1
            all_lp_words_found.append((pg, ki, dec, len(w)))
        ki += len(w)
    
    # IoC of decoded runes
    decoded_runes = [(CIPHER[poff+i] - KEY[poff+i]) % M for i in range(total_runes)]
    page_ioc = ioc(decoded_runes)
    
    pct = lp_hits / total_slots * 100 if total_slots else 0
    print(f'P{pg:02d}: {total_runes:4} runes, {total_slots:3} words, LP={lp_hits:3}/{total_slots:3} ({pct:5.1f}%), IoC={page_ioc:.4f}')
    
    # Show first 20 decoded words
    preview = ' '.join(decoded_words[:20])
    print(f'  Preview: {preview}')
    
    page_lp_counts[pg] = (lp_hits, total_slots, decoded_words)

print()
print('='*70)
print('ALL LP VOCABULARY HITS (sorted by page)')
print('='*70)
for pg, pos, word, wlen in sorted(all_lp_words_found, key=lambda x: (x[0], x[1])):
    print(f'  P{pg:02d} pos={pos:5d}: {word} (len={wlen})')

print()
print(f'TOTAL LP VOCAB HITS: {len(all_lp_words_found)}')

# Long LP words (len > 6) are most meaningful
long_hits = [(pg, pos, w, l) for pg, pos, w, l in all_lp_words_found if l > 6]
print(f'LP HITS len>6: {len(long_hits)}')
for pg, pos, word, wlen in sorted(long_hits, key=lambda x: -x[3]):
    print(f'  P{pg:02d} pos={pos:5d}: {word} (len={wlen})')

print()
print('='*70)
print('FULL DECODE - ALL PAGES (word-by-word with LP status)')
print('='*70)
for pg in range(21, 55):
    if pg not in page_offsets: continue
    _, pw = load_page(pg)
    if not pw: continue
    poff = page_offsets[pg]
    ki = poff
    print(f'\n--- PAGE {pg} (offset={poff}) ---')
    line = ''
    for w in pw:
        dec = decode_word(ki, len(w))
        marker = '*' if dec in LP_VOCAB else ' '
        line += f'{marker}{dec} '
        if len(line) > 100:
            print(line)
            line = ''
        ki += len(w)
    if line: print(line)

print()
print('='*70)
print('TTP CONSTRAINT ANALYSIS')
print('='*70)
# For each TTP pair, show both regions
for ci, (src_s, dst_s, ln) in enumerate(TTP_CONSTRAINTS):
    # Decode source region
    src_words = []
    # Find words in source region
    ki = 0
    for pg, total_runes, w in words_all_meta:
        wlen = len(w)
        if ki >= src_s and ki + wlen <= src_s + ln:
            dec = decode_word(ki, wlen)
            src_words.append(dec)
        ki += wlen
    
    # Since TTP means same key for src and dst, dst decodes identically
    print(f'TTP-{ci+1}: src={src_s}-{src_s+ln}, dst={dst_s}-{dst_s+ln}, len={ln}')
    preview = ' '.join(src_words[:15])
    print(f'  Decode: {preview}')
