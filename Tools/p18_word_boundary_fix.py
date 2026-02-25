"""
P18/P19 Word Boundary Investigation

KEY FINDING: In pages from runes_full.txt format:
- `-` = word separator (space)  
- newlines = image line breaks (words can span across them!)
- `.` = sentence end
- Our previous parsing split on BOTH dashes AND newlines = WRONG

This script compares word parsing methods and re-analyzes with correct boundaries.
"""
import os, sys, re

GP = {
    '\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
    '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
    '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
    '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
    '\u16A3':26,'\u16E1':27,'\u16E0':28
}
LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
MOD = 29

os.chdir(r'c:\Users\tyler\Repos\Cicada3301')

def parse_page(pg, method):
    """Parse rune page with different word-boundary methods.
    method='old': split on dashes AND newlines (our previous approach)
    method='new': strip newlines first, then split on dashes only
    """
    with open(f'LiberPrimus/pages/page_{pg:02d}/runes.txt','r',encoding='utf-8') as f:
        raw = f.read()
    
    if method == 'old':
        # Old method: split on dashes, dots, newlines
        # Extract rune sequences between separators
        words = []
        current = []
        for c in raw:
            if c in GP:
                current.append(GP[c])
            elif c in '-.\n\r':
                if current:
                    words.append(current)
                    current = []
        if current:
            words.append(current)
        return words
    
    elif method == 'new':
        # New method: strip newlines (are just image line breaks), then split on dashes
        # Remove newlines
        text = raw.replace('\n','').replace('\r','')
        # Split on dashes and dots
        words = []
        current = []
        for c in text:
            if c in GP:
                current.append(GP[c])
            elif c in '-.':
                if current:
                    words.append(current)
                    current = []
        if current:
            words.append(current)
        return words

def decrypt_word(word_gp, key, start_pos, klen, mode='ADD'):
    if mode == 'ADD':
        return [(word_gp[j] + key[(start_pos+j) % klen]) % MOD for j in range(len(word_gp))]
    elif mode == 'SUB':
        return [(word_gp[j] - key[(start_pos+j) % klen]) % MOD for j in range(len(word_gp))]

def gp_to_text(vals):
    return ''.join(LAT[v] for v in vals)

# ==== P19 ANALYSIS ====
print("="*80)
print("P19 WORD BOUNDARY COMPARISON") 
print("="*80)

for method in ['old', 'new']:
    words = parse_page(19, method)
    total_runes = sum(len(w) for w in words)
    print(f"\nMethod '{method}': {len(words)} words, {total_runes} total runes")
    
    # Show first 15 words with sizes
    for i, w in enumerate(words[:20]):
        print(f"  w{i}: {len(w)} runes = {gp_to_text(w)}")

# P19 key (43 values, ADD mode)
p19_key = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23]
p19_klen = 43

print(f"\n--- P19 decryption with CORRECT word boundaries (method='new') ---")
words_new = parse_page(19, 'new')
pos = 0
for i, w in enumerate(words_new[:20]):
    dec = decrypt_word(w, p19_key, pos, p19_klen, 'ADD')
    text = gp_to_text(dec)
    print(f"  w{i} (pos {pos}, {len(w)} runes): '{text}'")
    pos += len(w)

# ==== P18 ANALYSIS ====
print(f"\n{'='*80}")
print("P18 WORD BOUNDARY COMPARISON")
print("="*80)

for method in ['old', 'new']:
    words = parse_page(18, method)
    total_runes = sum(len(w) for w in words)
    print(f"\nMethod '{method}': {len(words)} words, {total_runes} total runes")
    
    # Show first 20 words with sizes
    for i, w in enumerate(words[:30]):
        print(f"  w{i}: {len(w)} runes = {gp_to_text(w)}")

# P18 confirmed key (34/53 confirmed, SUB mode, klen=53)
p18_confirmed = {
    2:21, 3:6, 4:19, 5:6, 6:6,
    13:18, 14:25, 15:25, 16:15, 17:10, 18:16, 19:24, 20:13, 21:11, 22:20,
    23:2, 24:5, 25:5,
    26:27, 27:3, 28:12, 29:19,
    38:24, 39:16, 40:5, 41:8, 42:23, 43:26, 44:21,
    46:7, 47:25, 48:24,
    50:1, 51:21
}
p18_klen = 53
# Fill undetermined with 0
p18_key = [p18_confirmed.get(b, 0) for b in range(p18_klen)]

# Dictionary for matching
DICT_WORDS = set()
for w in "A AN AM AS AT BE BY DO GO HE IF IN IS IT ME MY NO OF ON OR SO TO UP US WE THE AND ARE BUT CAN DID FOR GET HAS HER HIM HIS HOW ITS LET MAY NEW NOT NOW OLD ONE OUR OUT OWN SAY SHE TOO USE WAY WHO WHY ALL ANY BIG DAY END FAR FEW GOD GOT HAS HIM HIS HOW ITS JUST KEEP KIND KNOW LAST LEFT LIFE LIKE LINE LIVE LONG LOOK MADE MAKE MANY MAY MEAN MEN MIGHT MIND MOST MUCH MUST NAME NEED NEXT ONLY OPEN OTHER OVER OWN PART PLACE PLAY POINT PUT READ RIGHT ROOM RUN SAID SAME SAY SEEM SELF SHALL SHOW SIDE SMALL SO SOME SOMETHING STATE STILL SUCH TAKE TELL THAN THAT THE THEM THEN THERE THESE THEY THING THINK THIS THOSE THREE THROUGH TIME TURN UNDER UNTIL UPON VERY WANT WATER WHICH WHILE WHO WILL WITH WORD WORK WORLD WOULD WRITE YEAR ABOUT AFTER AGAIN ALSO ANOTHER BACK BECAUSE BEEN BEFORE BEING BETWEEN BOTH CAME COME COULD EACH EVEN EVERY FIND FIRST FROM GIVE GREAT GROUP HAND HAVE HEAD HIGH HOUSE INTO JUST KNOW LARGE LAST LATER LEARN LEFT LESS LIGHT LITTLE LONG LOOK MADE MAKE MANY MAY MIGHT MORE MOST MUCH MUST NAME NEED NEVER NEW NIGHT NUMBER OFTEN OTHER OVER PEOPLE PLACE POINT RIGHT SAID SAME SCHOOL SHOULD SINCE SMALL SOME SOMETHING STAND STATE STILL STORY SUCH TAKE TELL THAN THAT THEIR THEM THEN THERE THESE THEY THING THINK THIS THOSE THOUGHT THREE THROUGH TIME TOGETHER TURN UNDER UNTIL UPON VERY WANT WATER WHICH WHILE WILL WITH WITHOUT WORD WORK WORLD WOULD WRITE YEAR SPIRIT TRUTH EARTH DEATH FAITH SACRED DIVINE PRIMES CIPHER FATHER MOTHER NATURE REASON ANSWER BECOME NUMBER QUEST ORDER WISDOM LEARN LIGHT NORTH SOUTH BEING POWER WHERE WITHIN EVERY EMERGE CONSUME DIVIDE CIRCLE FOLLOW SEEK FIND PATH ABOVE BELOW OATH SWORN SHADOW INSTAR TUNNEL SURFACE SHED DIVINITY CIRCUMFERENCE".split():
    DICT_WORDS.add(w)

def text_to_gp_word(word):
    """Convert English word to GP values with digraph handling."""
    result = []
    i = 0
    w = word.upper()
    ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
              'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
              'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
    DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}
    while i < len(w):
        if i + 1 < len(w):
            di = w[i:i+2]
            if di in DIGRAPHS:
                result.append(DIGRAPHS[di])
                i += 2
                continue
        if w[i] in ENG2GP:
            result.append(ENG2GP[w[i]])
        i += 1
    return tuple(result)

# Build GP dictionary
gp_dict = {}
for w in DICT_WORDS:
    gp = text_to_gp_word(w)
    if gp not in gp_dict:
        gp_dict[gp] = []
    gp_dict[gp].append(w)

print(f"\n--- P18 word matching with CORRECT boundaries (method='new') ---")
print(f"Dictionary: {len(gp_dict)} GP patterns from {len(DICT_WORDS)} words")
words_new = parse_page(18, 'new')
pos = 0
match_count = 0
total_words = len(words_new)
for i, w in enumerate(words_new):
    dec = decrypt_word(w, p18_key, pos, p18_klen, 'SUB')
    text = gp_to_text(dec)
    key_tuple = tuple(dec)
    
    # Check which key positions are ALL confirmed
    buckets = [(pos+j) % p18_klen for j in range(len(w))]
    all_confirmed = all(b in p18_confirmed for b in buckets)
    
    matched = key_tuple in gp_dict
    if matched:
        match_count += 1
    
    marker = 'Y' if matched else (' ' if not all_confirmed else 'n')
    confirmed_str = 'C' if all_confirmed else 'p'
    
    if i < 50 or matched:  # Show first 50 or all matches
        dict_match = gp_dict.get(key_tuple, ['?'])[0]
        print(f"  {marker}{confirmed_str} w{i:2d} (pos {pos:3d}, {len(w):2d} runes, bkts={buckets[:3]}...): '{text}' {'= '+dict_match if matched else ''}")
    pos += len(w)

print(f"\nTotal: {match_count}/{total_words} words matched")

# Count matches where ALL key positions are confirmed
confirmed_matches = 0
confirmed_total = 0
pos = 0
for w in words_new:
    dec = decrypt_word(w, p18_key, pos, p18_klen, 'SUB')
    buckets = [(pos+j) % p18_klen for j in range(len(w))]
    all_confirmed = all(b in p18_confirmed for b in buckets)
    if all_confirmed:
        confirmed_total += 1
        if tuple(dec) in gp_dict:
            confirmed_matches += 1
    pos += len(w)
print(f"Fully-confirmed-bucket words: {confirmed_matches}/{confirmed_total} matched")

# ==== Now check: how many words does OLD parsing give vs NEW? ====
print(f"\n{'='*80}")
print("COMPARISON SUMMARY")
print("="*80)
for pg in [18, 19]:
    old = parse_page(pg, 'old')
    new = parse_page(pg, 'new')
    print(f"  Page {pg}: OLD={len(old)} words, NEW={len(new)} words")
    print(f"    OLD rune total: {sum(len(w) for w in old)}")
    print(f"    NEW rune total: {sum(len(w) for w in new)}")

# ==== Check P19 first 10 words with NEW parsing ====
print(f"\n{'='*80}")
print("P19 - DOES REARRANGING NOW MAP CORRECTLY?")
print("="*80)
words_p19 = parse_page(19, 'new')
pos = 0
for i, w in enumerate(words_p19[:15]):
    dec = decrypt_word(w, p19_key, pos, min(43, p19_klen), 'ADD')
    text = gp_to_text(dec)
    print(f"  w{i} (pos {pos:3d}, {len(w):2d} runes): '{text}'")
    pos += len(w)
    if pos >= 43:
        print(f"  --- (beyond first key period) ---")
        break

print("\n=== DONE ===")
