"""
Decode Best Key — Analyzes GPU hillclimber checkpoint keys
==========================================================
Loads the best key from a GPU checkpoint JSON file and:
  1. Decodes the full per-page plaintext
  2. Scores each page separately
  3. Highlights LP-vocabulary matches  
  4. Identifies possible crib anchors

Usage:
  python decode_best_key.py [gpu_id]         # load from checkpoint
  python decode_best_key.py --both           # compare GPU0 vs GPU1

Output: data/decode_best_gpu{N}.txt
"""
import sys, json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

M = 29
IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS','OF',
    'IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER','INSIDE',
    'YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','PARABLE','INSTAR',
    'AND','FOR','BUT','BY','AS','AT','THAT','WHICH','DO','SO','NO','WE',
    'MY','HE','SHE','IT','THEY','HIS','HER','OUR','THEIR','WHO','WHEN',
    'WHERE','WHY','HOW','IF','THEN','ALSO','MORE','MOST','LESS','VERY',
    'AGAIN','BACK','STILL','ONLY','EVEN','BOTH','EACH','SUCH','THOSE',
    'THESE','ANY','MANY','MUCH','LIKE','OVER','INTO','OUT','UP','DOWN'
}

# Known LP phrases for crib-dragging
LP_PHRASES = [
    "SOME WISDOM",
    "THE PRIMES ARE SACRED",
    "ALL THINGS SHOULD BE ENCRYPTED",
    "KNOW THIS",
    "AN INSTRUCTION",
    "PROGRAM YOUR MIND",
    "PROGRAM REALITY",
    "THE LOSS OF DIVINITY",
    "CIRCUMFERENCE",
    "CONSUMPTION",
    "PRESERVATION",
    "ADHERENCE",
    "AMASS GREAT WEALTH",
    "NEVER BECOME ATTACHED",
    "PREPARED TO DESTROY",
    "WELCOME PILGRIM",
    "SEEK TRUTH WITHIN",
    "QUESTION ALL THINGS",
    "DISCOVER TRUTH INSIDE YOURSELF",
    "FOLLOW YOUR TRUTH",
    "IMPOSE NOTHING ON OTHERS",
    "DIVINITY",
    "WISDOM",
    "PROGRAM",
]

LETTER_MAP = {
    'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
    'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
    'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14
}
DIGRAPH_MAP = {'TH':2,'OE':22,'AE':25,'NG':21,'EO':12,'IO':27,'EA':28}

def text_to_gp(txt):
    txt = txt.upper(); res = []; i = 0
    while i < len(txt):
        if i+1 < len(txt) and txt[i:i+2] in DIGRAPH_MAP:
            res.append(DIGRAPH_MAP[txt[i:i+2]]); i += 2
        elif txt[i] in LETTER_MAP:
            res.append(LETTER_MAP[txt[i]]); i += 1
        else:
            i += 1
    return res

def load_page(pg):
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return [], []
    text = path.read_text(encoding='utf-8')
    runes = []; words = []; curr = []
    for ch in text:
        if ch in RUNE_TO_IDX:
            runes.append(RUNE_TO_IDX[ch]); curr.append(RUNE_TO_IDX[ch])
        elif ch in '-. \n\r\t\u2022/' and curr:
            words.append(tuple(curr)); curr = []
    if curr: words.append(tuple(curr))
    return runes, words

def decrypt(cval, kval, mode):
    if mode == 'sub': return (cval - kval) % M
    if mode == 'add': return (cval + kval) % M
    return (kval - cval) % M  # beaufort

def words_to_text(plain_words):
    return ' '.join(''.join(IDX_TO[v] for v in w) for w in plain_words)

def word_score(plain_words):
    score = 0
    for w in plain_words:
        txt = ''.join(IDX_TO[v] for v in w)
        if txt in LP_VOCAB:
            score += len(txt) * 20 + 30
    return score

def analyze_checkpoint(gpu_id):
    ck_path = f'data/gpu_hill_checkpoint_gpu{gpu_id}.json'
    if not Path(ck_path).exists():
        print(f'No checkpoint at {ck_path}')
        return

    ck = json.loads(Path(ck_path).read_text())
    key = ck['key']
    mode = ck['mode']
    step = ck.get('step', '?')
    score = ck.get('score', '?')
    print(f'\n{"="*70}')
    print(f'GPU {gpu_id} checkpoint: mode={mode}, step={step}, score={score}')
    print(f'Key length: {len(key)}, first 20 values: {key[:20]}')
    print(f'{"="*70}')

    # Load all cipher pages
    all_words = []
    page_word_ranges = {}
    cipher_list = []
    for pg in range(21, 55):
        runes, words = load_page(pg)
        start_word = len(all_words)
        all_words.extend(words)
        page_word_ranges[pg] = (start_word, len(all_words))
        cipher_list.extend(runes)

    N = len(cipher_list)
    print(f'Total runes: {N}, words: {len(all_words)}')

    # Decode entire cipher with key
    ki = 0
    plain_words = []
    for w in all_words:
        dec = []
        for c in w:
            dec.append(decrypt(c, key[ki % len(key)], mode))
            ki += 1
        plain_words.append(tuple(dec))

    # Per-page analysis
    outlines = []
    total_ws = 0
    total_sing = 0
    total_sing_ok = 0

    for pg in range(21, 55):
        start_w, end_w = page_word_ranges[pg]
        page_words = plain_words[start_w:end_w]
        ws = word_score(page_words)
        total_ws += ws

        # Singleton check
        sing_ok = sum(1 for w in page_words if len(w) == 1 and w[0] in (10, 24))
        sing_total = sum(1 for w in page_words if len(w) == 1)
        total_sing += sing_total
        total_sing_ok += sing_ok

        text = words_to_text(page_words)
        # Highlight LP vocab words
        highlighted = []
        for w in page_words:
            t = ''.join(IDX_TO[v] for v in w)
            highlighted.append(f'[{t}]' if t in LP_VOCAB else t)
        htext = ' '.join(highlighted)

        sep = '***' if ws >= 200 or sing_ok == sing_total else '---'
        page_line = (f'P{pg:02d} | mode={mode} | WordScore={ws} | '
                     f'Singletons={sing_ok}/{sing_total} | {sep}\n'
                     f'  {text[:200]}\n'
                     f'  HIGHLIGHTED: {htext[:200]}')
        outlines.append(page_line)
        print(page_line)

    print(f'\nTOTAL WORDSCORE: {total_ws}  |  SINGLETONS: {total_sing_ok}/{total_sing}')

    # ── Crib dragging analysis ──
    print(f'\n{"─"*70}')
    print('CRIB DRAGGING (looking for LP phrases at all positions)')
    print(f'{"─"*70}')

    # Build rune-position map
    rune_positions = []
    word_of_rune = []
    ki = 0
    for wi, w in enumerate(all_words):
        for c in w:
            rune_positions.append(c)
            word_of_rune.append(wi)
            ki += 1

    crib_hits = []
    for phrase in LP_PHRASES:
        gp_phrase = text_to_gp(phrase)
        n = len(gp_phrase)
        if n < 2: continue
        best_score = 0
        best_pos = -1
        for pos in range(0, N - n + 1):
            # What would the key be at this position to produce this phrase?
            crib_key = [(gp_phrase[j] + rune_positions[pos+j]) % M if mode == 'beaufort'
                        else (rune_positions[pos+j] - gp_phrase[j]) % M if mode == 'sub'
                        else (gp_phrase[j] - rune_positions[pos+j]) % M
                        for j in range(n)]
            # Compare with actual key at those positions
            actual_key = [key[(pos+j) % len(key)] for j in range(n)]
            matches = sum(1 for a, b in zip(crib_key, actual_key) if a == b)
            if matches > best_score:
                best_score = matches
                best_pos = pos

        if best_score >= n * 0.5:  # at least 50% match
            pg_est = [pg for pg, (sw, ew) in page_word_ranges.items() 
                      if sw <= word_of_rune[min(best_pos, N-1)] < ew]
            pg_str = f'P{pg_est[0]:02d}' if pg_est else '?'
            crib_hits.append((best_score, n, phrase, best_pos, pg_str))
            print(f'  Crib "{phrase}" ({n} runes): {best_score}/{n} key matches at pos={best_pos} ({pg_str})')

    # ── Save output ──
    out_file = f'data/decode_best_gpu{gpu_id}.txt'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(f'GPU {gpu_id} Checkpoint Decode\n')
        f.write(f'Mode: {mode} | Step: {step} | Score: {score}\n')
        f.write(f'Key: {key[:50]}...\n')
        f.write('='*70 + '\n\n')
        for line in outlines:
            f.write(line + '\n\n')
        f.write(f'\nTOTAL WORDSCORE: {total_ws}  SINGLETONS: {total_sing_ok}/{total_sing}\n')
        if crib_hits:
            f.write('\nCRIB HITS:\n')
            for sc, n, ph, pos, pg in sorted(crib_hits, reverse=True):
                f.write(f'  {ph!r} ({n} runes): {sc}/{n} matches at pos={pos} ({pg})\n')
    print(f'\nFull decode saved to {out_file}')
    return crib_hits

if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else '1'
    if arg == '--both':
        analyze_checkpoint(0)
        analyze_checkpoint(1)
    else:
        analyze_checkpoint(int(arg))
