"""
P20 Non-Prime Runes Transposition Solver.

The 646 non-prime-position runes from P20, after Caesar shift 16, have IoC ~2.01
(matching English frequency distribution). This means they contain English-like text
that has been permuted. We need to find the correct transposition.

646 = 2 × 17 × 19

This script tries:
1. All rectangular grid transpositions (fill row→read col, fill col→read row)
2. Rail fence at various depths
3. Reverse
4. Common permutation patterns
5. Score by bigram/trigram frequency and word detection
"""

import os, sys, math
from collections import Counter
from itertools import product

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

# === GP Mapping ===
GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LATIN = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
           'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

# Common English words in runeglish notation (for scoring)
COMMON_WORDS = set([
    'THE', 'AND', 'THAT', 'THIS', 'WITH', 'FROM', 'HAVE', 'THEY',
    'WHICH', 'THEIR', 'WILL', 'EACH', 'ALL', 'ARE', 'NOT', 'BUT',
    'YOU', 'FOR', 'WAS', 'HIS', 'HER', 'HAS', 'ONE', 'WHO', 'OUR',
    'OUT', 'WHEN', 'WHAT', 'THERE', 'BEEN', 'THEM', 'THAN', 'ITS',
    'INTO', 'ONLY', 'MAY', 'SELF', 'TRUTH', 'SACRED', 'WISDOM',
    'AN', 'IN', 'IS', 'IT', 'OF', 'OR', 'TO', 'WE', 'BE', 'DO',
    # OE words commonly seen in Cicada
    'EODE', 'SEFA', 'BURG', 'FOLC', 'DYRE', 'HLAFORD', 'FELA',
    'WEAN', 'SECG', 'MONN', 'FOLGAD', 'SCOP', 'NOMA',
    # Cicada-specific
    'DIVINITY', 'CIRCUMFERENCE', 'INSTRUCTION', 'PARABLE', 'KOAN',
    'PILGRIM', 'INSTAR', 'PRIMES', 'TOTIENT', 'ENCRYPTED',
])

def word_score(text):
    """Count number of common English words found in text"""
    count = 0
    text_upper = text.upper()
    for word in COMMON_WORDS:
        if word in text_upper:
            count += len(word)  # Weight by word length
    return count

def bigram_score(values):
    """Score based on common English bigram patterns in GP values"""
    # Common bigrams in runeglish: TH(2)-E(18), A(24)-N(9), I(10)-N(9), etc.
    common_bigrams = {
        (2, 18): 10,   # TH-E
        (24, 9): 8,    # A-N  
        (10, 9): 8,    # I-N
        (18, 4): 7,    # E-R
        (3, 0): 6,     # O-F
        (10, 15): 6,   # I-S
        (16, 3): 6,    # T-O
        (9, 3): 6,     # N-O
        (24, 16): 6,   # A-T
        (28, 4): 5,    # EA-R  
        (24, 20): 5,   # A-L
        (8, 18): 5,    # H-E
        (0, 3): 5,     # F-O
        (9, 23): 5,    # N-D
        (18, 23): 5,   # E-D
        (18, 15): 5,   # E-S
        (4, 18): 5,    # R-E
        (2, 24): 5,    # TH-A
        (7, 10): 4,    # W-I
        (15, 2): 4,    # S-TH
    }
    score = 0
    for i in range(len(values)-1):
        bg = (values[i], values[i+1])
        if bg in common_bigrams:
            score += common_bigrams[bg]
    return score

# === Load P20 ===
p20 = load_page(20)
print(f"P20 total runes: {len(p20)}")

# Identify prime positions
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n % i == 0: return False
    return True

prime_positions = [i for i in range(len(p20)) if is_prime(i)]
non_prime_positions = [i for i in range(len(p20)) if not is_prime(i)]

print(f"Prime positions: {len(prime_positions)}")
print(f"Non-prime positions: {len(non_prime_positions)}")

# Extract non-prime runes
non_prime_runes = [p20[i] for i in non_prime_positions]
print(f"Non-prime rune count: {len(non_prime_runes)}")
print(f"Non-prime IoC: {ioc(non_prime_runes):.4f}")

# Apply Caesar shift 16
shifted = [(v - 16) % 29 for v in non_prime_runes]
print(f"After shift 16 IoC: {ioc(shifted):.4f}")
shifted_text = to_english(shifted)
print(f"Shifted text first 100: {shifted_text[:100]}")

# Check factorization
n = len(shifted)
print(f"\n{n} = ", end="")
temp = n
factors = []
for p in range(2, int(temp**0.5)+1):
    while temp % p == 0:
        factors.append(p)
        temp //= p
if temp > 1:
    factors.append(temp)
print(" × ".join(str(f) for f in factors))

# Find all divisor pairs
divisors = []
for d in range(1, n+1):
    if n % d == 0:
        divisors.append(d)
print(f"Divisors of {n}: {divisors}")

# === Transposition Methods ===

def transpose_row_to_col(data, rows, cols):
    """Fill row-by-row, read column-by-column"""
    result = []
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            if idx < len(data):
                result.append(data[idx])
    return result

def transpose_col_to_row(data, rows, cols):
    """Fill column-by-column, read row-by-row"""
    result = []
    for r in range(rows):
        for c in range(cols):
            idx = c * rows + r
            if idx < len(data):
                result.append(data[idx])
    return result

def rail_fence_decrypt(data, rails):
    """Decrypt rail fence cipher"""
    n = len(data)
    if rails <= 1 or rails >= n:
        return data
    
    # Calculate the length of each rail
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    rail_pattern = []
    for i in range(n):
        rail_pattern.append(rail)
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction = -direction
    
    # Calculate lengths
    rail_lengths = Counter(rail_pattern)
    
    # Fill rails from data
    pos = 0
    rail_data = {}
    for r in range(rails):
        rail_data[r] = list(data[pos:pos+rail_lengths[r]])
        pos += rail_lengths[r]
    
    # Read back
    result = []
    rail_indices = {r: 0 for r in range(rails)}
    for i in range(n):
        r = rail_pattern[i]
        if rail_indices[r] < len(rail_data[r]):
            result.append(rail_data[r][rail_indices[r]])
            rail_indices[r] += 1
    
    return result

def spiral_read(data, rows, cols):
    """Read in spiral order (outside→inside)"""
    if rows * cols != len(data):
        return data
    
    # Fill grid
    grid = []
    for r in range(rows):
        grid.append(data[r*cols:(r+1)*cols])
    
    result = []
    top, bottom, left, right = 0, rows-1, 0, cols-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            result.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                result.append(grid[r][left])
            left += 1
    return result

def diagonal_read(data, rows, cols):
    """Read diagonals from top-left"""
    if rows * cols != len(data):
        return data
    grid = []
    for r in range(rows):
        grid.append(data[r*cols:(r+1)*cols])
    
    result = []
    for d in range(rows + cols - 1):
        for r in range(max(0, d-cols+1), min(rows, d+1)):
            c = d - r
            if 0 <= c < cols:
                result.append(grid[r][c])
    return result

# === MAIN SEARCH ===

print("\n" + "="*80)
print("TRANSPOSITION SEARCH ON SHIFT-16 NON-PRIME RUNES")
print("="*80)

results = []

# Try all grid sizes
for rows in divisors:
    cols = n // rows
    if cols < 2 or rows < 2:
        continue
    
    # Row-to-col
    trans = transpose_row_to_col(shifted, rows, cols)
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 0 or ws > 0:
        results.append((bg + ws*2, f"ROW→COL {rows}x{cols}", text[:80], ioc(trans)))
    
    # Col-to-row
    trans = transpose_col_to_row(shifted, rows, cols)
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 0 or ws > 0:
        results.append((bg + ws*2, f"COL→ROW {rows}x{cols}", text[:80], ioc(trans)))
    
    # Spiral
    trans = spiral_read(shifted, rows, cols)
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 0 or ws > 0:
        results.append((bg + ws*2, f"SPIRAL {rows}x{cols}", text[:80], ioc(trans)))
    
    # Diagonal
    trans = diagonal_read(shifted, rows, cols)
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 0 or ws > 0:
        results.append((bg + ws*2, f"DIAGONAL {rows}x{cols}", text[:80], ioc(trans)))

# Rail fence
for rails in range(2, 30):
    trans = rail_fence_decrypt(shifted, rails)
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 0 or ws > 0:
        results.append((bg + ws*2, f"RAILFENCE {rails}", text[:80], ioc(trans)))

# Reverse
trans = list(reversed(shifted))
text = to_english(trans)
bg = bigram_score(trans)
ws = word_score(text)
results.append((bg + ws*2, f"REVERSE", text[:80], ioc(trans)))

# Try NON-exact grid sizes too (with padding)
for rows in range(2, 50):
    cols = math.ceil(n / rows)
    if rows * cols == n:
        continue  # Already handled
    
    # Pad with 0s
    padded = shifted + [0] * (rows * cols - n)
    
    trans = transpose_row_to_col(padded, rows, cols)[:n]
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 50 or ws > 20:
        results.append((bg + ws*2, f"ROW→COL {rows}x{cols}(pad)", text[:80], ioc(trans)))
    
    trans = transpose_col_to_row(padded, rows, cols)[:n]
    text = to_english(trans)
    bg = bigram_score(trans)
    ws = word_score(text)
    if bg > 50 or ws > 20:
        results.append((bg + ws*2, f"COL→ROW {rows}x{cols}(pad)", text[:80], ioc(trans)))

# Sort by score
results.sort(key=lambda x: -x[0])

print(f"\nTop 30 results (by combined bigram + word score):")
for score, desc, text, ic in results[:30]:
    print(f"\n  Score={score:4d} IoC={ic:.4f} {desc}")
    print(f"    {text}")

# === ALSO: Check ALL shift values (not just 16) with transpositions ===
print("\n" + "="*80)
print("ALL SHIFTS + TRANSPOSITIONS (quick scan)")
print("="*80)

for shift in range(29):
    shifted_s = [(v - shift) % 29 for v in non_prime_runes]
    ic = ioc(shifted_s)
    if ic > 1.5:
        print(f"  Shift {shift:2d}: IoC={ic:.4f}")
        
        # Quick transposition check with key grids
        for rows, cols in [(2, n//2), (17,38), (19,34), (34,19), (38,17)]:
            if rows * cols != n:
                continue
            trans = transpose_row_to_col(shifted_s, rows, cols)
            text = to_english(trans)
            ws = word_score(text)
            bg = bigram_score(trans)
            if ws > 10 or bg > 50:
                print(f"    ROW→COL {rows}x{cols}: ws={ws} bg={bg} | {text[:60]}")
            
            trans = transpose_col_to_row(shifted_s, rows, cols)
            text = to_english(trans)
            ws = word_score(text)
            bg = bigram_score(trans)
            if ws > 10 or bg > 50:
                print(f"    COL→ROW {rows}x{cols}: ws={ws} bg={bg} | {text[:60]}")

# === Also: Check if NON-PRIME runes need DIFFERENT cipher (Beaufort with Deor?) ===
print("\n" + "="*80)
print("NON-PRIME RUNES with BEAUFORT(Deor) at various offsets")
print("="*80)

# Load Deor poem OE tokens
def tokenize_oe_text(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if text[i] == 'Þ' or text[i] == 'Ð':
            values.append(2); i += 1
        elif text[i] == 'Æ':
            values.append(25); i += 1
        elif i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                values.append(2); i += 2
            elif digraph == 'NG':
                values.append(21); i += 2
            elif digraph == 'OE':
                values.append(22); i += 2
            elif digraph == 'AE':
                values.append(25); i += 2
            elif digraph in ('IA', 'IO'):
                values.append(27); i += 2
            elif digraph == 'EA':
                values.append(28); i += 2
            elif digraph == 'EO':
                values.append(12); i += 2
            elif text[i] in ENG2GP:
                values.append(ENG2GP[text[i]]); i += 1
            else:
                i += 1
        elif text[i] in ENG2GP:
            values.append(ENG2GP[text[i]]); i += 1
        else:
            i += 1
    return values

DEOR_OE = """Welund him be wurman wræces cunnade,
anhydig eorl earfoþa dreag,
hæfde him to gesiþþe sorge ond longaþ,
wintercealde wræce; wean oft onfond,
siþþan hine Niðhad on nede legde,
swoncre seonobende on syllan monn.
Þæs ofereode, þisses swa mæg.
Beadohilde ne wæs hyre broþra deaþ
on sefan swa sar swa hyre sylfre þing,
þæt heo gearolice ongieten hæfde
þæt heo eacen wæs; æfre ne meahte
þriste geþencan, hu ymb þæt sceolde.
Þæs ofereode, þisses swa mæg.
We þæt Mæðhilde monge gefrugnon
wurdon grundlease Geates frige,
þæt hi seo sorglufu slæp ealle binom.
Þæs ofereode, þisses swa mæg.
Ðeodric ahte þritig wintra
Mæringa burg; þæt wæs monegum cuþ.
Þæs ofereode, þisses swa mæg.
We geascodan Eormanrices
wylfenne geþoht; ahte wide folc
Gotena rices. Þæt wæs grim cyning.
Sæt secg monig sorgum gebunden,
wean on wenan, wyscte geneahhe
þæt þæs cynerices ofercumen wære.
Þæs ofereode, þisses swa mæg.
Siteð sorgcearig, sælum bedæled,
on sefan sweorceð, sylfum þinceð
þæt sy endeleas earfoða dæl.
Mæg þonne geþencan, þæt geond þas woruld
witig Dryhten wendeþ geneahhe,
eorle monegum are gesceawað,
wislicne blæd, sumum weana dæl.
Þæt ic bi me sylfum secgan wille,
þæt ic hwile wæs Heodeninga scop,
dryhtne dyre. Me wæs Deor noma.
Ahte ic fela wintra folgað tilne,
holdne hlaford, oþþæt Heorrenda nu,
leoðcræftig monn londryht geþah,
þæt me eorla hleo ær gesealde.
Þæs ofereode, þisses swa mæg."""

deor_tokens = tokenize_oe_text(DEOR_OE)
print(f"Deor tokens: {len(deor_tokens)}")

# Apply Beaufort(Deor) at non-prime positions
# For non-prime positions, what Deor indices should we use?
# Option A: use deor[non_prime_position] (the actual position index)
# Option B: use deor[sequential_index]

# Option A: deor[non_prime_pos[i] % len(deor)]
nprunes = non_prime_runes
beau_a = [(deor_tokens[non_prime_positions[i] % len(deor_tokens)] - nprunes[i]) % 29 for i in range(len(nprunes))]
ic_a = ioc(beau_a)
print(f"Beaufort(Deor) at actual positions: IoC={ic_a:.4f}")

# Option B: deor[i % len(deor)]
beau_b = [(deor_tokens[i % len(deor_tokens)] - nprunes[i]) % 29 for i in range(len(nprunes))]
ic_b = ioc(beau_b)
print(f"Beaufort(Deor) sequential: IoC={ic_b:.4f}")

# Option C: SUB mode
sub_a = [(nprunes[i] - deor_tokens[non_prime_positions[i] % len(deor_tokens)]) % 29 for i in range(len(nprunes))]
ic_sa = ioc(sub_a)
print(f"SUB(Deor) at actual positions: IoC={ic_sa:.4f}")

# Option D: ADD mode
add_a = [(nprunes[i] + deor_tokens[non_prime_positions[i] % len(deor_tokens)]) % 29 for i in range(len(nprunes))]
ic_aa = ioc(add_a)
print(f"ADD(Deor) at actual positions: IoC={ic_aa:.4f}")

# Check: what about Beaufort(Deor) on the FULL P20 at non-prime positions (matching prime method)?
# Prime method: stream[i] = (deor[prime_pos[i]] - p20[prime_pos[i]]) % 29
# Maybe non-prime should be: (deor[nonprime_pos[i]] - p20[nonprime_pos[i]]) % 29 — same as Option A
print(f"\nBest non-prime Beaufort(Deor) at actual positions: IoC={ic_a:.4f}")
if ic_a > 1.3:
    text = to_english(beau_a)
    print(f"  Text: {text[:100]}")

# What if non-prime positions use a DIFFERENT key offset into Deor?
best_ic_deor = 0
best_off_deor = 0
for off in range(len(deor_tokens)):
    beau_off = [(deor_tokens[(non_prime_positions[i] + off) % len(deor_tokens)] - nprunes[i]) % 29 for i in range(len(nprunes))]
    ic_off = ioc(beau_off)
    if ic_off > best_ic_deor:
        best_ic_deor = ic_off
        best_off_deor = off

print(f"\nBest Deor offset for non-primes: offset={best_off_deor}, IoC={best_ic_deor:.4f}")

print("\n\nDone.")
