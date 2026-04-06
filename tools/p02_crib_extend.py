"""P02 crib extension: verify FELLOW at w6, check w14 cross-cycle consistency."""
import sys, itertools
sys.stdout.reconfigure(encoding='utf-8')

IDX='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
RUNE_TO_IDX={r:i for i,r in enumerate(IDX)}
GP=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
with open('pages/page_02/runes.txt',encoding='utf-8') as f: raw=f.read()
cipher=[RUNE_TO_IDX[c] for c in raw if c in RUNE_TO_IDX]

# 25 CONFIRMED KEY POSITIONS
CONFIRMED=[20,1,20,27,1,7,26,25,4,19,22,4,26,9,1,18,9,15,20,1,6,10,10,16,6,23,3,13,22,10,5,0,0,2,15,4,2,0,9,22,26,22,15]
CONFIRMED_SET={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,21,22,23,24,25,26,27,28,29,30}

seps={'-','.','&',chr(36),' ','\n'}
tpw=[]
cur=[]
for c in raw:
    if c in RUNE_TO_IDX: cur.append(RUNE_TO_IDX[c])
    elif c in seps and cur: tpw.append(cur[:]); cur=[]
if cur: tpw.append(cur)
ki=0; ws=[]
for wt in tpw:
    ws.append(ki)
    for c in wt:
        k=CONFIRMED[ki%43]
        if not(c==0 and k==0): ki+=1

# All words with their lengths and key positions used
print("=== Word structure ===")
for idx in range(min(20, len(tpw))):
    ks=ws[idx]; n=len(tpw[idx])
    key_pos=list(dict.fromkeys((ks+j)%43 for j in range(n)))
    unknowns=[p for p in key_pos if p not in CONFIRMED_SET]
    cur_dec=''.join(GP[(cipher[ks+j]-CONFIRMED[(ks+j)%43])%29] for j in range(n))
    print(f"  w{idx+1:2}[{n}] ki={ks:3}..{ks+n-1:3} unknowns={unknowns}: {cur_dec}")

print()
print("=== FELLOW hypothesis check ===")
print("FELLOW (F+E+L+L+O+W) at w6, key[15..20]=[9,19,26,27,3,5]:")
fellow={15:9,16:19,17:26,18:27,19:3,20:5}
# Verify w6
w6_ks=ws[5]; w6_n=len(tpw[5])
w6_dec=[]
for j in range(w6_n):
    ki_p=(w6_ks+j)%43
    k=fellow.get(ki_p,CONFIRMED[ki_p])
    w6_dec.append(GP[(cipher[w6_ks+j]-k)%29])
print(f"  w6 with FELLOW key: {''.join(w6_dec)}")

# Check all words that use key positions 15-20 (second cycle: ki=58..63 in w14
# and third cycle: ki=101..106)
print("\nWords using key positions 15-20 (second cycle ki+43):")
for idx in range(len(tpw)):
    ks=ws[idx]; n=len(tpw[idx])
    uses_15_20=[p for p in [15,16,17,18,19,20] if any((ks+j)%43==p for j in range(n))]
    if uses_15_20 and idx!=5:  # skip w6 itself
        cur_dec=''.join(GP[(cipher[ks+j]-CONFIRMED[(ks+j)%43])%29] for j in range(n))
        fellow_dec=''.join(GP[(cipher[ks+j]-fellow.get((ks+j)%43,CONFIRMED[(ks+j)%43]))%29] for j in range(n))
        print(f"  w{idx+1:2}[{n}] ki={ks} uses pos {uses_15_20}")
        print(f"    KNOWN_KEY decode: {cur_dec}")
        print(f"    FELLOW decode:    {fellow_dec}")

print()
print("=== LP vocab candidates for w14 (7 tokens) ===")
w14_ks=ws[13]; w14_n=len(tpw[13])
print(f"w14 ciphers: {[GP[cipher[w14_ks+j]] for j in range(w14_n)]}")
print(f"w14 key positions: {[(w14_ks+j)%43 for j in range(w14_n)]}")
# Only key[14]=1 is confirmed; key[15-20] are unknowns
# Try all LP 7-token words
def gp_encode(word):
    """Encode English word as GP indices, using TH digraph where possible."""
    result=[]
    i=0
    while i<len(word):
        if i+1<len(word) and word[i:i+2]=='TH': result.append(2); i+=2
        elif i+1<len(word) and word[i:i+2]=='NG': result.append(21); i+=2
        elif i+1<len(word) and word[i:i+2]=='OE': result.append(22); i+=2
        elif i+1<len(word) and word[i:i+2]=='AE': result.append(25); i+=2
        elif i+1<len(word) and word[i:i+2]=='IA': result.append(27); i+=2
        elif i+1<len(word) and word[i:i+2]=='EA': result.append(28); i+=2
        elif i+1<len(word) and word[i:i+2]=='EO': result.append(12); i+=2
        else:
            c=word[i]
            for g_idx,g in enumerate(GP):
                if len(g)==1 and g==c: result.append(g_idx); break
            else: result.append(-1)  # unknown
            i+=1
    return result

lp_words_7 = ['STUDENT','STUDIED','HIMSELF','FOLLOWS','THOUGHT','KNOWING','BECOMES','SEEKING','NOTHING',
               'OUTSIDE','THROUGH','MASTERS','WITHOUT','SUBJECT','BETWEEN','BELIEVE','BECAUSE','OBSERVE',
               'SHADOWS','NOTHING','ANCIENT','UNKNOWN','REALITY','SEEKING','WHETHER','ALREADY','NOTHING',
               'PILGRIM','JOURNEY','SEEKING','FINDING','ANSWERS','FOLLOWS','LOOKING','STAYING','WALKING',
               'STRANGE','CIRCLES','PASSAGE','REACHES','DELIGHT','FREEDOM','NOTHING','ACHIEVE','DESTROY']
# Remove duplicates
lp_words_7=list(dict.fromkeys(lp_words_7))

for word in lp_words_7:
    enc=gp_encode(word)
    if len(enc)!=w14_n or -1 in enc: continue
    ok=True; kv={}
    for j in range(w14_n):
        ki_p=(w14_ks+j)%43
        t=enc[j]
        if ki_p in CONFIRMED_SET:
            if (cipher[w14_ks+j]-CONFIRMED[ki_p])%29!=t: ok=False; break
        else:
            kv[ki_p]=(cipher[w14_ks+j]-t)%29
    if ok:
        compatible=all(kv.get(p,fellow[p])==fellow[p] for p in [15,16,17,18,19,20] if p in kv)
        c_str="*** FELLOW-COMPATIBLE ***" if compatible else f"key differs at {[p for p in [15,16,17,18,19,20] if p in kv and kv[p]!=fellow[p]]}"
        print(f"  MATCH: w14={word} key_changes={kv}  {c_str}")
