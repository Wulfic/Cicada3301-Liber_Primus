"""
Key Pattern Analysis — extract key values at perfect-crib positions,
check for repeating key structure, and propagate via TTP constraints.

Perfect crib matches from GPU0 sub mode checkpoint:
  CONSUMPTION  (pos=31,  score 10/10)
  PRESERVATION (pos=2093, 11/11)
  ADHERENCE    (pos=8532,  9/9)
  SOME WISDOM  (pos=4131, 10/10)
  DIVINITY     (pos=1356,  8/8)
  KNOW THIS    (pos=476,   7/7)
  PROGRAM      (pos=599,   7/7)
  WISDOM       (pos=4135,  6/6)
"""

import json, sys
from pathlib import Path

# ─────────────────────────────────────────────
# Gematria Primus: letter → rune index (0‑28)
# ─────────────────────────────────────────────
RW = "FUTHORCGWHNIJEOPSTBLMNGDAEYI*X"   # won't use this directly
LP_MAP = {
    'F':0,'U':1,'TH':2,'O':3,'R':4,'C':5,'K':5,'G':6,'W':7,'H':8,
    'N':9,'I':10,'J':11,'Y':26,'EO':12,'P':13,'X':14,'Z':14,'S':15,
    'T':16,'B':17,'E':18,'M':19,'L':20,'NG':21,'ING':21,'OE':22,
    'D':23,'A':24,'AE':25,'IO':27,'IA':27,'EA':28,' ':29,
    'V':1,   # V→U in LP
    'Q':5,   # Q→C/K
}
INDEX_TO_LETTER = {v: k for k, v in LP_MAP.items() if k not in ('K','Z','ING','IA','V','Q')}

def encode(word: str) -> list[int]:
    """Encode a word string to LP rune indices using digraph rules (longest match first)."""
    runes = []
    i = 0
    w = word.upper()
    while i < len(w):
        if w[i] == ' ':
            i += 1; continue
        # Try trigraph first
        if i+2 < len(w) and w[i:i+3] in LP_MAP:
            runes.append(LP_MAP[w[i:i+3]]); i += 3
        # Try digraph
        elif i+1 < len(w) and w[i:i+2] in LP_MAP:
            runes.append(LP_MAP[w[i:i+2]]); i += 2
        elif w[i] in LP_MAP:
            runes.append(LP_MAP[w[i]]); i += 1
        else:
            print(f"WARNING: char '{w[i]}' not in LP_MAP (pos={i}, word={word})")
            i += 1
    return runes

CRIBS = [
    ("CONSUMPTION",   31),
    ("SOME WISDOM", 4131),
    ("KNOW THIS",    476),
    ("PROGRAM",      599),
    ("DIVINITY",    1356),
    ("PRESERVATION",2093),
    ("THE LOSS OF DIVINITY", 4325),
    ("ADHERENCE",   8532),
]

# ─────────────────────────────────────────────
# TTP constraints (same as hillclimber)
# ─────────────────────────────────────────────
TTP_CONSTRAINTS = [
    (3001,  9727, 1312),
    (6298, 12311, 1468),
    (   0,  5803,  404),
    (2736,  8643,  265),
    ( 737,  8100,  172),
    ( 910,  8273,   97),
]

def build_link_map(n):
    lm = list(range(n))
    for src, dst, ln in TTP_CONSTRAINTS:
        for i in range(ln):
            lm[dst + i] = lm[src + i]
    return lm

# ─────────────────────────────────────────────
# Load checkpoint key
# ─────────────────────────────────────────────
ckpt_path = Path("data/gpu_hill_checkpoint_gpu0.json")
with open(ckpt_path) as f:
    ckpt = json.load(f)

mode   = ckpt["mode"]
step   = ckpt["step"]
score  = ckpt["score"]
key    = ckpt["key"]    # list of 14529 ints (0-28)
N      = len(key)
LINK   = build_link_map(N)

print(f"Checkpoint: mode={mode}, step={step:,}, score={score:.1f}, N={N}")
print()

# ─────────────────────────────────────────────
# Load cipher text — same method as hillclimber
# (pages 21-54 from pages/page_XX/runes.txt)
# ─────────────────────────────────────────────
RUNE_TO_IDX = {chr(k): v for k, v in [
    (0x16A0,0),(0x16A2,1),(0x16A6,2),(0x16A9,3),(0x16B1,4),(0x16B3,5),
    (0x16B7,6),(0x16B9,7),(0x16BB,8),(0x16BE,9),(0x16C1,10),(0x16C4,11),
    (0x16C7,12),(0x16C8,13),(0x16C9,14),(0x16CB,15),(0x16CF,16),(0x16D2,17),
    (0x16D6,18),(0x16D7,19),(0x16DA,20),(0x16DD,21),(0x16DF,22),(0x16DE,23),
    (0x16AA,24),(0x16AB,25),(0x16A3,26),(0x16E1,27),(0x16E0,28)]}

def load_page(pg):
    from pathlib import Path
    path = Path(f'pages/page_{pg:02d}/runes.txt')
    if not path.exists(): return []
    text = path.read_text(encoding='utf-8')
    return [RUNE_TO_IDX[c] for c in text if c in RUNE_TO_IDX]

cipher = []
page_offsets = {}
for pg in range(21, 55):
    page_offsets[pg] = len(cipher)
    cipher.extend(load_page(pg))

print(f"Cipher length: {len(cipher)} runes (first 10: {cipher[:10]})")
print(f"Page offsets (21-30): { {k:v for k,v in list(page_offsets.items())[:10]} }")
print()

# ─────────────────────────────────────────────
# Decode function (sub mode: plain = (cipher-key)%29)
# ─────────────────────────────────────────────
M = 29
def decode_sub(c_val, k_val):
    return (c_val - k_val) % M

# ─────────────────────────────────────────────
# For each crib, show key values, implied key,
# and surrounding plaintext context
# ─────────────────────────────────────────────
all_anchors = {}  # pos → key_value (confirmed)

print("=" * 70)
print("CRIB ANALYSIS")
print("=" * 70)

for phrase, start_pos in CRIBS:
    plain_runes = encode(phrase)
    L = len(plain_runes)
    
    # Key implied by this crib (if sub mode is correct):
    # key[pos+i] = (cipher[pos+i] - plain[i]) % M
    implied_key = [(cipher[start_pos + i] - plain_runes[i]) % M
                   for i in range(L) if start_pos + i < len(cipher) and start_pos+i < N]
    
    # Actual key from checkpoint
    actual_key  = [key[start_pos + i] for i in range(len(implied_key))]
    
    # Match count
    matches = sum(1 for a,b in zip(implied_key, actual_key) if a == b)
    
    print(f"\nCRIB: '{phrase}' at pos={start_pos}")
    print(f"  Plain runes  : {plain_runes}")
    print(f"  Cipher runes : {cipher[start_pos:start_pos+L]}")
    print(f"  Implied key  : {implied_key}")
    print(f"  Actual  key  : {actual_key}")
    print(f"  Matches: {matches}/{len(implied_key)}")
    
    if matches == len(implied_key):
        print(f"  *** PERFECT MATCH — anchoring {L} key positions ***")
        for i, k_val in enumerate(implied_key):
            p = start_pos + i
            canon = LINK[p]
            all_anchors[canon] = k_val
    
    # Decode ±10 runes around this position for context
    ctx_start = max(0, start_pos - 5)
    ctx_end   = min(N, start_pos + L + 5)
    ctx_plain = [decode_sub(cipher[p], key[p]) for p in range(ctx_start, ctx_end)]
    ctx_str   = "".join(INDEX_TO_LETTER.get(v, f"[{v}]") for v in ctx_plain)
    print(f"  Context (pos {ctx_start}‥{ctx_end}): {ctx_str}")

print()
print("=" * 70)
print(f"TOTAL ANCHORED KEY POSITIONS: {len(all_anchors)}")
print(f"  (After TTP propagation — canonical positions)")
print()

# ─────────────────────────────────────────────
# Key frequency analysis: what are the key values
# at anchored positions?
# ─────────────────────────────────────────────
from collections import Counter
anchor_values = list(all_anchors.values())
freq = Counter(anchor_values)
print("Key value frequency at anchored positions:")
for val, cnt in sorted(freq.items(), key=lambda x:-x[1]):
    ltr = INDEX_TO_LETTER.get(val, f"[{val}]")
    print(f"  {val:2d} ({ltr:3s}) : {'#'*cnt} ({cnt})")

print()

# ─────────────────────────────────────────────
# Check for periodicity in the key
# Look at key differences (delta) across anchors
# ─────────────────────────────────────────────
print("=" * 70)
print("KEY DELTA ANALYSIS (looking for repeating period)")
print("=" * 70)

sorted_anchors = sorted(all_anchors.items())  # (pos, key_val)
print(f"\nAnchored positions and key values:")
for pos, kv in sorted_anchors:
    ltr = INDEX_TO_LETTER.get(kv, f"[{kv}]")
    print(f"  pos={pos:5d}  key={kv:2d} ({ltr})")

# Check GCDs of differences between anchor positions
from math import gcd
positions = [p for p, _ in sorted_anchors]
diffs = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
if diffs:
    g = diffs[0]
    for d in diffs[1:]:
        g = gcd(g, d)
    print(f"\nGCD of inter-anchor position gaps: {g}")
    print(f"  Gaps: {diffs}")
    print(f"  This suggests candidate key period: {g} (or multiples)")

print()

# ─────────────────────────────────────────────
# Try to identify key period by autocorrelation
# of the full key array
# ─────────────────────────────────────────────
print("=" * 70)
print("KEY AUTOCORRELATION (top match periods 2 to 500)")
print("=" * 70)

key_arr = key[:N]
best_periods = []
for period in range(2, 501):
    matches = sum(1 for i in range(N - period)
                  if key_arr[i] == key_arr[i + period])
    expected_random = (N - period) / M
    ratio = matches / expected_random
    best_periods.append((ratio, period, matches))

best_periods.sort(reverse=True)
print("Top 20 candidate periods (ratio vs random):")
for ratio, period, matches in best_periods[:20]:
    print(f"  period={period:4d}  matches={matches:6d}  ratio={ratio:.3f}")

print()

# ─────────────────────────────────────────────
# For the best period, extract the repeating key
# ─────────────────────────────────────────────
best_ratio, best_period, _ = best_periods[0]
if best_ratio > 1.5:
    print(f"Significant periodicity found at period={best_period} (ratio={best_ratio:.3f})")
    # Extract key at multiples of best_period
    key_word = []
    for offset in range(best_period):
        vals = [key_arr[offset + k*best_period] for k in range(N // best_period)]
        most_common = Counter(vals).most_common(1)[0][0]
        ltr = INDEX_TO_LETTER.get(most_common, f"[{most_common}]")
        key_word.append(ltr)
    print(f"Repeating key word candidate: {''.join(key_word)}")
else:
    print(f"No strong periodicity found (best ratio={best_ratio:.3f} at period={best_period})")
    print("Key may be a running key (one-time-pad-like) rather than repeating")

# ─────────────────────────────────────────────
# Save anchored key to a file for further use
# ─────────────────────────────────────────────
anchor_out = {"mode": mode, "anchors": {str(k): v for k, v in all_anchors.items()},
              "total_anchors": len(all_anchors)}
import json
with open("data/key_anchors.json", "w") as f:
    json.dump(anchor_out, f, indent=2)
print(f"\nAnchors saved to data/key_anchors.json")
