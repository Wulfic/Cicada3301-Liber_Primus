"""
COMPREHENSIVE LP Solved Plaintext as Running Key Attack.

Previous tests were INCOMPLETE (only partial pages, some fabricated text).
This script uses ALL confirmed solved plaintext from ALL pages.
Also analyzes P19 key differences against candidate texts.
"""

import os, sys, math
from collections import Counter

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

# === OE Tokenizer ===
LATIN_TO_VAL = {
    'F': 0, 'U': 1, 'V': 1, 'TH': 2, 'Þ': 2, 'Ð': 2,
    'O': 3, 'R': 4, 'C': 5, 'K': 5, 'G': 6, 'W': 7, 'H': 8, 'N': 9,
    'I': 10, 'J': 11, 'EO': 12, 'Z': 14, 'S': 15, 'T': 16, 'B': 17,
    'E': 18, 'M': 19, 'L': 20, 'NG': 21, 'OE': 22, 'D': 23,
    'A': 24, 'AE': 25, 'Æ': 25, 'Y': 26, 'IA': 27, 'IO': 27, 'EA': 28
}

def tokenize_english(text):
    """Convert English text to GP values using digraph-aware tokenizer"""
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-0123456789':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if i + 2 < len(text) and text[i:i+3] == 'ING':
            # Handle -ING carefully: I + NG
            values.append(10)  # I
            values.append(21)  # NG  
            i += 3
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

# === ALL SOLVED PLAINTEXT (from SOLVED_PLAINTEXT_COLLECTION.md) ===

LP_SOLVED = {
    'P00': "LIBER PRIMUS",
    'P01': "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    'P02': "CHAPTER I INTUS",
    'P03': "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF",
    'P04': "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    'P05': "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED",
    'P06_09': """A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY""",
    'P10_13': """THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY""",
    'P14_15': """A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS WERE ENLIGHTENED""",
    'P16': "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
    'P55': "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    'P56': "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
    'P57': "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
    'P59': "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    'P60': "CHAPTER I INTUS",
    'P63': "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED",
    'P64': """A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED""",
    'P68': """THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY""",
    'P73': "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    'P74': "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
}

# === Page Loading ===
def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

# === IoC ===
def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

def to_english(gp_values):
    return ''.join(LATIN[v] for v in gp_values)

# === Primes ===
def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

PRIMES = sieve_primes(10000)

# ========= MAIN =========

def main():
    print("=" * 80)
    print("COMPREHENSIVE LP SOLVED PLAINTEXT AS RUNNING KEY")
    print("=" * 80)
    
    # Build concatenated solved plaintext in page order
    page_order = ['P00', 'P01', 'P02', 'P03', 'P04', 'P05', 'P06_09', 'P10_13', 'P14_15', 'P16',
                  'P55', 'P56', 'P57', 'P59', 'P60', 'P63', 'P64', 'P68', 'P73', 'P74']
    
    all_plaintext_tokens = []
    for name in page_order:
        tokens = tokenize_english(LP_SOLVED[name])
        all_plaintext_tokens.extend(tokens)
    
    # Also build LP1-only and LP2-only
    lp1_tokens = []
    for name in ['P00', 'P01', 'P02', 'P03', 'P04', 'P05', 'P06_09', 'P10_13', 'P14_15', 'P16']:
        lp1_tokens.extend(tokenize_english(LP_SOLVED[name]))
    
    lp2_tokens = []
    for name in ['P55', 'P56', 'P57', 'P59', 'P60', 'P63', 'P64', 'P68', 'P73', 'P74']:
        lp2_tokens.extend(tokenize_english(LP_SOLVED[name]))
    
    print(f"Total solved tokens (all):  {len(all_plaintext_tokens)}")
    print(f"LP1 solved tokens:          {len(lp1_tokens)}")
    print(f"LP2 solved tokens:          {len(lp2_tokens)}")
    
    # Reversed versions
    all_reversed = list(reversed(all_plaintext_tokens))
    lp1_reversed = list(reversed(lp1_tokens))
    
    # Target pages to test
    UNSOLVED = list(range(18, 55))
    
    key_streams = {
        'ALL_FWD': all_plaintext_tokens,
        'ALL_REV': all_reversed,
        'LP1_FWD': lp1_tokens,
        'LP1_REV': lp1_reversed,
        'LP2_FWD': lp2_tokens,
    }
    
    results = []
    
    for pg in UNSOLVED:
        cipher = load_page(pg)
        if cipher is None:
            continue
        n = len(cipher)
        
        for ks_name, ks in key_streams.items():
            if len(ks) < n:
                # Not enough key material, skip
                continue
            
            # Test ALL offsets
            max_offset = len(ks) - n
            for offset in range(max_offset + 1):
                key_slice = ks[offset:offset+n]
                
                for mode_name, op in [('SUB', lambda c,k: (c-k)%29), ('ADD', lambda c,k: (c+k)%29), ('BEAU', lambda c,k: (k-c)%29)]:
                    plain = [op(c,k) for c,k in zip(cipher, key_slice)]
                    ic = ioc(plain)
                    
                    if ic > 1.25:  # Higher threshold due to large number of tests
                        text = to_english(plain[:60])
                        results.append((ic, f"P{pg} {ks_name} off={offset} {mode_name}", text))
        
        # Also test with F-skip
        for ks_name, ks in key_streams.items():
            for fmode in ['sub', 'add', 'beau']:
                plain = []
                k_idx = 0
                for c in cipher:
                    if c == 0:  # F rune
                        plain.append(0)
                    else:
                        k = ks[k_idx % len(ks)]
                        if fmode == 'sub':
                            plain.append((c - k) % 29)
                        elif fmode == 'add':
                            plain.append((c + k) % 29)
                        elif fmode == 'beau':
                            plain.append((k - c) % 29)
                        k_idx += 1
                
                ic = ioc(plain)
                if ic > 1.25:
                    text = to_english(plain[:60])
                    results.append((ic, f"P{pg} {ks_name} FSKIP-{fmode.upper()}", text))
    
    # Print results
    print(f"\n{'='*80}")
    print(f"RESULTS WITH IoC > 1.25  ({len(results)} found)")
    print(f"{'='*80}")
    
    results.sort(key=lambda x: -x[0])
    for ic, desc, text in results[:30]:
        print(f"  IoC={ic:.4f}  {desc}")
        print(f"    {text}")
    
    if not results:
        print("  NO RESULTS above IoC 1.25!")
    
    # === P19 KEY DIFFERENCE ANALYSIS ===
    print(f"\n{'='*80}")
    print("P19 KEY DIFFERENCE ANALYSIS")
    print(f"{'='*80}")
    
    p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
    
    # Check difference with each solved page's text at various offsets
    print("\nDifference analysis: (P19_key[i] - text[offset+i]) % 29")
    print("Looking for: constant, periodic, arithmetic, or recognizable patterns\n")
    
    for ks_name, ks in key_streams.items():
        best_matches = 0
        best_offset = 0
        best_diff = None
        
        for offset in range(min(len(ks), 5000)):
            if offset + 43 > len(ks):
                break
            text_slice = ks[offset:offset+43]
            diff = [(p19_key[i] - text_slice[i]) % 29 for i in range(43)]
            
            # Count matches (diff == 0) 
            matches = diff.count(0)
            if matches > best_matches:
                best_matches = matches
                best_offset = offset
                best_diff = diff
        
        print(f"{ks_name}: Best offset={best_offset}, {best_matches}/43 zero-diffs")
        if best_diff:
            # Check if diff is constant
            if len(set(best_diff)) == 1:
                print(f"  *** CONSTANT DIFF: {best_diff[0]} ***")
            # Check if diff is periodic
            for period in range(2, 22):
                is_periodic = True
                for i in range(period, 43):
                    if best_diff[i] != best_diff[i % period]:
                        is_periodic = False
                        break
                if is_periodic:
                    print(f"  *** PERIODIC with period {period}: {best_diff[:period]} ***")
                    break
            # Show first 20 diffs
            print(f"  Diffs: {best_diff[:20]}...")
            # Check if diffs match prime sequence mod 29
            prime_diffs = [PRIMES[i] % 29 for i in range(43)]
            prime_matches = sum(1 for a,b in zip(best_diff, prime_diffs) if a == b)
            print(f"  Matches with prime(i) mod 29: {prime_matches}/43")
    
    # Also check differences with Deor and Rune Poem OE
    print("\n--- Deor/Rune Poem difference analysis ---")
    
    # Load Deor and Rune Poem
    DEOR_OE_TOKENS = tokenize_oe_text("""Welund him be wurman wræces cunnade,
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
Þæs ofereode, þisses swa mæg.""")
    
    for name, tokens in [("Deor_OE", DEOR_OE_TOKENS)]:
        best_m, best_o = 0, 0
        for offset in range(len(tokens)):
            if offset + 43 > len(tokens):
                break
            diff = [(p19_key[i] - tokens[(offset+i) % len(tokens)]) % 29 for i in range(43)]
            m = diff.count(0)
            if m > best_m:
                best_m = m
                best_o = offset
                best_d = diff
        
        print(f"\n{name}: Best offset={best_o}, {best_m}/43 zero-diffs")
        if best_m > 0:
            diff = [(p19_key[i] - tokens[(best_o+i) % len(tokens)]) % 29 for i in range(43)]
            print(f"  Diffs: {diff}")
            
            # Check if diffs encode English text
            diff_as_text = to_english(diff)
            print(f"  Diffs as runeglish: {diff_as_text}")
            
            # Check if diffs match the positions in the known primes
            prime_diffs = [PRIMES[i] % 29 for i in range(43)]
            pm = sum(1 for a,b in zip(diff, prime_diffs) if a == b)
            print(f"  Matches with prime(i)%29: {pm}/43")
            
            # Check consecutive diffs for arithmetic progression
            consec = [diff[i+1] - diff[i] for i in range(42)]
            print(f"  Consecutive deltas: {consec[:15]}...")


def tokenize_oe_text(text):
    """OE tokenizer"""
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


if __name__ == '__main__':
    main()
