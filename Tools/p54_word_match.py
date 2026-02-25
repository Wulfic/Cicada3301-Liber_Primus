"""
P54 Word Structure Analysis
"""
import os
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

ENG2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
          'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
          'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}
DIGRAPHS = {'TH':2,'NG':21,'EO':12,'OE':22,'EA':28,'AE':25,'IA':27}

def eng_to_gp(text):
    result = []
    i = 0; text = text.upper()
    while i < len(text):
        if i+1 < len(text) and text[i:i+2] in DIGRAPHS:
            result.append(DIGRAPHS[text[i:i+2]])
            i += 2
        elif text[i] in ENG2GP:
            result.append(ENG2GP[text[i]])
            i += 1
        else:
            i += 1
    return result

def gp_to_lat(vals):
    return ''.join(LAT[v] for v in vals)

with open('LiberPrimus/pages/page_54/runes.txt','r',encoding='utf-8') as f:
    raw = f.read()

# Show full cipher in LAT with original formatting
print("=== P54 RAW STRUCTURE ===")
for c in raw:
    if c in GP: print(LAT[GP[c]], end='')
    elif c == '-': print(' - ', end='')
    elif c == '\n': print(' / ', end='')
    elif c == '.': print('.', end='')
print()

# Parse words
words = []
current_word = []
for c in raw:
    if c in GP:
        current_word.append(GP[c])
    elif c in ('-', '\n', '.'):
        if current_word:
            words.append(current_word)
            current_word = []
if current_word:
    words.append(current_word)

print(f"\nTotal words: {len(words)}")
cw_lens = [len(w) for w in words]
print(f"Word lengths: {cw_lens}")
for i, w in enumerate(words):
    lat = gp_to_lat(w)
    print(f"  w{i:2d} ({len(w):2d}): {lat}")

# ===== KNOWN TEXT MATCHING =====
print("\n" + "="*80)
print("KNOWN TEXT WORD-LENGTH MATCHING")
print("="*80)

# Candidate plaintexts (known Cicada sections)
candidates = [
    "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO",
    "IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY",
    "CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS",
    "WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH",
    "PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK",
    "ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT",
    "THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH",
    "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE",
    "TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH",
    "LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES",
    "FIND THE DIVINITY WITHIN AND EMERGE",
]

for cand in candidates:
    cand_words = cand.split()
    gp_words = [eng_to_gp(w) for w in cand_words]
    lens = [len(w) for w in gp_words]
    total = sum(lens)
    
    # Check word length pattern match
    for start in range(len(cw_lens) - len(lens) + 1):
        if cw_lens[start:start+len(lens)] == lens:
            print(f"\n*** MATCH at word {start}: '{cand[:60]}...' ***")
            print(f"  Word lengths: {lens}, total GP: {total}")
            
            # Recover key for each mode
            plain_flat = []
            for gw in gp_words:
                plain_flat.extend(gw)
            cipher_flat = []
            for w in words[start:start+len(lens)]:
                cipher_flat.extend(w)
            
            for mode in ['SUB', 'ADD', 'BEAU']:
                key = []
                for j in range(len(plain_flat)):
                    ci = cipher_flat[j]
                    pi = plain_flat[j]
                    if mode == 'SUB': k = (ci - pi) % MOD
                    elif mode == 'ADD': k = (pi - ci) % MOD
                    elif mode == 'BEAU': k = (pi + ci) % MOD
                    key.append(k)
                
                # Check periodicity
                found_period = False
                for p in range(1, 30):
                    periodic = all(key[j] == key[j%p] for j in range(len(key)))
                    if periodic:
                        key_period = key[:p]
                        key_p_lat = gp_to_lat(key_period)
                        found_period = True
                        
                        # Decrypt entire cipher with this key
                        cipher_all = [v for t,v in [(('R', GP[c]) if c in GP else ('X', -1)) for c in raw] if t == 'R']
                        dec_all = []
                        for i in range(len(cipher_all)):
                            kv = key_period[i % p]
                            if mode == 'SUB': dec_all.append((cipher_all[i] - kv) % MOD)
                            elif mode == 'ADD': dec_all.append((cipher_all[i] + kv) % MOD)
                            elif mode == 'BEAU': dec_all.append((kv - cipher_all[i]) % MOD)
                        
                        text = gp_to_lat(dec_all)
                        # Score
                        score = 0
                        for w in ['THE','AND','THAT','WITH','FOR','ALL','YOU','NOT','THIS',
                                  'WITHIN','DEEP','WEB','EXIST','PAGE','HASH','DUTY','PILGRIM',
                                  'SEEK','END','ARE','EVERY','BELIEVE','HOLY','WISDOM','IS']:
                            score += text.count(w) * len(w)
                        
                        print(f"  {mode} period={p}: key={key_p_lat} ({key_period}) score={score}")
                        print(f"    Full: {text}")
                        break
                
                if not found_period:
                    # Show key without period
                    key_lat = gp_to_lat(key)
                    print(f"  {mode}: no short period, key={key_lat[:60]}")

# ===== Try matching with flexible word boundaries =====
# Since dashes in ciphertext may not correspond to plaintext word boundaries
# just try the continuous text matching approach
print("\n" + "="*80)
print("CONTINUOUS TEXT CRIB MATCHING")
print("="*80)

cipher_all = [GP[c] for c in raw if c in GP]
N = len(cipher_all)

for cand in candidates:
    cand_gp = eng_to_gp(cand)
    if len(cand_gp) > N:
        continue
    
    # Try at every position
    for start in range(N - len(cand_gp) + 1):
        for mode in ['SUB', 'ADD', 'BEAU']:
            key = []
            for j in range(len(cand_gp)):
                ci = cipher_all[start + j]
                pi = cand_gp[j]
                if mode == 'SUB': k = (ci - pi) % MOD
                elif mode == 'ADD': k = (pi - ci) % MOD
                elif mode == 'BEAU': k = (pi + ci) % MOD
                key.append(k)
            
            # Check for short periods
            for p in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
                if len(key) < p * 2:
                    continue
                periodic = all(key[j] == key[j % p] for j in range(len(key)))
                if periodic:
                    key_p = key[:p]
                    # Decrypt full
                    dec = [(cipher_all[i] - key_p[i%p]) % MOD if mode == 'SUB' 
                           else (cipher_all[i] + key_p[i%p]) % MOD if mode == 'ADD'
                           else (key_p[i%p] - cipher_all[i]) % MOD
                           for i in range(N)]
                    text = gp_to_lat(dec)
                    score = sum(text.count(w) * len(w) for w in ['THE','AND','THAT','WITH','FOR','ALL',
                        'YOU','NOT','THIS','WITHIN','DEEP','WEB','PAGE','EXIST','DUTY','PILGRIM',
                        'SEEK','END','ARE','EVERY','BELIEVE','WISDOM','IS','HOLY','SACRED'])
                    
                    if score >= 20:
                        key_lat = gp_to_lat(key_p)
                        text_preview = text[:80]
                        print(f"\n  MATCH! '{cand[:40]}...' at pos={start} {mode} period={p}")
                        print(f"    Key: {key_lat} ({key_p})")
                        print(f"    Text: {text_preview}")
                        print(f"    Score: {score}")
                    break

print("\n=== DONE ===")
