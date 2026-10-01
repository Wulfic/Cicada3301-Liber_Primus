"""
P02 Hill-Climber with English bigrams from Emerson corpus
==========================================================
Starts from KNOWN_KEY which already has visible fragments,
uses 577K English text from Emerson essays for bigram/trigram scoring.
"""

import os, sys, math, random, time
from collections import defaultdict

RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,  'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,
    'ᚻ': 8,  'ᚾ': 9,  'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LATIN = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA',
]
N = 29
KEY_LEN = 43
CONFIRMED = {12: 26, 13: 9, 14: 1}  # THAT confirmed

# Original known key from session 17 crib analysis
KNOWN_KEY = [23, 9, 14, 21, 14, 18, 26, 25, 4, 19, 22, 4, 26, 9, 1,
             18, 9, 15, 20, 1, 6, 21, 20, 25, 21, 11, 16, 22, 15, 16,
             16, 0, 0, 2, 15, 4, 2, 0, 9, 22, 26, 22, 15]

DIGRAPH_TO_GP = {'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
MONO_TO_GP = {
    'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,'N':9,
    'I':10,'J':11,'P':13,'X':14,'S':15,'T':16,'B':17,'E':18,'M':19,'L':20,
    'D':23,'A':24,'Y':26,
}

def text_to_gp(text):
    result = []
    text = text.upper()
    i = 0
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPH_TO_GP:
            result.append(DIGRAPH_TO_GP[text[i:i+2]])
            i += 2
        elif text[i] in MONO_TO_GP:
            result.append(MONO_TO_GP[text[i]])
            i += 1
        else:
            i += 1
    return result

def parse_cipher(path):
    seq = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not any(c in RUNE_TO_IDX for c in line):
            continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                seq.append(RUNE_TO_IDX[ch])
    return seq

def parse_word_structure(path):
    words = []
    cur = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not any(c in RUNE_TO_IDX for c in line):
            continue
        for ch in line:
            if ch in RUNE_TO_IDX:
                cur.append(RUNE_TO_IDX[ch])
            elif ch in '-./':
                if cur:
                    words.append(cur[:])
                    cur = []
    if cur:
        words.append(cur)
    return words

def build_kv_pairs(cipher_seq):
    result = []
    ki = 0
    for c in cipher_seq:
        if c == 0:
            result.append((0, None))
        else:
            result.append((c, ki % KEY_LEN))
            ki += 1
    return result

def decode(kv_pairs, key):
    out = []
    for c, kp in kv_pairs:
        out.append(0 if kp is None else (c - key[kp]) % N)
    return out

def decode_latin(kv_pairs, key):
    return ''.join(IDX_TO_LATIN[v] for v in decode(kv_pairs, key))

def build_bigrams(corpus_path):
    """Build GP bigram log-probability table from corpus."""
    text = open(corpus_path, encoding='utf-8', errors='ignore').read()
    gp = text_to_gp(text)
    
    bigrams = defaultdict(int)
    trigrams = defaultdict(int)
    for i in range(len(gp)-1):
        bigrams[(gp[i], gp[i+1])] += 1
    for i in range(len(gp)-2):
        trigrams[(gp[i], gp[i+1], gp[i+2])] += 1
    
    total_bg = sum(bigrams.values())
    total_tg = sum(trigrams.values())
    
    # Add-1 smoothing, compute log probs
    floor_bg = math.log(0.01 / total_bg) if total_bg > 0 else -10.0
    floor_tg = math.log(0.01 / total_tg) if total_tg > 0 else -10.0
    
    bg_log = {}
    for k, c in bigrams.items():
        bg_log[k] = math.log((c + 1) / (total_bg + N*N))
    
    tg_log = {}
    for k, c in trigrams.items():
        tg_log[k] = math.log((c + 1) / (total_tg + N*N*N))
    
    print(f"Corpus: {len(gp)} GP chars, {len(bigrams)} bigrams, {len(trigrams)} trigrams")
    return bg_log, tg_log, floor_bg, floor_tg

def score_bigram(dec_list, bg_log, tg_log, floor_bg, floor_tg):
    """Log-prob score based on bigrams + trigrams."""
    score = 0.0
    for i in range(len(dec_list)-1):
        score += bg_log.get((dec_list[i], dec_list[i+1]), floor_bg)
    for i in range(len(dec_list)-2):
        score += tg_log.get((dec_list[i], dec_list[i+1], dec_list[i+2]), floor_tg) * 0.5
    return score

# LP word set for bonus scoring
LP_BONUS_WORDS = set()
for w in """A AN THE OF AND TO IS IT OR IN ON AT HE HIS HIM WAS HAD NOT YOU WHO BE
THAT WHAT WITH WILL FROM ALL
AKOAN KOAN MAN DECIDED GO STUDY WITH MASTER WENT DOOR WISHES STUDENT TOLD
NAME CALLED THOUGHT MOMENT PROFESSOR HUMAN BEING SPECIES CONSCIOUSNESS
INHABITING ARBITRARY BODY MERELY GETTING IRRITATED TRAILED OFF PAUSE
WELCOME COME HERE SAME OTHER SONG IDENTITY SELF INNER VOICE
LESSON EXPLAINED DURING SOUND HEAR HEARD SPEAKING LISTEN
WISDOM TRUTH KNOWLEDGE FOLLOW BELIEVE SACRED DIVINE DIVINITY
MIND REALITY WORLD PROGRAM PRIMES TOTIENT INTELLIGENCE
QUESTION DISCOVER NOTHING WITHIN PILGRIM JOURNEY
SHADOW CONSUMPTION PRESERVATION ADHERENCE LOSS BEHAVIORS CAUSE
THELOSSOFDIVINITY THELOSSOF CIRCUMFERENCE
CABAL SHADOWS AETHEREAL VOID CARNAL FORM MOBIUS ANALOG MOURNFUL""".split():
    gp = tuple(text_to_gp(w))
    if gp:
        LP_BONUS_WORDS.add(gp)

def score_full(kv_pairs, word_kvs, key, bg_log, tg_log, floor_bg, floor_tg):
    dec = decode(kv_pairs, key)
    s = score_bigram(dec, bg_log, tg_log, floor_bg, floor_tg)
    
    # Word bonus for LP vocabulary matches
    for word_enc in word_kvs:
        d = tuple((c - key[kp]) % N if kp is not None else 0 for c, kp in word_enc)
        if d in LP_BONUS_WORDS:
            s += len(d) * 5.0
    return s

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cipher_path = os.path.join(base, 'pages', 'page_02', 'runes.txt')
    corpus_path = os.path.join(base, 'data', 'emerson_essays.txt')
    
    cipher_seq = parse_cipher(cipher_path)
    kv_pairs = build_kv_pairs(cipher_seq)
    word_src = parse_word_structure(cipher_path)
    
    # Build per-word kv pairs
    word_kvs = []
    ki = 0
    for word in word_src:
        we = []
        for c in word:
            if c == 0:
                we.append((0, None))
            else:
                we.append((c, ki % KEY_LEN))
                ki += 1
        word_kvs.append(we)
    
    print(f"P02: {len(cipher_seq)} runes, {len(word_src)} words")
    
    # Build bigram table from Emerson corpus
    bg_log, tg_log, floor_bg, floor_tg = build_bigrams(corpus_path)
    
    free_positions = [kp for kp in range(KEY_LEN) if kp not in CONFIRMED]
    
    # Show KNOWN_KEY decode first
    kn = list(KNOWN_KEY)
    for kp, kv in CONFIRMED.items():
        kn[kp] = kv
    print(f"\nKNOWN_KEY decode:")
    print(decode_latin(kv_pairs, kn))
    print(f"KNOWN_KEY score: {score_full(kv_pairs, word_kvs, kn, bg_log, tg_log, floor_bg, floor_tg):.2f}")
    print()
    
    # ─── Phase 1: Hill-climb from KNOWN_KEY ──────────────────────────────
    print("Phase 1: Hill-climbing from KNOWN_KEY...")
    current_key = kn[:]
    current_score = score_full(kv_pairs, word_kvs, current_key, bg_log, tg_log, floor_bg, floor_tg)
    
    improved = True
    round_num = 0
    while improved:
        improved = False
        round_num += 1
        for kp in free_positions:
            best_v = current_key[kp]
            best_s = current_score
            for v in range(N):
                if v == current_key[kp]: continue
                current_key[kp] = v
                s = score_full(kv_pairs, word_kvs, current_key, bg_log, tg_log, floor_bg, floor_tg)
                if s > best_s:
                    best_s = s
                    best_v = v
            current_key[kp] = best_v
            if best_v != kn[kp]:
                current_score = best_s
                if round_num == 1:
                    print(f"  kp{kp:2d}: {kn[kp]:2d}({IDX_TO_LATIN[kn[kp]]}) → {best_v:2d}({IDX_TO_LATIN[best_v]}) score→{best_s:.1f}")
                    improved = True
        if not improved and round_num == 1:
            print("  No improvements in round 1")
    
    print(f"\nAfter hill-climb (score={current_score:.2f}):")
    print(decode_latin(kv_pairs, current_key))
    
    # Show word-by-word
    ki2 = 0
    lp_count = 0
    for wi, word in enumerate(word_src):
        we = []
        for c in word:
            if c == 0: we.append((0, None))
            else: we.append((c, ki2 % KEY_LEN)); ki2 += 1
        d = tuple((c - current_key[kp]) % N if kp is not None else 0 for c, kp in we)
        wt = ''.join(IDX_TO_LATIN[v] for v in d)
        m = " ✓" if d in LP_BONUS_WORDS else ""
        if d in LP_BONUS_WORDS: lp_count += 1
        print(f"  w{wi+1:2d} [{len(word):2d}]: {wt:24s}{m}")
    print(f"LP bonus words matched: {lp_count}")
    
    # ─── Phase 2: Simulated annealing from hill-climb result ─────────────
    print(f"\nPhase 2: SA refinement from hillclimb result...")
    T = 2.0
    T_min = 0.001  
    cooling = 0.99997
    n_iter = 600_000
    
    best_key = list(current_key)
    best_score = current_score
    
    t0 = time.time()
    accepted = 0
    for it in range(n_iter):
        T *= cooling
        if T < T_min: break
        
        # Swap strategy: perturb 1 or 2 positions
        trial = list(current_key)
        kp = random.choice(free_positions)
        trial[kp] = random.randint(0, N-1)
        
        s = score_full(kv_pairs, word_kvs, trial, bg_log, tg_log, floor_bg, floor_tg)
        delta = s - current_score
        if delta > 0 or random.random() < math.exp(delta / max(T, 1e-9)):
            current_key = trial
            current_score = s
            accepted += 1
            if s > best_score:
                best_score = s
                best_key = list(trial)
        
        if it % 100000 == 0:
            elapsed = time.time() - t0
            print(f"  iter={it:7d} T={T:.4f} best={best_score:.1f} cur={current_score:.1f} [{elapsed:.1f}s]")
    
    print(f"\nSA done: {time.time()-t0:.1f}s, best={best_score:.2f}, accepted={accepted}/{n_iter}")
    
    # Final output
    print(f"\n{'='*60}")
    print("FINAL RESULT:")
    print(f"Key: {best_key}")
    print(f"GP:  {[IDX_TO_LATIN[v] for v in best_key]}")
    print()
    final_decode = decode_latin(kv_pairs, best_key)
    print(f"Full text: {final_decode}")
    print()
    
    # Word-by-word
    ki3 = 0
    lp_total = 0
    print("Word-by-word final:")
    for wi, word in enumerate(word_src):
        we = []
        for c in word:
            if c == 0: we.append((0, None))
            else: we.append((c, ki3 % KEY_LEN)); ki3 += 1
        d = tuple((c - best_key[kp]) % N if kp is not None else 0 for c, kp in we)
        wt = ''.join(IDX_TO_LATIN[v] for v in d)
        m = " ✓" if d in LP_BONUS_WORDS else ""
        if d in LP_BONUS_WORDS: lp_total += 1
        print(f"  w{wi+1:2d} [{len(word):2d}]: {wt:24s}{m}")
    print(f"\nFinal LP words: {lp_total}/{len(word_src)}")

if __name__ == '__main__':
    main()
