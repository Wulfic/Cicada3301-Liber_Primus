"""
Test LP1 (pages 0-20 + other solved pages) as a running key for P21-54.
Hypothesis: plain = (cipher - LP1_runes[offset + i]) % 29 for each position i.
Tests all feasible offsets and scores LP vocabulary.
"""
import sys
from pathlib import Path
from collections import Counter

RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

IDX_TO = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA']
M = 29

LP_VOCAB = {
    'AN','INSTRUCTION','SOME','WISDOM','THE','PRIMES','ARE','SACRED','ALL',
    'THINGS','SHOULD','BE','ENCRYPTED','KNOW','THIS','WARNING','WELCOME',
    'PILGRIM','LOSS','DIVINITY','CIRCUMFERENCE','PRACTICES','THREE',
    'BEHAVIORS','CAUSE','CONSUMPTION','PRESERVATION','ADHERENCE','AMASS',
    'GREAT','WEALTH','NEVER','BECOME','ATTACHED','TO','WHAT','YOU','OWN',
    'PREPARED','DESTROY','PROGRAM','YOUR','MIND','REALITY','SEEK','TRUTH',
    'WITHIN','HOLY','BEING','EACH','FOLLOW','END','EMERGE','WILL','EVERY',
    'DEEP','ABOVE','SAME','OTHER','ONE','DIVINE','FROM','A','I','IS',
    'OF','IN','NOT','WITH','HAVE','SELF','PATH','QUESTION','DISCOVER',
    'INSIDE','YOURSELF','IMPOSE','NOTHING','OTHERS','CHAPTER','INTUS',
    'PARABLE','INSTAR','BUTTERFLY','SHADOW','FORM','AND','FOR','BUT','BY',
    'AS','AT','THAT','WHICH','CAUSE','BEGINNING','JOURNEY','LIGHT','DARK',
    'WORLD','SOUL','HIDDEN','OPEN','TRUE','FALSE','BODY','EYES','HEART',
    'MIND','SPIRIT','VOICE','WORDS','LANGUAGE','NUMBER','PRIME','CYCLE',
    'IF','THEN','THOSE','THEIR','THEM','THEY','WHO','WHAT','WHERE','WHEN',
}

def load_runes(pages):
    runes = []
    for pg in pages:
        p = Path(f'pages/page_{pg:02d}/runes.txt')
        if p.exists():
            for ch in p.read_text(encoding='utf-8'):
                if ch in RUNE_TO_IDX:
                    runes.append(RUNE_TO_IDX[ch])
    return runes

def load_words(pages):
    """Load runes with word boundaries preserved."""
    words = []
    for pg in pages:
        p = Path(f'pages/page_{pg:02d}/runes.txt')
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        curr = []
        for ch in text:
            if ch in RUNE_TO_IDX:
                curr.append(RUNE_TO_IDX[ch])
            elif ch in '-. \n\r\t\u2022/' and curr:
                words.append(tuple(curr))
                curr = []
        if curr:
            words.append(tuple(curr))
    return words

print("Loading cipher (P21-P54)...")
cipher = load_runes(range(21, 55))
cipher_words = load_words(range(21, 55))
print(f"  Cipher: {len(cipher)} runes, {len(cipher_words)} words")

print("Loading LP1 key material (pages 0-20 + solved pages 55-74)...")
solved_pages = list(range(0, 21)) + [55,56,57,58,59,60,61,62,63,64,67,68,71,72,73,74]
key_runes = load_runes(solved_pages)
print(f"  Key material: {len(key_runes)} runes")

# Build word start positions for cipher
word_starts = []
pos = 0
for w in cipher_words:
    word_starts.append(pos)
    pos += len(w)
word_ends = [s + len(w) for s, w in zip(word_starts, cipher_words)]

def decode_at_offset(offset, use_wrap=False):
    """Decode cipher using key_runes starting at offset.
    If use_wrap=True, wraps key when exhausted.
    Returns (word_score, words_matched, first_100_chars).
    """
    key_len = len(key_runes)
    plain = []
    for i, c in enumerate(cipher):
        ki = offset + i
        if use_wrap:
            ki = ki % key_len
        if ki >= key_len:
            plain.append(-1)  # no key at this position
        else:
            plain.append((c - key_runes[ki]) % M)
    
    # Score words
    word_score = 0
    words_matched = []
    pos = 0
    for w in cipher_words:
        w_plain = plain[pos:pos+len(w)]
        if -1 not in w_plain:
            txt = ''.join(IDX_TO[v] for v in w_plain)
            if txt in LP_VOCAB:
                word_score += len(txt) * 10 + 30
                words_matched.append(txt)
        pos += len(w)
    
    # First 100 decoded chars
    first150 = ''.join(IDX_TO[v] for v in plain[:150] if v != -1)
    coverage = sum(1 for v in plain if v != -1)
    return word_score, words_matched, first150, coverage

print("\n=== Testing LP1 as running key (no wrap) ===")
print("Trying offsets 0 to (LP1_len - cipher_len) and some wrapping variants...\n")

best_score = 0
best_offset = -1
best_wrap = False
results = []

# Test without wrapping: offsets where LP1 covers at least cipher_len positions
max_no_wrap_offset = len(key_runes) - len(cipher)
print(f"Max no-wrap offset: {max_no_wrap_offset} (negative means LP1 too short)")
if max_no_wrap_offset < 0:
    print(f"LP1 ({len(key_runes)}) shorter than cipher ({len(cipher)}) — no-wrap only possible at offset 0 for partial coverage")

# Test offset 0 no-wrap (partial coverage)
score, matched, first150, coverage = decode_at_offset(0, use_wrap=False)
print(f"Offset=0, no-wrap: WordScore={score}, coverage={coverage}/{len(cipher)}, matched={matched[:15]}")
print(f"  First 150: {first150}")
print()
results.append((score, 0, False, coverage))

# Test offset 0 with wrapping
score, matched, first150, coverage = decode_at_offset(0, use_wrap=True)
print(f"Offset=0, wrap: WordScore={score}, coverage={coverage}/{len(cipher)}, matched={matched[:15]}")
print(f"  First 150: {first150}")
print()
results.append((score, 0, True, coverage))

# Test various offsets with wrapping
print("=== Testing various offsets with wrapping ===")
for offset in range(0, min(len(key_runes), 500), 10):
    score, matched, first150, coverage = decode_at_offset(offset, use_wrap=True)
    results.append((score, offset, True, coverage))
    if score > best_score:
        best_score = score
        best_offset = offset
        best_wrap = True

# Also scan page-by-page offsets (each solved page start)
print("\n=== Testing offsets at each solved page start ===")
pos = 0
page_offsets_solved = {}
for pg in solved_pages:
    page_offsets_solved[pg] = pos
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if p.exists():
        cnt = sum(1 for ch in p.read_text(encoding='utf-8') if ch in RUNE_TO_IDX)
        pos += cnt

for pg, pg_offset in list(page_offsets_solved.items())[:20]:
    score, matched, first150, coverage = decode_at_offset(pg_offset, use_wrap=True)
    results.append((score, pg_offset, True, coverage))
    if score > best_score:
        best_score = score
        best_offset = pg_offset
        best_wrap = True

# Sort by score descending
results.sort(key=lambda x: -x[0])
print("\n=== Top 20 results ===")
for score, offset, wrap, cov in results[:20]:
    print(f"  offset={offset:5d}, wrap={wrap}, WordScore={score}, coverage={cov}")

# Full decode of best result
print(f"\n=== Best: offset={best_offset}, wrap={best_wrap}, score={best_score} ===")
score, matched, first150, coverage = decode_at_offset(best_offset, use_wrap=best_wrap)
print(f"Matched words: {matched[:30]}")
print(f"First 150 chars: {first150}")

# Print per-page decode for best result
print(f"\n=== Per-page decode (best offset={best_offset}, wrap={best_wrap}) ===")
key_len = len(key_runes)
pos = 0
page_starts_cipher = {}
cum_pos = 0
for pg in range(21, 55):
    page_starts_cipher[pg] = cum_pos
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if p.exists():
        cnt = sum(1 for ch in p.read_text(encoding='utf-8') if ch in RUNE_TO_IDX)
        cum_pos += cnt

for pg in range(21, 55):
    pg_start = page_starts_cipher[pg]
    p = Path(f'pages/page_{pg:02d}/runes.txt')
    if not p.exists():
        continue
    page_cipher = [cipher[pg_start + i] for i in range(sum(1 for ch in p.read_text(encoding='utf-8') if ch in RUNE_TO_IDX))]
    plain_page = []
    for i, c in enumerate(page_cipher):
        ki = (best_offset + pg_start + i) % key_len if best_wrap else best_offset + pg_start + i
        if not best_wrap and ki >= key_len:
            plain_page.append('?')
        else:
            plain_page.append(IDX_TO[(c - key_runes[ki]) % M])
    decoded = ''.join(plain_page)[:80]
    # count LP vocab hits
    words_in_page = []
    pp = pg_start
    for w in cipher_words:
        if pp >= pg_start and pp < pg_start + len(page_cipher):
            wp = [(cipher[pp+j] - key_runes[((best_offset + pp + j) % key_len if best_wrap else best_offset+pp+j)]) % M 
                   for j in range(len(w)) 
                   if (best_wrap or (best_offset+pp+j < key_len))]
            if len(wp) == len(w):
                txt = ''.join(IDX_TO[v] for v in wp)
                if txt in LP_VOCAB:
                    words_in_page.append(txt)
        pp += len(w)
        if pp >= pg_start + len(page_cipher):
            break
    print(f"P{pg:02d}: {decoded} | vocab={words_in_page[:8]}")
