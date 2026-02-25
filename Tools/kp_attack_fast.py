"""
Fast Known Plaintext Attack - Single-rune words only
Tests all-I and all-A against totient stream, F-skip totient, and P19 key.
Also checks for Caesar, linear, and periodic patterns.
"""
import os, sys, math
from collections import Counter

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,
      '\u16B7':6,'\u16B9':7,'\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,
      '\u16D6':18,'\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,
      '\u16AA':24,'\u16AB':25,'\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = {0:'F',1:'U',2:'TH',3:'O',4:'R',5:'C',6:'G',7:'W',8:'H',9:'N',
           10:'I',11:'J',12:'EO',13:'P',14:'X',15:'S',16:'T',17:'B',18:'E',
           19:'M',20:'L',21:'NG',22:'OE',23:'D',24:'A',25:'AE',26:'Y',27:'IA',28:'EA'}

def sieve(n):
    s=[True]*(n+1); s[0]=s[1]=False
    for i in range(2,int(n**0.5)+1):
        if s[i]:
            for j in range(i*i,n+1,i): s[j]=False
    return [i for i in range(len(s)) if s[i]]

def totient(n):
    r=n;p=2;t=n
    while p*p<=t:
        if t%p==0:
            while t%p==0: t//=p
            r-=r//p
        p+=1
    if t>1: r-=r//t
    return r

print("Building totient stream...")
PRIMES = sieve(600000)
TOT = [totient(PRIMES[i])%29 for i in range(min(50000,len(PRIMES)))]
print(f"  {len(TOT)} values ready")

P19_KEY = [24,15,2,24,4,21,11,10,20,16,9,19,26,11,7,5,11,6,27,8,22,25,21,16,25,0,27,9,21,7,27,15,21,9,3,16,5,22,18,4,5,18,23,28,28,28,28]

def load(pn):
    f=f'LiberPrimus/pages/page_{pn:02d}/runes.txt'
    if not os.path.exists(f): return None,None
    with open(f,'r',encoding='utf-8') as fh: content=fh.read().strip()
    runes=[]; words=[]; cur=[]; ws=0; pos=0
    for c in content:
        if c in GP:
            if not cur: ws=pos
            runes.append(GP[c]); cur.append(GP[c]); pos+=1
        elif c in ('\u2022','.','\n',' ','-'):
            if cur: words.append((ws,len(cur),list(cur))); cur=[]
        elif c=="'": pass
    if cur: words.append((ws,len(cur),list(cur)))
    return runes,words

# ===== ANALYSIS =====
print("\n" + "="*80)
print("KNOWN PLAINTEXT ATTACK - FAST VERSION")
print("="*80)

page_data = {}
for pn in range(18,55):
    runes,words = load(pn)
    if runes is None: continue
    singles = [(ws,rr[0]) for ws,l,rr in words if l==1]
    twos = [(ws,rr) for ws,l,rr in words if l==2]
    if singles:
        page_data[pn] = {'runes':runes,'singles':singles,'twos':twos,'n':len(runes)}

# --- TEST 1: Totient matching (all-I, all-A) ---
print("\n=== TEST 1: TOTIENT STREAM MATCHING ===\n")

for pn in sorted(page_data):
    d = page_data[pn]
    singles = d['singles']
    runes = d['runes']
    if len(singles) < 3: continue
    
    # Build F-skip map
    fmap={}; ki=0
    for i,rv in enumerate(runes):
        fmap[i]=ki
        if rv!=0: ki+=1
    
    for pt,pname in [(10,'I'),(24,'A')]:
        for mname,mf in [('Vig',lambda c,p:(c-p)%29),('Beau',lambda c,p:(p+c)%29),('Sub',lambda c,p:(p-c)%29)]:
            # Regular
            kv = [(s[0],mf(s[1],pt)) for s in singles]
            mx = max(p for p,v in kv)
            best_m,best_o = 0,-1
            for off in range(min(40000,len(TOT)-mx)):
                m = sum(1 for p,v in kv if TOT[off+p]==v)
                if m>best_m: best_m=m; best_o=off
            
            expect = len(singles)/29  # random expectation
            if best_m >= max(3, expect*2.5):
                print(f"P{pn:02d} [{mname:4s} {pname}] Tot@{best_o:5d}: {best_m}/{len(singles)} (expect {expect:.1f})")
            
            # F-skip
            kvf = [(fmap[s[0]],mf(s[1],pt)) for s in singles]
            mxf = max(p for p,v in kvf)
            best_mf,best_of = 0,-1
            for off in range(min(40000,len(TOT)-mxf)):
                m = sum(1 for p,v in kvf if off+p<len(TOT) and TOT[off+p]==v)
                if m>best_mf: best_mf=m; best_of=off
            
            if best_mf >= max(3, expect*2.5):
                print(f"P{pn:02d} [{mname:4s}+F {pname}] Tot@{best_of:5d}: {best_mf}/{len(singles)} (expect {expect:.1f})")

# --- TEST 2: Caesar detection ---
print("\n=== TEST 2: CAESAR DETECTION ===\n")
for pn in sorted(page_data):
    d = page_data[pn]
    singles = d['singles']
    if len(singles) < 3: continue
    
    for pt,pname in [(10,'I'),(24,'A')]:
        for mname,mf in [('Vig',lambda c,p:(c-p)%29),('Beau',lambda c,p:(p+c)%29)]:
            vals = [mf(s[1],pt) for s in singles]
            freq = Counter(vals)
            mc = freq.most_common(1)[0]
            if mc[1] >= len(singles)*0.5:
                print(f"P{pn:02d} [{mname} {pname}] Most common key={mc[0]}: {mc[1]}/{len(singles)} ({100*mc[1]/len(singles):.0f}%)")

# --- TEST 3: Linear key detection ---
print("\n=== TEST 3: LINEAR KEY DETECTION ===\n")
for pn in sorted(page_data):
    d = page_data[pn]
    singles = d['singles']
    if len(singles) < 4: continue
    
    for pt,pname in [(10,'I'),(24,'A')]:
        for mname,mf in [('Vig',lambda c,p:(c-p)%29),('Beau',lambda c,p:(p+c)%29)]:
            kv = [(s[0],mf(s[1],pt)) for s in singles]
            best_a,best_b,best_m = 0,0,0
            for a in range(29):
                for b in range(29):
                    m = sum(1 for p,v in kv if (a*p+b)%29==v)
                    if m>best_m: best_a,best_b,best_m = a,b,m
            
            expect = len(singles)/29
            if best_m >= max(3, expect*2.5):
                print(f"P{pn:02d} [{mname} {pname}] Linear ({best_a}*pos+{best_b})%29: {best_m}/{len(singles)} (expect {expect:.1f})")

# --- TEST 4: Periodic key ---
print("\n=== TEST 4: PERIODIC KEY DETECTION ===\n")
for pn in sorted(page_data):
    d = page_data[pn]
    singles = d['singles']
    if len(singles) < 5: continue
    
    for pt,pname in [(10,'I'),(24,'A')]:
        for mname,mf in [('Vig',lambda c,p:(c-p)%29),('Beau',lambda c,p:(p+c)%29)]:
            kv = [(s[0],mf(s[1],pt)) for s in singles]
            
            for period in range(2,51):
                groups = {}
                for p,v in kv:
                    g = p%period
                    if g not in groups: groups[g]=[]
                    groups[g].append(v)
                
                # Check consistency
                cons = sum(Counter(vals).most_common(1)[0][1] if len(vals)>1 else 1 for vals in groups.values())
                total = len(kv)
                
                if cons == total and total >= 5:
                    # Perfect period! But check if it's trivially because each group has only 1 element
                    multi_groups = sum(1 for vals in groups.values() if len(vals)>1)
                    if multi_groups >= 2:
                        print(f"P{pn:02d} [{mname} {pname}] PERFECT period {period}: {cons}/{total} ({multi_groups} overlapping groups)")

# --- TEST 5: P19 key matching ---
print("\n=== TEST 5: P19 KEY MATCHING ===\n")
for pn in sorted(page_data):
    d = page_data[pn]
    singles = d['singles']
    if len(singles) < 3: continue
    
    best = (0,0,'','','')
    for pt,pname in [(10,'I'),(24,'A')]:
        for mname,mf in [('Vig',lambda c,p:(c-p)%29),('Beau',lambda c,p:(p+c)%29)]:
            for off in range(47):
                m = sum(1 for s in singles if mf(s[1],pt) == P19_KEY[(s[0]+off)%47])
                if m>best[1]: best=(off,m,mname,pname,f"{off}")
    
    expect = len(singles)/29
    if best[1] >= max(3, expect*2):
        print(f"P{pn:02d} [{best[2]} {best[3]}] P19key@{best[0]}: {best[1]}/{len(singles)} (expect {expect:.1f})")

# --- TEST 6: Two-rune word Caesar scan ---
print("\n=== TEST 6: TWO-RUNE WORD CAESAR SCAN ===\n")

TWO_RUNE = {
    (2,18):"THE",(10,9):"IN",(10,16):"IT",(10,15):"IS",
    (3,9):"ON",(3,4):"OR",(3,0):"OF",(24,16):"AT",
    (24,15):"AS",(24,9):"AN",(17,18):"BE",(17,26):"BY",
    (23,3):"DO",(6,3):"GO",(8,18):"HE",(10,0):"IF",
    (19,18):"ME",(19,26):"MY",(9,3):"NO",(15,3):"SO",
    (16,3):"TO",(1,13):"UP",(1,15):"US",(7,18):"WE",
    (24,19):"AM",(24,16):"AT",
}

for pn in sorted(page_data):
    d = page_data[pn]
    twos = d['twos']
    if len(twos) < 5: continue
    
    for shift in range(29):
        decoded = []
        for pos,ciph in twos:
            p0=(ciph[0]-shift)%29; p1=(ciph[1]-shift)%29
            w = TWO_RUNE.get((p0,p1))
            if w: decoded.append(w)
        
        if len(decoded) >= max(3, len(twos)*0.12):
            print(f"P{pn:02d} shift {shift:2d}: {len(decoded)}/{len(twos)} ({100*len(decoded)/len(twos):.0f}%) - {', '.join(decoded[:10])}")

# --- TEST 7: Verify against P19 known solution ---
print("\n=== TEST 7: VERIFY APPROACH ON P19 (KNOWN SOLUTION) ===\n")

runes19,words19 = load(19)
if runes19:
    singles19 = [(ws,rr[0]) for ws,l,rr in words19 if l==1]
    print(f"P19: {len(runes19)} runes, {len(singles19)} single-rune words")
    
    # P19 uses Vigenere ADD with key length 47
    # plaintext[i] = (cipher[i] - key[i%47]) % 29
    # So: key[i%47] = (cipher[i] - plaintext[i]) % 29
    # For single-rune words that decrypt to I(10) or A(24):
    for sw_pos, sw_cipher in singles19:
        key_val = P19_KEY[sw_pos % 47]
        plain_val = (sw_cipher - key_val) % 29
        plain_latin = IDX2LAT.get(plain_val, '?')
        print(f"  Pos {sw_pos:3d}: cipher={sw_cipher:2d}, key[{sw_pos%47}]={key_val:2d}, "
              f"plain={plain_val:2d} ({plain_latin})")
        # Is the decrypted single-rune word "I" or "A"?
        if plain_val == 10:
            print(f"    -> Decrypts to I ✓")
        elif plain_val == 24:
            print(f"    -> Decrypts to A ✓")
        else:
            print(f"    -> Decrypts to {plain_latin} (NOT I or A!)")

# --- TEST 8: Actually check if P19 single-rune words validate ---
print("\n=== TEST 8: P19 VALIDATION - TOTIENT CHECK ===\n")
if runes19:
    # We know P19 uses Vigenere ADD with key = P19_KEY (period 47)
    # If we assume all single-rune words are "I":
    kv_I = [(s[0], (s[1]-10)%29) for s in singles19]
    print(f"  If all='I': key values = {[v for _,v in kv_I]}")
    
    # Check P19 key periodicity
    for period in [47]:
        groups = {}
        for p,v in kv_I:
            g = p%period
            if g not in groups: groups[g]=[]
            groups[g].append(v)
        
        cons = sum(Counter(vals).most_common(1)[0][1] if len(vals)>1 else 1 for vals in groups.values())
        print(f"  Period {period}: {cons}/{len(kv_I)} consistent")
    
    # Now with actual decrypted values
    actual = []
    for s in singles19:
        plain = (s[1] - P19_KEY[s[0]%47]) % 29
        actual.append(plain)
    print(f"  Actual decrypted values: {actual}")
    print(f"  Actual Latin: {[IDX2LAT.get(v,'?') for v in actual]}")

print("\nDONE")
