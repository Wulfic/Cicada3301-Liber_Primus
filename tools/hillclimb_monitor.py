"""
hillclimb_monitor.py — Real-time monitoring & validation for gpu_hillclimber_v2
================================================================================
Reads the active checkpoint, computes per-page quality metrics, detects false
solves, and exports reverse-engineerable solution data.

Usage:
  python Tools/hillclimb_monitor.py              # one-shot analysis
  python Tools/hillclimb_monitor.py --watch       # re-run every 60s
  python Tools/hillclimb_monitor.py --export      # write per-page solution JSON

Outputs:
  stdout: per-page table with IoC, word score, noise patterns, LP vocab density
  data/hillclimb_monitor_latest.json: machine-readable state (when --export)
"""

import sys, json, time, math, os
from pathlib import Path
from collections import Counter
import numpy as np

M = 29

# ── GP Alphabet ──────────────────────────────────────────────────────────────
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X',
          'S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}
LETTER_TO_GP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14,
    'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28
}

def _gp_encode(phrase):
    w = phrase.upper().replace(' ', ''); r = []; i = 0
    while i < len(w):
        if i+1 < len(w) and w[i:i+2] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i:i+2]]); i += 2
        elif w[i] in LETTER_TO_GP:
            r.append(LETTER_TO_GP[w[i]]); i += 1
        else: i += 1
    return r

# ── Load pages ───────────────────────────────────────────────────────────────
def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return [], [], ''
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    raw_structure = []  # track separators for word boundary reconstruction
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/&$%' and curr:
            words.append(tuple(curr)); curr = []
            raw_structure.append(ch)
    if curr: words.append(tuple(curr))
    return runes, words, text

cipher_list = []; words_per_page = {}; page_offsets = {}; page_lengths = {}
cum = 0
for pg in range(21, 55):
    runes, words, _ = load_page(pg)
    if runes:
        page_offsets[pg] = cum
        page_lengths[pg] = len(runes)
        words_per_page[pg] = words
        cum += len(runes)
        cipher_list.extend(runes)

CIPHER = np.array(cipher_list, dtype=np.int32)
N_CIPHER = len(CIPHER)

# ── TTP constraints (for validation) ────────────────────────────────────────
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]

# ── Confirmed cribs ─────────────────────────────────────────────────────────
CONFIRMED_CRIBS = [
    ('CONSUMPTION',         31),
    ('KNOWTHIS',           476),
    ('PROGRAM',            599),
    ('DIUINITY',          1356),
    ('PRESERUATION',      2093),
    ('CIRCUMFERENCE',     3080),
    ('SOMEWISDOM',        4131),
    ('THELOSSOFDIUINITY', 4325),
    ('ADHERENCE',         8532),
]

# ── Singleton positions ─────────────────────────────────────────────────────
singleton_positions = []; pos = 0
for pg in range(21, 55):
    _, words, _ = load_page(pg)
    local_pos = 0
    for w in words:
        if len(w) == 1:
            singleton_positions.append(page_offsets.get(pg, 0) + local_pos)
        local_pos += len(w)

# ── Known noise patterns from Session 11 diagnosis ──────────────────────────
NOISE_PATTERNS = ['DPTS', 'CDPI', 'TSUH', 'EATSUH', 'TSEATS', 'DPTSUH',
                  'CDPTSUH', 'SUHEAT', 'THOFTH', 'EOTHEO']

# ── LP Vocabulary (extended) ────────────────────────────────────────────────
LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','DIUINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','PRESERUATION','ADHERENCE',
    'AMASS','GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS',
    'OF','IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER',
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS',
    'PARABLE','INSTAR','SHADOW','FORM','AND','FOR','BUT','BY','AS','AT',
    'THAT','WHICH','DECEPTION','ABOUT','MOST','STRONG',
    'WORTH','BUFFER','AETHEREAL','CARNAL','OBSCURA','MOBIUS','PRIMAL',
    'PRIME','CEASING','CEASE','LOSE','PATTERN','PATTERNS',
    'KNOWLEDGE','BUILD','BEGIN','DETAIL','PROFUNDITY','WHOLE','SIMPLY',
    'VOID','ANALOG','CABAL','MOURNFUL','TOTIENT','ENCRYPT','SHADOWS',
    'DEOR','COMMAND','INTELLIGENCE','INNOCENT','ILLUSION','CERTAINTY',
    'SUFFERING','STRUGGLE','NECESSARY','JOURNEY','PILGRIM',
}

# ── English wordlist (for broad word detection) ─────────────────────────────
ENGLISH_WORDS = set()
wl_path = Path('data/wordlist.txt')
if wl_path.exists():
    for ln in wl_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        w = ln.strip().upper()
        if 3 <= len(w) <= 15:
            ENGLISH_WORDS.add(w)

# ────────────────────────────────────────────────────────────────────────────
# METRICS
# ────────────────────────────────────────────────────────────────────────────

def compute_ioc(indices):
    """Index of Coincidence for a sequence of GP indices."""
    if len(indices) < 2:
        return 0.0
    freq = Counter(indices)
    n = len(indices)
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1)) * M

def decode_page(key, pg):
    """Decode a single page using the key. Returns list of GP indices."""
    start = page_offsets[pg]
    length = page_lengths[pg]
    return [(int(CIPHER[start + i]) - int(key[start + i])) % M for i in range(length)]

def decode_to_text(decoded_indices):
    """Convert GP index list to runeglish text string."""
    return ''.join(IDX_TO[v] for v in decoded_indices)

def decode_words(key, pg):
    """Decode page respecting word boundaries. Returns list of decoded word strings."""
    start = page_offsets[pg]
    result = []
    pos = 0
    for word_tuple in words_per_page.get(pg, []):
        word_dec = []
        for i, cipher_val in enumerate(word_tuple):
            gpos = start + pos + i
            if gpos < N_CIPHER:
                word_dec.append(IDX_TO[(int(CIPHER[gpos]) - int(key[gpos])) % M])
        result.append(''.join(word_dec))
        pos += len(word_tuple)
    return result

def count_noise_patterns(text):
    """Count occurrences of known noise attractor patterns."""
    total = 0
    hits = {}
    for pat in NOISE_PATTERNS:
        c = text.upper().count(pat)
        if c > 0:
            hits[pat] = c
            total += c
    return total, hits

def count_lp_vocab_words(word_list):
    """Count how many decoded words match LP vocabulary."""
    hits = 0
    matched = []
    for w in word_list:
        w_up = w.upper()
        if w_up in LP_VOCAB and len(w_up) >= 2:
            hits += 1
            matched.append(w_up)
    return hits, matched

def count_english_words(word_list):
    """Count how many decoded words are real English (3+ chars)."""
    hits = 0
    matched = []
    for w in word_list:
        w_up = w.upper()
        # Apply GP digraph corrections for matching
        w_corrected = w_up.replace('NG', 'NG').replace('TH', 'TH')
        if w_up in ENGLISH_WORDS and len(w_up) >= 3:
            hits += 1
            matched.append(w_up)
    return hits, matched

def verify_cribs(key):
    """Verify all confirmed cribs still decode correctly."""
    results = []
    for phrase, start in CONFIRMED_CRIBS:
        expected = _gp_encode(phrase)
        actual = [(int(CIPHER[start + i]) - int(key[start + i])) % M for i in range(len(expected))]
        matches = sum(1 for a, b in zip(expected, actual) if a == b)
        results.append({
            'phrase': phrase,
            'position': start,
            'match': f'{matches}/{len(expected)}',
            'perfect': matches == len(expected),
        })
    return results

def verify_singletons(key):
    """Check that all singleton positions decode to I or A."""
    total = len(singleton_positions)
    hits = 0
    for sp in singleton_positions:
        decoded = (int(CIPHER[sp]) - int(key[sp])) % M
        if decoded in (10, 24):  # I or A
            hits += 1
    return hits, total

def verify_ttp(key):
    """Verify TTP consistency: linked positions have same key values."""
    total_violations = 0
    for src_s, dst_s, ln in TTP_CONSTRAINTS:
        for i in range(ln):
            if key[src_s + i] != key[dst_s + i]:
                total_violations += 1
    return total_violations

def assess_false_solve_risk(ioc, noise_count, lp_density, eng_word_ratio, page_length):
    """
    Classify whether a page's decode looks genuine vs false-solve.
    Returns: ('genuine', 'suspicious', 'likely_false', 'noise') + reason.
    """
    # Very short pages are inherently noisy
    if page_length < 80:
        if ioc > 2.0 and noise_count == 0 and eng_word_ratio > 0.3:
            return 'suspicious', 'short page with high metrics — verify manually'
        return 'noise', f'short page ({page_length} runes) — metrics unreliable'

    # Known noise attractor signature
    if noise_count > 10:
        return 'likely_false', f'{noise_count} noise patterns (DPTS/TSUH/etc) — quadgram artifact'

    # Very high IoC but no real words
    if ioc > 2.5 and eng_word_ratio < 0.1:
        return 'likely_false', 'very high IoC but no English words — TH/EA/OE digraph artifact'

    # Good signs: moderate IoC + real words + low noise
    if ioc > 1.5 and eng_word_ratio > 0.2 and noise_count < 3:
        return 'genuine', f'IoC {ioc:.2f}, {eng_word_ratio*100:.0f}% English words, low noise'

    if ioc > 1.3 and lp_density > 0.15:
        return 'suspicious', f'IoC {ioc:.2f}, LP density {lp_density*100:.0f}% — needs manual review'

    return 'noise', f'IoC {ioc:.2f}, underdetermined — keep climbing'

# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────

def run_analysis(export=False):
    # Load checkpoint
    ck_path = Path('data/gpu_hill_checkpoint_gpu1.json')
    if not ck_path.exists():
        print('ERROR: No checkpoint found at data/gpu_hill_checkpoint_gpu1.json')
        return
    ck = json.loads(ck_path.read_text())
    key = np.array(ck['key'], dtype=np.int32)
    step = ck['step']
    score = ck['score']

    print(f'\n{"="*80}')
    print(f'  HILLCLIMB MONITOR v2 — Step {step:,} | Score {score:.1f}')
    print(f'  Checkpoint: {ck_path} ({ck_path.stat().st_mtime:.0f})')
    print(f'{"="*80}\n')

    # ── Global validation ────────────────────────────────────────────────
    crib_results = verify_cribs(key)
    crib_ok = all(c['perfect'] for c in crib_results)
    sing_hits, sing_total = verify_singletons(key)
    ttp_violations = verify_ttp(key)

    print(f'  GLOBAL VALIDATION:')
    print(f'    Cribs: {"ALL OK" if crib_ok else "FAILURES!"} ({sum(1 for c in crib_results if c["perfect"])}/{len(crib_results)})')
    for c in crib_results:
        status = 'OK' if c['perfect'] else 'FAIL'
        print(f'      [{status}] {c["phrase"]} @ {c["position"]} ({c["match"]})')
    print(f'    Singletons: {sing_hits}/{sing_total} ({"OK" if sing_hits == sing_total else "INCOMPLETE"})')
    print(f'    TTP consistency: {ttp_violations} violations ({"OK" if ttp_violations == 0 else "BROKEN!"})')
    print()

    # ── Per-page analysis ────────────────────────────────────────────────
    page_results = []
    total_noise = 0

    print(f'  {"Page":>4} | {"Runes":>5} | {"IoC":>5} | {"LPvoc":>5} | {"EngW":>5} | {"Noise":>5} | {"Status":<16} | Preview')
    print(f'  {"-"*4}-+-{"-"*5}-+-{"-"*5}-+-{"-"*5}-+-{"-"*5}-+-{"-"*5}-+-{"-"*16}-+-{"-"*30}')

    for pg in sorted(page_offsets.keys()):
        decoded = decode_page(key, pg)
        text = decode_to_text(decoded)
        words = decode_words(key, pg)
        n_runes = page_lengths[pg]

        ioc = compute_ioc(decoded)
        noise_count, noise_hits = count_noise_patterns(text)
        total_noise += noise_count
        lp_hits, lp_matched = count_lp_vocab_words(words)
        eng_hits, eng_matched = count_english_words(words)
        n_words = len(words)
        eng_ratio = eng_hits / max(1, n_words)
        lp_char_count = sum(len(w) for w in lp_matched)
        lp_density = lp_char_count / max(1, len(text))

        status, reason = assess_false_solve_risk(ioc, noise_count, lp_density, eng_ratio, n_runes)

        # Preview: first 60 chars of word-separated decode
        preview = ' '.join(words[:12])[:60]

        status_tag = {'genuine': 'GENUINE', 'suspicious': 'SUSPECT',
                      'likely_false': 'FALSE', 'noise': 'unsolved'}[status]

        print(f'  P{pg:02d}  | {n_runes:5d} | {ioc:5.2f} | {lp_hits:5d} | {eng_hits:5d} | {noise_count:5d} | {status_tag:<16} | {preview}')

        page_results.append({
            'page': pg,
            'runes': n_runes,
            'ioc': round(ioc, 4),
            'lp_vocab_hits': lp_hits,
            'lp_vocab_matched': lp_matched[:10],
            'english_word_hits': eng_hits,
            'english_matched': eng_matched[:10],
            'noise_count': noise_count,
            'noise_detail': noise_hits,
            'status': status,
            'reason': reason,
            'words': words[:30],
            'full_text': text,
            'key_segment': list(map(int, key[page_offsets[pg]:page_offsets[pg]+n_runes])),
        })

    print()
    print(f'  SUMMARY:')
    genuine = [p for p in page_results if p['status'] == 'genuine']
    suspect = [p for p in page_results if p['status'] == 'suspicious']
    false_s = [p for p in page_results if p['status'] == 'likely_false']
    print(f'    Genuine: {len(genuine)} pages')
    suspect_names = ', '.join('P' + str(p['page']) for p in suspect)
    print(f'    Suspicious: {len(suspect)} pages ({suspect_names})')
    print(f'    Likely false: {len(false_s)} pages')
    print(f'    Total noise patterns: {total_noise}')

    # ── Noise trend (compare to last run if available) ───────────────────
    prev_path = Path('data/hillclimb_monitor_latest.json')
    if prev_path.exists():
        prev = json.loads(prev_path.read_text())
        prev_step = prev.get('step', 0)
        prev_score = prev.get('score', 0)
        prev_noise = prev.get('total_noise', 0)
        if prev_step < step:
            delta_score = score - prev_score
            delta_noise = total_noise - prev_noise
            delta_steps = step - prev_step
            print(f'\n  TREND (since step {prev_step:,}):')
            print(f'    Score: {prev_score:.1f} -> {score:.1f} ({delta_score:+.1f} over {delta_steps:,} steps)')
            print(f'    Noise: {prev_noise} -> {total_noise} ({delta_noise:+d}) {"(improving!)" if delta_noise < 0 else "(degrading)" if delta_noise > 0 else "(stable)"}')

    # ── Export ───────────────────────────────────────────────────────────
    if export:
        export_data = {
            'step': step,
            'score': score,
            'timestamp': time.time(),
            'crib_results': crib_results,
            'singleton_check': f'{sing_hits}/{sing_total}',
            'ttp_violations': ttp_violations,
            'total_noise': total_noise,
            'pages': page_results,
        }
        out_path = Path('data/hillclimb_monitor_latest.json')
        out_path.write_text(json.dumps(export_data, indent=2, ensure_ascii=False))
        print(f'\n  Exported to {out_path}')

        # Also write per-page solution files for reverse engineering
        sol_dir = Path('data/per_page_solutions')
        sol_dir.mkdir(exist_ok=True)
        for pr in page_results:
            pg = pr['page']
            sol = {
                'page': pg,
                'cipher_mode': 'sub',
                'formula': 'plain = (cipher - key) % 29',
                'step': step,
                'score': score,
                'ioc': pr['ioc'],
                'status': pr['status'],
                'reason': pr['reason'],
                'lp_vocab': pr['lp_vocab_matched'],
                'english_words': pr['english_matched'],
                'noise_count': pr['noise_count'],
                'decoded_words': pr['words'],
                'decoded_text': pr['full_text'],
                'key_segment': pr['key_segment'],
                'key_length': len(pr['key_segment']),
                'reverse_engineer': {
                    'to_decode': f'for i in range(len(cipher)): plain[i] = (cipher[i] - key[i]) % 29',
                    'to_encode': f'for i in range(len(plain)): cipher[i] = (plain[i] + key[i]) % 29',
                    'alphabet': 'F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IO EA',
                    'alphabet_size': 29,
                },
            }
            (sol_dir / f'p{pg:02d}_solution.json').write_text(
                json.dumps(sol, indent=2, ensure_ascii=False))
        print(f'  Per-page solutions written to {sol_dir}/')

    print()


if __name__ == '__main__':
    export = '--export' in sys.argv
    watch = '--watch' in sys.argv

    if watch:
        print('Monitoring mode — Ctrl+C to stop\n')
        last_step = 0
        while True:
            try:
                ck_path = Path('data/gpu_hill_checkpoint_gpu1.json')
                if ck_path.exists():
                    ck = json.loads(ck_path.read_text())
                    cur_step = ck.get('step', 0)
                    if cur_step > last_step:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        run_analysis(export=export)
                        last_step = cur_step
                time.sleep(60)
            except KeyboardInterrupt:
                print('\nStopped.')
                break
            except Exception as e:
                print(f'Error: {e}')
                time.sleep(10)
    else:
        run_analysis(export=export)
