"""
GPU Running-Key Scanner for Liber Primus P21-P54
=================================================
Tests enormous text corpora as running keys using GPU-parallelism.

For each text source (Tao Te Ching, Bhagavad Gita, Bible, etc.) and
each cipher mode (sub/add/beaufort), tests ALL offsets simultaneously
on GPU and reports any that produce IoC > 0.045 or word-score > 200.

Also tests:
  - P.S. number (131 digits) in multiple representations
  - Guitar tones key extended / repeated
  - Concatenations of all known LP text in different orders
  - Random text from our wordlist (dictionary crib approach)

Usage:
  python gpu_running_key.py [gpu_id]

Outputs: data/gpu_runkey_results.txt
"""

import sys, os, time, json
from pathlib import Path
from collections import Counter
import numpy as np
import cupy as cp

sys.stdout.reconfigure(encoding='utf-8')

GPU_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
cp.cuda.Device(GPU_ID).use()
OUTFILE = f'data/gpu_runkey_gpu{GPU_ID}.txt'
M = 29

IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

LETTER_MAP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14
}
DIGRAPH_MAP = {'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28}

LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE','BEHAVIORS',
    'CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS','GREAT','WEALTH',
    'NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN','PREPARED','DESTROY',
    'PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH','WITHIN','HOLY','BEING',
    'EACH','FOLLOW','END','EMERGE','WILL','EVERY','DEEP','ABOVE','SAME',
    'OTHER','ONE','DIVINE','FROM','A','I','IS','OF','IN','NOT','WITH','HAVE',
    'SELF','PATH','QUESTION','DISCOVER','INSIDE','YOURSELF','IMPOSE','NOTHING',
    'OTHERS','CHAPTER','PARABLE','INSTAR','AND','FOR','BUT','BY','AS','AT'
}

def text_to_gp(txt):
    txt = txt.upper().replace('\n', ' ').replace('\r', ' ')
    result = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in DIGRAPH_MAP:
            result.append(DIGRAPH_MAP[txt[i:i+2]]); i += 2
        elif txt[i] in LETTER_MAP:
            result.append(LETTER_MAP[txt[i]]); i += 1
        else:
            i += 1
    return result

def load_flat(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    return [RUNE_TO_IDX[c] for c in path.read_text(encoding='utf-8') if c in RUNE_TO_IDX]

def load_words(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    text = path.read_text(encoding='utf-8'); words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX: curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr: words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return words

# ─── Load cipher ─────────────────────────────────────────────────────────────
print('Loading cipher...')
words_all = []
cipher_list = []
for pg in range(21, 55):
    clist = load_flat(pg)
    wlist = load_words(pg)
    cipher_list.extend(clist)
    words_all.extend(wlist)
CIPHER = np.array(cipher_list, dtype=np.int32)
N = len(CIPHER)
print(f'  Cipher: {N} runes, {len(words_all)} words')

# Singleton positions
sing_pos = []; sing_cip = []
pos = 0
for w in words_all:
    if len(w) == 1: sing_pos.append(pos); sing_cip.append(w[0])
    pos += len(w)
SING_POS = np.array(sing_pos, dtype=np.int32)
SING_CIP = np.array(sing_cip, dtype=np.int32)
N_SING = len(SING_POS)
print(f'  {N_SING} singletons')

# ─── GPU kernel: test all offsets of a key stream ────────────────────────────
# For each offset o in [0..len(key)-N]:
#   key_segment = key[o..o+N]  (or repeated/cyclic)
#   plain[i] = decrypt(cipher[i], key[(o+i) % key_len])
#   score[o] = sum of singleton hits (max = N_SING) + IoC * 1000
IOC_KERNEL = cp.RawKernel(r'''
extern "C" __global__
void scan_offsets(
    const int* cipher,     // [N]
    const int* key,        // [KEY_LEN] — treated as periodic
    int*       sing_hits,  // [N_OFF] output
    float*     ioc_score,  // [N_OFF] output
    int        N,
    int        KEY_LEN,
    int        N_OFF,
    int        N_SING_ARG,
    const int* sing_pos,
    const int* sing_cip,
    int        mode        // 0=sub, 1=add, 2=beaufort
) {
    int o = blockIdx.x * blockDim.x + threadIdx.x;
    if (o >= N_OFF) return;

    // Count singleton hits
    int hits = 0;
    for (int s = 0; s < N_SING_ARG; s++) {
        int p = sing_pos[s];
        int c = sing_cip[s];
        int kv = key[(o + p) % KEY_LEN];
        int dec;
        if (mode == 0) dec = (c - kv + 29) % 29;
        else if (mode == 1) dec = (c + kv) % 29;
        else dec = (kv - c + 29) % 29;
        if (dec == 10 || dec == 24) hits++;
    }
    sing_hits[o] = hits;

    // Compute IoC of first 500 chars (for speed)
    int freq[29] = {0};
    int cnt = 0;
    int lim = min(N, 500);
    for (int i = 0; i < lim; i++) {
        int c = cipher[i];
        int kv = key[(o + i) % KEY_LEN];
        int dec;
        if (mode == 0) dec = (c - kv + 29) % 29;
        else if (mode == 1) dec = (c + kv) % 29;
        else dec = (kv - c + 29) % 29;
        freq[dec]++;
        cnt++;
    }
    float ioc = 0.0f;
    for (int r = 0; r < 29; r++) ioc += (float)freq[r] * (float)(freq[r] - 1);
    ioc_score[o] = (cnt > 1) ? ioc / ((float)cnt * (float)(cnt-1)) : 0.0f;
}
''', 'scan_offsets')

IOC_THRESHOLD  = 0.042  # above random (0.0345)
SING_THRESHOLD = int(N_SING * 0.5)  # at least 50% singletons pass

cp_cipher   = cp.array(CIPHER, dtype=cp.int32)
cp_sing_pos = cp.array(SING_POS, dtype=cp.int32)
cp_sing_cip = cp.array(SING_CIP, dtype=cp.int32)

def scan_key_stream(key_vals, key_name, modes=None):
    """Test key_vals as periodic running key against all cipher pages."""
    if modes is None: modes = [('sub',0), ('add',1), ('beaufort',2)]
    key_np = np.array(key_vals, dtype=np.int32)
    key_len = len(key_np)
    if key_len < 10: return
    # Extend to at least N if short (periodic)
    if key_len < N:
        repeats = (N // key_len) + 2
        key_np = np.tile(key_np, repeats)[:N + key_len]
        key_len = len(key_np)

    N_OFF = min(key_len, 50000)  # max offsets to try

    cp_key = cp.array(key_np, dtype=cp.int32)
    cp_hits = cp.zeros(N_OFF, dtype=cp.int32)
    cp_ioc  = cp.zeros(N_OFF, dtype=cp.float32)

    for mode_name, mode_int in modes:
        BLK = 256
        GRD = (N_OFF + BLK - 1) // BLK
        IOC_KERNEL((GRD,), (BLK,),
            (cp_cipher, cp_key, cp_hits, cp_ioc,
             cp.int32(N), cp.int32(key_len), cp.int32(N_OFF),
             cp.int32(N_SING), cp_sing_pos, cp_sing_cip, cp.int32(mode_int)))
        cp.cuda.Stream.null.synchronize()

        hits_np = cp_hits.get()
        ioc_np  = cp_ioc.get()

        # Find best offsets
        best_by_sing = np.argsort(-hits_np)[:5]
        best_by_ioc  = np.argsort(-ioc_np)[:5]
        best_offs    = sorted(set(best_by_sing.tolist() + best_by_ioc.tolist()))

        any_good = False
        for o in np.argsort(-hits_np)[:3].tolist() + np.argsort(-ioc_np)[:3].tolist():
            if hits_np[o] >= SING_THRESHOLD or ioc_np[o] >= IOC_THRESHOLD:
                any_good = True
                break

        if any_good or hits_np.max() > SING_THRESHOLD * 0.7:
            msg = (f'[{key_name}][{mode_name}] '
                   f'Best sing: {hits_np.max()}/{N_SING} at off={int(np.argmax(hits_np))}, '
                   f'Best IoC: {float(ioc_np.max()):.4f} at off={int(np.argmax(ioc_np))}')
            print(msg)
            with open(OUTFILE, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')

            # For the very best offset, do full word decode
            best_o = int(np.argmax(hits_np))
            if hits_np[best_o] >= SING_THRESHOLD:
                # CPU decode
                kv_arr = key_np
                decoded_words = []
                ki = best_o
                for w in words_all[:100]:
                    dec = []
                    for c in w:
                        k = kv_arr[ki % key_len]
                        if mode_name == 'sub': dec.append((c - k) % M)
                        elif mode_name == 'add': dec.append((c + k) % M)
                        else: dec.append((k - c) % M)
                        ki += 1
                    decoded_words.append(''.join(IDX_TO[v] for v in dec))
                ws = sum((len(w)*20+30 if w in LP_VOCAB else 0) for w in decoded_words)
                detail = f'  offset={best_o}, wordscore={ws}: {" ".join(decoded_words[:30])}'
                print(detail)
                with open(OUTFILE, 'a', encoding='utf-8') as f:
                    f.write(detail + '\n')

# ─── Build key sources ────────────────────────────────────────────────────────

print('\n=== Building key sources ===')
key_sources = []

# 1. LP1 solved pages (P00-P20) 
lp1_solved_pages = [0,1,2,3,4,5,6,7,8,9,10,13,14,15,16,17,18,19,20]
lp1_stream = []
for pg in lp1_solved_pages: lp1_stream.extend(load_flat(pg))
key_sources.append((lp1_stream, 'LP1-solved(0-20)'))

# 2. LP2 cleartext
lp2_pages = [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
lp2_stream = []
for pg in lp2_pages: lp2_stream.extend(load_flat(pg))
key_sources.append((lp2_stream, 'LP2-cleartext'))

# 3. LP1+LP2 combined
key_sources.append((lp1_stream + lp2_stream, 'LP1+LP2'))

# 4. LP2+LP1 (reversed order)
key_sources.append((lp2_stream + lp1_stream, 'LP2+LP1'))

# 5. P.S. number (various representations)
ps_str = '10412790658919985359827898739594318956404425106955675643739226952372682423852959081739834390370374475764863415203423499357108713631'
ps_digits_mod29 = [int(d) % 29 for d in ps_str]
key_sources.append((ps_digits_mod29, 'PS-num-digits-mod29'))

def to_base29(n):
    if n == 0: return [0]
    d = []
    while n > 0: d.append(n % 29); n //= 29
    return list(reversed(d))

ps_base29 = to_base29(int(ps_str))
key_sources.append((ps_base29, 'PS-num-base29'))

# SHA-256 of P.S. as GP stream
import hashlib
ps_sha256 = hashlib.sha256(ps_str.encode()).digest()
ps_sha_gp = [b % 29 for b in ps_sha256]
key_sources.append((ps_sha_gp, 'PS-sha256-mod29'))

# 6. Guitar tones [G=6,F=0,D=23,C=5,B=17,C=5] extended
guitar_base = [6, 0, 23, 5, 17, 5]
guitar_num  = [int(d) % 29 for d in '0421812877725']
key_sources.append((guitar_base, 'guitar-tones'))
key_sources.append((guitar_num,  'guitar-number'))
key_sources.append((guitar_base + guitar_num, 'guitar-combined'))

# 7. Cookie primes 167, 761
cookie_key = []
import hashlib
for prime in [167, 761]:
    h = hashlib.sha256(str(prime).encode()).digest()
    cookie_key.extend([b % 29 for b in h])
key_sources.append((cookie_key, 'cookie-primes-167-761'))

# 8. Missing telnet primes (21st–200th prime) mod 29
def sieve(limit):
    s = list(range(limit)); s[1]=0
    for i in range(2, int(limit**0.5)+1):
        if s[i]:
            for j in range(i*i, limit, i): s[j]=0
    return [x for x in s if x]
primes = sieve(2000)
missing_telnet = primes[20:200]  # p(21)=73 through ~p(200)
missing_mod29  = [p % 29 for p in missing_telnet]
key_sources.append((missing_mod29, 'missing-telnet-primes-p21-p200'))

# 9. Deor poem GP values
deor_text = Path('data/deor_poem.txt').read_text(encoding='utf-8') if Path('data/deor_poem.txt').exists() else ''
deor_gp = text_to_gp(deor_text)
if deor_gp: key_sources.append((deor_gp, 'deor-poem-GP'))

# 10. Self-Reliance
sr_text = Path('data/self_reliance.txt').read_text(encoding='utf-8', errors='replace') if Path('data/self_reliance.txt').exists() else ''
sr_gp = text_to_gp(sr_text)[:20000]
if sr_gp: key_sources.append((sr_gp, 'self-reliance-GP'))

# 11. Emerson Essays (first 30K)
em_text = Path('data/emerson_essays.txt').read_text(encoding='utf-8', errors='replace') if Path('data/emerson_essays.txt').exists() else ''
em_gp = text_to_gp(em_text)[:30000]
if em_gp: key_sources.append((em_gp, 'emerson-essays-GP'))

# 12. Fibonacci sequence mod 29 (extended)
def fib_mod29(n):
    a, b = 0, 1; r = []
    for _ in range(n): r.append(a % 29); a, b = b, (a+b) % 100003
    return r
key_sources.append((fib_mod29(N+1000), 'fibonacci-mod29'))

# 13. Prime totients mod 29
totients_mod29 = [(p-1) % 29 for p in primes[:N+100]]
key_sources.append((totients_mod29, 'prime-totients-mod29'))

# 14. All LP runes (whole book, cleartext pages only)
all_lp_clear = []
for pg in range(0, 75):
    if pg not in range(21, 55):
        all_lp_clear.extend(load_flat(pg))
key_sources.append((all_lp_clear, 'all-LP-cleartext'))

# 15. Emerson key_search_corpus (the big corpus)
ks_text = Path('data/key_search_corpus.txt').read_text(encoding='utf-8', errors='replace') if Path('data/key_search_corpus.txt').exists() else ''
ks_gp = text_to_gp(ks_text)[:50000]
if ks_gp: key_sources.append((ks_gp[:30000], 'key-search-corpus-GP'))

# 16. Liber AL vel Legis
lal_text = Path('reference/liber_al_vel_legis.txt').read_text(encoding='utf-8', errors='replace') if Path('reference/liber_al_vel_legis.txt').exists() else ''
lal_gp = text_to_gp(lal_text)
if lal_gp: key_sources.append((lal_gp, 'liber-al-GP'))

# 17. LP Transcript (community)
transcript = Path('reference/liber_primus_transcript.md').read_text(encoding='utf-8', errors='replace') if Path('reference/liber_primus_transcript.md').exists() else ''
trans_gp = text_to_gp(transcript)[:50000]
if trans_gp: key_sources.append((trans_gp, 'LP-transcript-GP'))

# 18. Wordlist brute: all 1-8 letter words as repeated Vigenere keys
wordlist = []
if Path('data/wordlist.txt').exists():
    wordlist = [w.strip().upper() for w in Path('data/wordlist.txt').read_text(encoding='utf-8', errors='replace').splitlines() if 3 <= len(w.strip()) <= 10]
    print(f'  Wordlist: {len(wordlist)} words')

print(f'  Total key sources: {len(key_sources)}')

# ─── Run scans ───────────────────────────────────────────────────────────────
with open(OUTFILE, 'w', encoding='utf-8') as f:
    f.write(f'GPU {GPU_ID} Running-Key Scanner — {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'Cipher: {N} runes, Singletons: {N_SING}\n')
    f.write('='*60 + '\n')

print(f'\n=== Scanning {len(key_sources)} key sources on GPU {GPU_ID} ===')
t0 = time.time()

for i, (key_vals, key_name) in enumerate(key_sources):
    if not key_vals: continue
    print(f'[{i+1}/{len(key_sources)}] {key_name} ({len(key_vals)} vals)... ', end='', flush=True)
    t1 = time.time()
    scan_key_stream(key_vals, key_name)
    print(f'{time.time()-t1:.1f}s')

print(f'\n=== Main sources done in {time.time()-t0:.1f}s ===')

# ─── Phase 2: Wordlist Vigenere scan ─────────────────────────────────────────
if GPU_ID == 0:
    print('\n=== Phase 2: Wordlist scan (keywords 3-10 letters) ===')
    # Build large batch: for each word, extend to N and scan all 3 modes
    # Group into batches of 10,000 words

    BATCH = 10000
    t_word_start = time.time()
    hits_log = []

    for batch_start in range(0, len(wordlist), BATCH):
        batch = wordlist[batch_start:batch_start+BATCH]

        # Convert each word to GP array, tile to length N+word_len
        best_sing = 0
        for word in batch:
            gp_word = text_to_gp(word)
            if not gp_word: continue
            wl = len(gp_word)
            # Tile to at least N
            n_tile = (N // wl) + 2
            key_np = (gp_word * n_tile)[:N]

            cp_key = cp.array(np.array(key_np, dtype=np.int32))
            cp_hits = cp.zeros(1, dtype=cp.int32)
            cp_ioc  = cp.zeros(1, dtype=cp.float32)

            for mode_name, mode_int in [('sub',0),('add',1),('beaufort',2)]:
                IOC_KERNEL((1,), (1,),
                    (cp_cipher, cp_key, cp_hits, cp_ioc,
                     cp.int32(N), cp.int32(N), cp.int32(1),
                     cp.int32(N_SING), cp_sing_pos, cp_sing_cip, cp.int32(mode_int)))
                cp.cuda.Stream.null.synchronize()
                h = int(cp_hits.get()[0])
                ioc = float(cp_ioc.get()[0])
                if h > best_sing: best_sing = h
                if h >= int(N_SING * 0.5) or ioc >= IOC_THRESHOLD:
                    msg = f'WORD HIT: {word} [{mode_name}] singletons={h}/{N_SING} ioc={ioc:.4f}'
                    print(msg)
                    hits_log.append(msg)
                    with open(OUTFILE, 'a', encoding='utf-8') as f:
                        f.write(msg + '\n')

        n_done = min(batch_start + BATCH, len(wordlist))
        elapsed = time.time() - t_word_start
        rate = n_done / elapsed if elapsed > 0 else 0
        print(f'  Words {batch_start}-{n_done}/{len(wordlist)} | best_sing={best_sing}/{N_SING} | {rate:.0f} words/s')

elif GPU_ID == 1:
    # GPU 1: run Tao Te Ching + Bhagavad Gita content from online fetch
    # These are too important to skip — include inline key versions
    
    # Tao Te Ching (first chapter in various translations - commonly used in LP)
    tao_text = """
    THE TAO THAT CAN BE TOLD IS NOT THE ETERNAL TAO
    THE NAME THAT CAN BE NAMED IS NOT THE ETERNAL NAME
    THE NAMELESS IS THE BEGINNING OF HEAVEN AND EARTH
    THE NAMED IS THE MOTHER OF TEN THOUSAND THINGS
    EVER DESIRELESS ONE CAN SEE THE MYSTERY
    EVER DESIRING ONE CAN SEE THE MANIFESTATIONS
    THESE TWO SPRING FROM THE SAME SOURCE BUT DIFFER IN NAME
    THIS APPEARS AS DARKNESS DARKNESS WITHIN DARKNESS
    THE GATE TO ALL MYSTERY
    WITHOUT GOING OUTSIDE YOU MAY KNOW THE WHOLE WORLD
    WITHOUT LOOKING THROUGH THE WINDOW YOU MAY SEE THE WAYS OF HEAVEN
    THE FURTHER YOU GO THE LESS YOU KNOW
    THUS THE SAGE KNOWS WITHOUT TRAVELLING SEES WITHOUT LOOKING WORKS WITHOUT DOING
    KNOWING OTHERS IS WISDOM KNOWING YOURSELF IS ENLIGHTENMENT
    MASTERING OTHERS REQUIRES FORCE MASTERING YOURSELF REQUIRES STRENGTH
    HE WHO KNOWS HE HAS ENOUGH IS RICH
    PERSEVERANCE IS A SIGN OF WILL POWER
    HE WHO STAYS WHERE HE IS ENDURES
    TO DIE BUT NOT TO PERISH IS TO BE ETERNALLY PRESENT
    DO THE DIFFICULT THINGS WHILE THEY ARE EASY
    ACCOMPLISH THE GREAT TASK BY A SERIES OF SMALL ACTS
    A JOURNEY OF A THOUSAND MILES BEGINS WITH A SINGLE STEP
    RESPOND TO ANGER WITH VIRTUE DO NOT RETURN EVIL WITH EVIL
    DEAL WITH THE DIFFICULT WHILE IT IS STILL EASY
    ACHIEVE GREATNESS IN LITTLE THINGS
    THE WAY TO DO IS TO BE
    FOR THE IGNORANT THE TRIFLES SEEM IMPORTANT FOR THE WISE THE IMPORTANT THINGS SEEM TRIFLES
    BENDING WITH THE WIND IS STRONGER THAN STANDING RIGID
    YIELD AND OVERCOME BEND AND BE STRAIGHT EMPTY AND BE FULL
    THE SOFT OVERCOMES THE HARD THE GENTLE OVERCOMES THE RIGID
    EVERYONE KNOWS THIS BUT FEW CAN PUT IT INTO PRACTICE
    BECAUSE OF A GREAT LOVE ONE IS COURAGEOUS
    SIMPLICITY PATIENCE COMPASSION THESE THREE ARE YOUR GREATEST TREASURES
    SIMPLE IN ACTIONS AND THOUGHTS YOU RETURN TO THE SOURCE OF BEING
    PATIENT WITH BOTH FRIENDS AND ENEMIES YOU ACCORD WITH THE WAY THINGS ARE
    COMPASSIONATE TOWARD YOURSELF YOU RECONCILE ALL BEINGS IN THE WORLD
    """
    
    # Bhagavad Gita key sections
    gita_text = """
    NEVER WAS THERE A TIME WHEN I DID NOT EXIST NOR YOU NOR ALL THESE BEINGS
    NOR IN THE FUTURE SHALL ANY OF US CEASE TO BE
    THE SOUL IS NEVER BORN NOR DIES AT ANY TIME
    IT HAS NOT COME INTO BEING DOES NOT COME INTO BEING AND WILL NOT COME INTO BEING
    IT IS UNBORN ETERNAL EVER EXISTING AND PRIMEVAL
    IT IS NOT SLAIN WHEN THE BODY IS SLAIN
    AS A PERSON PUTS ON NEW GARMENTS GIVING UP OLD ONES
    SIMILARLY THE SOUL ACCEPTS NEW MATERIAL BODIES GIVING UP THE OLD AND USELESS ONES
    THE SOUL CAN NEVER BE CUT BY WEAPONS NOR BURNED BY FIRE
    NOR CAN IT BE MOISTENED BY WATER NOR WITHERED BY THE WIND
    DO YOUR DUTY AND DO NOT WAVER
    LET RIGHT DEEDS BE THY MOTIVE NOT THE FRUIT WHICH COMES FROM THEM
    SET THINE HEART UPON THY WORK BUT NEVER ON ITS REWARD
    WORK NOT FOR A REWARD BUT NEVER CEASE TO DO THY WORK
    BE NOT PROUD OF LEARNING QUESTION EVERY TRUTH
    THE SOUL IS IMMORTAL THE BODY IS MORTAL
    THOSE WHO SEEK THE TRUTH WILL FIND IT
    KNOWLEDGE OF TRUTH DESTROYS IGNORANCE
    THE ETERNAL SELF WITHIN YOU KNOWS ALL TRUTH
    THOSE WHO SURRENDER TO THE SUPREME BEING FIND TRUTH
    """
    
    tao_gp = text_to_gp(tao_text)
    gita_gp = text_to_gp(gita_text)
    
    print(f'Tao Te Ching: {len(tao_gp)} GP values')
    print(f'Bhagavad Gita: {len(gita_gp)} GP values')
    
    scan_key_stream(tao_gp, 'tao-te-ching-inline')
    scan_key_stream(gita_gp, 'bhagavad-gita-inline')
    scan_key_stream(tao_gp + gita_gp, 'tao+gita-combined')
    
    # Also test all LP wisdom sentences extended / reversed
    wisdom_text = """
    SOME WISDOM THE PRIMES ARE SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS
    AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY
    THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY
    CONSUMPTION PRESERVATION ADHERENCE
    AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN
    QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS
    WELCOME PILGRIM TO THE PILGRIMAGE OF THE SACRED RUNES
    AN END EVERY BEGINNING IS AN END AND EVERY END IS A BEGINNING
    THE DIVINE IS WITHIN YOU SEEK IT WITHIN PRIMES WITHIN TRUTH WITHIN SELF
    SEEK AND YE SHALL FIND KNOCK AND THE DOOR SHALL BE OPENED UNTO YOU
    """
    wisdom_gp = text_to_gp(wisdom_text)
    scan_key_stream(wisdom_gp, 'LP-wisdom-all-sections')
    
    # Run GPU 1 wordlist (different range)
    if wordlist:
        print('\n=== GPU 1: Wordlist scan ===')
        for batch_start in range(0, len(wordlist), 10000):
            batch = wordlist[batch_start:batch_start+10000]
            for word in batch:
                gp_word = text_to_gp(word)
                if not gp_word: continue
                n_tile = (N // len(gp_word)) + 2
                key_np = (gp_word * n_tile)[:N]
                cp_key = cp.array(np.array(key_np, dtype=np.int32))
                cp_hits = cp.zeros(1, dtype=cp.int32)
                cp_ioc  = cp.zeros(1, dtype=cp.float32)
                for mode_name, mode_int in [('sub',0),('add',1),('beaufort',2)]:
                    IOC_KERNEL((1,),(1,),
                        (cp_cipher, cp_key, cp_hits, cp_ioc,
                         cp.int32(N), cp.int32(N), cp.int32(1),
                         cp.int32(N_SING), cp_sing_pos, cp_sing_cip, cp.int32(mode_int)))
                    cp.cuda.Stream.null.synchronize()
                    h = int(cp_hits.get()[0])
                    if h >= int(N_SING * 0.5):
                        msg = f'WORD HIT GPU1: {word} [{mode_name}] singletons={h}/{N_SING}'
                        print(msg)
                        with open(OUTFILE, 'a', encoding='utf-8') as f: f.write(msg + '\n')
            print(f'  Batch {batch_start} done')

print(f'\nAll done. Results in {OUTFILE}')
