"""
Comprehensive test of Deor poem + Prime rearrangement as running key.

P19 plaintext says: "REARRANGING THE PRIME NUMBERS WILL SHOW A PATH TO THE DEOR"

This script tests multiple interpretations:
1. Deor poem characters at PRIME positions as running key
2. Primes used to INDEX into Deor poem for key generation  
3. Deor poem with missing primes (73-1223) rearrangement
4. Anglo-Saxon Rune Poem as running key
5. Deor + Rune Poem combined
6. Prime-position extraction from Deor for each page
7. Various offset/cycling strategies
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

def tokenize_oe(text):
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}–—-':
        text = text.replace(ch, '')
    values = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i:i+2] in LATIN_TO_VAL:
            values.append(LATIN_TO_VAL[text[i:i+2]])
            i += 2
        elif text[i] in LATIN_TO_VAL:
            values.append(LATIN_TO_VAL[text[i]])
            i += 1
        else:
            i += 1
    return values

def tokenize_english(text):
    """Tokenize modern English text to GP values"""
    text = text.upper()
    return [ENG2GP[c] for c in text if c in ENG2GP]

# === Texts ===
DEOR_TEXT = """Welund him be wurman wræces cunnade,
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

# Anglo-Saxon Rune Poem (Old English original)
RUNE_POEM_OE = """Feoh byþ frofur fira gehwylcum;
sceal ðeah manna gehwylc miclun hyt dælan
gif he wile for drihtne domes hleotan.
Ur byþ anmod ond oferhyrned,
felafrecne deor, feohteþ mid hornum
mære morstapa; þæt is modig wuht.
Ðorn byþ ðearle scearp; ðegna gehwylcum
anfeng ys yfyl, ungemetum reþe
manna gehwelcum, ðe him mid resteð.
Os byþ ordfruma ælere spræce,
wisdomes wraþu ond witena frofur
and eorla gehwam eadnys ond tohiht.
Rad byþ on recyde rinca gehwylcum
sefte ond swiþhwæt, ðamðe sitteþ on ufan
meare mægenheardum ofer milpaþas.
Cen byþ cwicera gehwam, cuþ on fyre
blac ond beorhtlic, byrneþ oftust
ðær hi æþelingas inne restaþ.
Gyfu gumena byþ gleng and herenys,
wraþu and wyrþscype and wræcna gehwam
ar and ætwist, ðe byþ oþra leas.
Wennebruceþ, ðe can weana lyt
sares and sorge and him sylfa hæfþ
blæd and blysse and eac byrga geniht.
Hægl byþ hwitust corna; hwyrft hit of heofones lyfte,
wealcaþ hit windes scura; weorþeþ hit to wætere syððan.
Nyd byþ nearu on breostan; weorþeþ hi þeah oft niþa bearnum
to helpe and to hæle gehwæþre, gif hi his hlystaþ æror.
Is byþ ofereald, ungemetum slidor,
glisnaþ glæshluttur gimmum gelicust,
flor forste geworuht, fæger ansyne.
Ger byÞ gumena hiht, ðonne God læteþ,
halig heofones cyning, hrusan syllan
beorhte bleda beornum ond ðearfum.
Eoh byþ utan unsmeþe treow,
heard hrusan fæst, hyrde fyres,
wyrtrumun underwreþyd, wyn on eþle.
Peorð byþ symble plega and hlehter
wlancum on middum, ðar wigan sittaþ
on beorsele bliþe ætsomne.
Eolh-secg eard hæfþ oftust on fenne
wexeð on wature, wundaþ grimme,
blode breneð beorna gehwylcne
ðe him ænigne onfeng gedeþ.
Sigel semannum symble biþ on hihte,
ðonne hi hine feriaþ ofer fisces beþ,
oþ hi brimhengest bringeþ to lande.
Tir biþ tacna sum, healdeð trywa wel
wiþ æþelingas; a biþ on færylde
ofer nihta genipu, næfre swiceþ.
Beorc byþ bleda leas, bereþ efne swa ðeah
tanas butan tudder, biþ on telgum wlitig,
heah on helme hrysted fægere,
geloden leafum, lyfte getenge.
Eh byþ for eorlum æþelinga wyn,
hors hofum wlanc, ðær him hæleþ ymbe
welege on wicgum wrixlaþ spræce
and biþ unstyllum æfre frofur.
Man byþ on myrgþe his magan leof:
sceal þeah anra gehwylc oðrum swican,
forðum drihten wyle dome sine
þæt earme flæsc eorþan betæcan.
Lagu byþ leodum langsum geþuht,
gif hi sculun neþan on nacan tealtum
and hi sæyþa swyþe bregaþ
and se brimhengest bridles ne gymeð.
Ing wæs ærest mid East-Denum
gesewen secgun, oþ he siððan est
ofer wæg gewat; wæn æfter ran;
ðus Heardingas ðone hæle nemdun.
Eþel byþ oferleof æghwylcum men,
gif he mot ðær rihtes and gerysena on
brucan on bolde bleadum oftast.
Dæg byþ drihtnes sond, deore mannum,
mære metodes leoht, myrgþ and tohiht
eadgum and earmum, eallum brice.
Ac byþ on eorþan elda bearnum
flæsces fodor, fereþ gelome
ofer ganotes bæþ; garsecg fandaþ
hwæþer ac hæbbe æþele treowe.
Æsc biþ oferheah, eldum dyre
stiþ on staþule, stede rihte hylt,
ðeah him feohtan on firas monige.
Yr byþ æþelinga and eorla gehwæs
wyn and wyrþmynd, byþ on wicge fæger,
fæstlic on færelde, fyrdgeatewa sum.
Iar byþ eafix and ðeah a bruceþ
fodres on foldan, hafaþ fægerne eard
wætre beworpen, ðær he wynnum leofaþ.
Ear byþ egle eorla gehwylcun,
ðonne fæstlice flæsc onginneþ,
hraw colian, hrusan ceosan
blac to gebeddan; bleda gedreosaþ,
wynna gewitaþ, wera geswicaþ."""

# === Page Loading ===
def load_page(pg):
    for p in [f'LiberPrimus/pages/page_{pg:02d}/runes.txt', f'LiberPrimus/pages/page_{pg}/runes.txt']:
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                raw = f.read()
                return [GP[c] for c in raw if c in GP]
    return None

# === Primes ===
def sieve_primes(n):
    is_prime = [True] * (n+1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5)+1):
        if is_prime[i]:
            for j in range(i*i, n+1, i):
                is_prime[j] = False
    return [i for i in range(2, n+1) if is_prime[i]]

PRIMES = sieve_primes(100000)
PRIME_SET = set(PRIMES)

# Missing primes from telnet (73-1223)
MISSING_PRIMES = [p for p in PRIMES if 73 <= p <= 1223]

# === IoC ===
def ioc(values, alphabet_size=29):
    n = len(values)
    if n < 2: return 0
    counts = Counter(values)
    return sum(c*(c-1) for c in counts.values()) / (n*(n-1)) * alphabet_size

# === Decrypt modes ===
def decrypt_sub(cipher, key):
    return [(c - k) % 29 for c, k in zip(cipher, key)]

def decrypt_add(cipher, key):
    return [(c + k) % 29 for c, k in zip(cipher, key)]

def decrypt_beau(cipher, key):
    return [(k - c) % 29 for c, k in zip(cipher, key)]

# === English word scoring ===  
COMMON_WORDS = {'THE','AND','TO','OF','A','IN','IS','IT','THAT','FOR','WAS','ON','ARE','AS','WITH',
                'HIS','THEY','BE','AT','ONE','HAVE','THIS','FROM','OR','HAD','BY','NOT','BUT','WHAT',
                'ALL','WERE','WE','WHEN','YOUR','CAN','SAID','THERE','EACH','WHICH','DO','HOW','IF',
                'WILL','UP','OTHER','ABOUT','OUT','MANY','THEN','THEM','THESE','SO','SOME','HER',
                'WOULD','MAKE','LIKE','INTO','HAS','LOOK','TWO','MORE','GO','SEE','NO','WAY','COULD',
                'MY','THAN','BEEN','CALL','WHO','OIL','ITS','FIND','LONG','DOWN','DAY','DID','GET',
                'COME','MADE','MAY','PART','OVER','SELF','WITHIN','BEING','MIND','KNOW','TRUTH',
                'SHED','OUR','COMMAND','WELCOME','DIVINITY','CIRCUMFERENCE','CONSUMPTION','PRESERVATION',
                'SHALL','UPON','THROUGH','SACRED','PRIME','WISDOM','LOSS','INNOCENCE','END',
                'JOURNEY','EMERGE','INTELLIGENCE','HOLY','LAW','PROGRAM','REALITY','QUESTION',
                'DISCOVER','FOLLOW','IMPOSE','NOTHING','SWORN','OATH','PATH','REARRANGING'}

def to_english(gp_values):
    """Convert GP values to approximated English text"""
    return ''.join(LATIN[v] for v in gp_values)

def word_score(gp_values):
    """Score plaintext by looking for common words"""
    text = to_english(gp_values)
    score = 0
    for w in COMMON_WORDS:
        if w in text:
            score += len(w) * len(w)
    return score

# === Key generation strategies ===

def key_direct_deor(deor_tokens, length, offset=0):
    """Use Deor tokens directly as running key, cycling"""
    return [deor_tokens[(i + offset) % len(deor_tokens)] for i in range(length)]

def key_deor_at_prime_positions(deor_tokens, length):
    """Take Deor characters only at prime-indexed positions (2nd, 3rd, 5th, 7th...)"""
    prime_chars = [deor_tokens[p] for p in PRIMES if p < len(deor_tokens)]
    if not prime_chars:
        return None
    return [prime_chars[i % len(prime_chars)] for i in range(length)]

def key_prime_index_into_deor(deor_tokens, length):
    """For position i, use deor[prime(i) % len(deor)]"""
    return [deor_tokens[PRIMES[i] % len(deor_tokens)] for i in range(length)]

def key_prime_mod_index_deor(deor_tokens, length):
    """For position i, use deor[(PRIMES[i] mod 29)]"""
    return [deor_tokens[PRIMES[i] % 29 % len(deor_tokens)] for i in range(length)]

def key_missing_primes_index_deor(deor_tokens, length):
    """Use missing primes (73-1223) as indices into Deor"""
    return [deor_tokens[MISSING_PRIMES[i % len(MISSING_PRIMES)] % len(deor_tokens)] for i in range(length)]

def key_missing_prime_ordinals_index_deor(deor_tokens, length):
    """Use ordinal positions of missing primes (21-200) as indices into Deor"""
    ordinals = [PRIMES.index(p) for p in MISSING_PRIMES]
    return [deor_tokens[ordinals[i % len(ordinals)] % len(deor_tokens)] for i in range(length)]

def key_prime_cumsum_deor(deor_tokens, length):
    """Cumulative sum of primes mod len(deor) as index"""
    cumsum = 0
    key = []
    for i in range(length):
        cumsum = (cumsum + PRIMES[i]) % len(deor_tokens)
        key.append(deor_tokens[cumsum])
    return key

def key_deor_prime_skip(deor_tokens, length):
    """Read Deor, but skip to next prime-indexed char after each read"""
    key = []
    pos = 0
    for i in range(length):
        key.append(deor_tokens[pos % len(deor_tokens)])
        # Next position = next prime after current position
        pos += 1
        while pos not in PRIME_SET and pos < 100000:
            pos += 1
        if pos >= 100000:
            pos = pos % len(deor_tokens)
    return key

def key_deor_every_nth_prime(deor_tokens, length, n=1):
    """Take every nth character from Deor but only at positions that are prime"""
    positions = [p for p in PRIMES if p < len(deor_tokens)]
    selected = positions[::n]
    if not selected:
        return None
    chars = [deor_tokens[p] for p in selected]
    return [chars[i % len(chars)] for i in range(length)]

def key_rune_poem(rune_tokens, length, offset=0):
    """Use Rune Poem tokens as running key"""
    return [rune_tokens[(i + offset) % len(rune_tokens)] for i in range(length)]

def key_rune_poem_at_primes(rune_tokens, length):
    """Rune poem characters at prime positions"""
    prime_chars = [rune_tokens[p] for p in PRIMES if p < len(rune_tokens)]
    if not prime_chars:
        return None
    return [prime_chars[i % len(prime_chars)] for i in range(length)]

def key_combined_deor_rune(deor_tokens, rune_tokens, length):
    """Alternate between Deor and Rune Poem"""
    combined = []
    d_idx, r_idx = 0, 0
    for i in range(length):
        if i % 2 == 0:
            combined.append(deor_tokens[d_idx % len(deor_tokens)])
            d_idx += 1
        else:
            combined.append(rune_tokens[r_idx % len(rune_tokens)])
            r_idx += 1
    return combined

def key_deor_xor_primes(deor_tokens, length):
    """XOR Deor values with prime sequence mod 29"""
    return [(deor_tokens[i % len(deor_tokens)] + PRIMES[i] % 29) % 29 for i in range(length)]

def key_deor_add_primes(deor_tokens, length):
    """Add prime(i) mod 29 to Deor values"""
    return [(deor_tokens[i % len(deor_tokens)] + PRIMES[i]) % 29 for i in range(length)]

def key_deor_sub_primes(deor_tokens, length):
    """Subtract prime(i) mod 29 from Deor values"""
    return [(deor_tokens[i % len(deor_tokens)] - PRIMES[i]) % 29 for i in range(length)]

def key_totient_of_primes_into_deor(deor_tokens, length):
    """Use totient(prime(i)) = prime(i)-1 as index into deor"""
    return [deor_tokens[(PRIMES[i] - 1) % len(deor_tokens)] for i in range(length)]

def key_deor_permuted_by_missing_primes(deor_tokens, length):
    """Permute Deor positions using missing primes as a permutation map"""
    permuted = list(deor_tokens)
    for idx, mp in enumerate(MISSING_PRIMES):
        src = idx % len(permuted)
        dst = mp % len(permuted)
        permuted[src], permuted[dst] = permuted[dst], permuted[src]
    return [permuted[i % len(permuted)] for i in range(length)]

def key_deor_reversed(deor_tokens, length):
    """Deor tokens reversed"""
    rev = list(reversed(deor_tokens))
    return [rev[i % len(rev)] for i in range(length)]

def key_deor_fibonacci_positions(deor_tokens, length):
    """Fibonacci numbers as positions into Deor"""
    fib = [1, 1]
    while fib[-1] < len(deor_tokens) * 10:
        fib.append(fib[-1] + fib[-2])
    key = [deor_tokens[f % len(deor_tokens)] for f in fib]
    return [key[i % len(key)] for i in range(length)]

# F-skip versions
def decrypt_fskip(cipher, key_source, mode='sub'):
    """F-skip: when cipher rune = F(0), output F and don't advance key"""
    result = []
    k_idx = 0
    for c in cipher:
        if c == 0:  # F
            result.append(0)
        else:
            k = key_source[k_idx % len(key_source)]
            if mode == 'sub':
                result.append((c - k) % 29)
            elif mode == 'add':
                result.append((c + k) % 29)
            elif mode == 'beau':
                result.append((k - c) % 29)
            k_idx += 1
    return result

# ========= MAIN =========

def test_key(name, key, cipher, page_num, results):
    """Test a key against a cipher in all 3 modes"""
    if key is None:
        return
    n = len(cipher)
    k = key[:n] if len(key) >= n else key * (n // len(key) + 1)
    k = k[:n]
    
    for mode_name, decrypt_fn in [('SUB', decrypt_sub), ('ADD', decrypt_add), ('BEAU', decrypt_beau)]:
        plain = decrypt_fn(cipher, k)
        ic = ioc(plain)
        wscore = word_score(plain) if ic > 1.15 else 0
        
        if ic > 1.15 or wscore > 50:
            text_preview = to_english(plain[:80])
            results.append((ic, wscore, f"P{page_num} {name} {mode_name}", text_preview))
    
    # Also test F-skip
    for fmode in ['sub', 'add', 'beau']:
        plain = decrypt_fskip(cipher, key, fmode)
        if plain:
            ic = ioc(plain)
            wscore = word_score(plain) if ic > 1.15 else 0
            if ic > 1.15 or wscore > 50:
                text_preview = to_english(plain[:80])
                results.append((ic, wscore, f"P{page_num} {name} FSKIP-{fmode.upper()}", text_preview))


def main():
    print("=" * 80)
    print("DEOR + PRIME RUNNING KEY ATTACK")
    print("=" * 80)
    
    # Tokenize texts
    deor_tokens = tokenize_oe(DEOR_TEXT)
    rune_poem_tokens = tokenize_oe(RUNE_POEM_OE)
    
    # Also create English versions
    deor_english_tokens = tokenize_english(DEOR_TEXT)
    rune_english_tokens = tokenize_english(RUNE_POEM_OE)
    
    print(f"Deor OE tokens: {len(deor_tokens)}")
    print(f"Rune Poem OE tokens: {len(rune_poem_tokens)}")
    print(f"Deor English tokens: {len(deor_english_tokens)}")
    print(f"Rune Poem English tokens: {len(rune_english_tokens)}")
    print()
    
    # Show first 30 tokens of each
    print(f"Deor OE first 30: {[LATIN[v] for v in deor_tokens[:30]]}")
    print(f"Rune Poem OE first 30: {[LATIN[v] for v in rune_poem_tokens[:30]]}")
    print()
    
    # Unsolved pages
    UNSOLVED = list(range(18, 55))
    
    results = []
    
    for pg in UNSOLVED:
        cipher = load_page(pg)
        if cipher is None:
            continue
        n = len(cipher)
        
        # All key strategies with Deor OE
        strategies_deor = [
            ("Deor_direct", lambda n, off=0: key_direct_deor(deor_tokens, n, off)),
            ("Deor_off10", lambda n: key_direct_deor(deor_tokens, n, 10)),
            ("Deor_off29", lambda n: key_direct_deor(deor_tokens, n, 29)),
            ("Deor_off42", lambda n: key_direct_deor(deor_tokens, n, 42)),
            ("Deor_prime_pos", lambda n: key_deor_at_prime_positions(deor_tokens, n)),
            ("Deor_prime_idx", lambda n: key_prime_index_into_deor(deor_tokens, n)),
            ("Deor_prime_mod29", lambda n: key_prime_mod_index_deor(deor_tokens, n)),
            ("Deor_missing_idx", lambda n: key_missing_primes_index_deor(deor_tokens, n)),
            ("Deor_missing_ord", lambda n: key_missing_prime_ordinals_index_deor(deor_tokens, n)),
            ("Deor_cumsum", lambda n: key_prime_cumsum_deor(deor_tokens, n)),
            ("Deor_prime_skip", lambda n: key_deor_prime_skip(deor_tokens, n)),
            ("Deor_every2nd", lambda n: key_deor_every_nth_prime(deor_tokens, n, 2)),
            ("Deor_every3rd", lambda n: key_deor_every_nth_prime(deor_tokens, n, 3)),
            ("Deor_xor_prime", lambda n: key_deor_xor_primes(deor_tokens, n)),
            ("Deor_add_prime", lambda n: key_deor_add_primes(deor_tokens, n)),
            ("Deor_sub_prime", lambda n: key_deor_sub_primes(deor_tokens, n)),
            ("Deor_totient", lambda n: key_totient_of_primes_into_deor(deor_tokens, n)),
            ("Deor_miss_perm", lambda n: key_deor_permuted_by_missing_primes(deor_tokens, n)),
            ("Deor_reversed", lambda n: key_deor_reversed(deor_tokens, n)),
            ("Deor_fib_pos", lambda n: key_deor_fibonacci_positions(deor_tokens, n)),
        ]
        
        # Rune Poem strategies
        strategies_rune = [
            ("RunePoem_direct", lambda n, off=0: key_rune_poem(rune_poem_tokens, n, off)),
            ("RunePoem_off29", lambda n: key_rune_poem(rune_poem_tokens, n, 29)),
            ("RunePoem_primes", lambda n: key_rune_poem_at_primes(rune_poem_tokens, n)),
        ]
        
        # Combined strategies
        strategies_combined = [
            ("Combined_D+R", lambda n: key_combined_deor_rune(deor_tokens, rune_poem_tokens, n)),
        ]
        
        # Deor English tokenization strategies
        strategies_eng = [
            ("DeorEng_direct", lambda n, off=0: key_direct_deor(deor_english_tokens, n, off)),
            ("DeorEng_primepos", lambda n: key_deor_at_prime_positions(deor_english_tokens, n)),
            ("DeorEng_primeidx", lambda n: key_prime_index_into_deor(deor_english_tokens, n)),
            ("RPoemEng_direct", lambda n: key_rune_poem(rune_english_tokens, n)),
            ("RPoemEng_primes", lambda n: key_rune_poem_at_primes(rune_english_tokens, n)),
        ]
        
        all_strategies = strategies_deor + strategies_rune + strategies_combined + strategies_eng
        
        for name, key_fn in all_strategies:
            try:
                key = key_fn(n)
                test_key(name, key, cipher, pg, results)
            except Exception as e:
                pass  # Skip errors silently
    
    # === SPECIAL: Verify against P19 known plaintext ===
    print("\n" + "=" * 80)
    print("P19 KNOWN PLAINTEXT VERIFICATION")
    print("=" * 80)
    
    p19_cipher = load_page(19)
    if p19_cipher:
        p19_known_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
        
        for name, tokens in [("Deor_OE", deor_tokens), ("RunePoem_OE", rune_poem_tokens), 
                              ("Deor_Eng", deor_english_tokens), ("RunePoem_Eng", rune_english_tokens)]:
            print(f"\n--- Checking {name} against P19 known key (first 43 values) ---")
            
            # Direct match
            direct = tokens[:43]
            match_count = sum(1 for a, b in zip(direct, p19_known_key) if a == b)
            print(f"  Direct alignment: {match_count}/43 matches")
            
            # Prime positions
            prime_chars = [tokens[p] for p in PRIMES if p < len(tokens)]
            prime_key = prime_chars[:43]
            match_count = sum(1 for a, b in zip(prime_key, p19_known_key) if a == b)
            print(f"  Prime-position:   {match_count}/43 matches")
            
            # prime(i) index
            pidx_key = [tokens[PRIMES[i] % len(tokens)] for i in range(43)]
            match_count = sum(1 for a, b in zip(pidx_key, p19_known_key) if a == b)
            print(f"  Prime-indexed:    {match_count}/43 matches")
            
            # Try all offsets for direct
            best_offset, best_matches = 0, 0
            for off in range(len(tokens)):
                key_attempt = [tokens[(i + off) % len(tokens)] for i in range(43)]
                m = sum(1 for a, b in zip(key_attempt, p19_known_key) if a == b)
                if m > best_matches:
                    best_matches = m
                    best_offset = off
            print(f"  Best offset: offset={best_offset}, {best_matches}/43 matches")
            
            # Check: (known_key - text) mod 29 = constant? (would mean simple shift)
            diffs = [(p19_known_key[i] - tokens[i % len(tokens)]) % 29 for i in range(min(43, len(tokens)))]
            if len(set(diffs)) == 1:
                print(f"  *** CONSTANT DIFF: {diffs[0]} ***")
            
            # Random expectation
            print(f"  (Random expectation: {43/29:.1f} matches)")
    
    # === Print results ===
    print("\n" + "=" * 80)
    print("ALL RESULTS WITH IoC > 1.15")
    print("=" * 80)
    
    results.sort(key=lambda x: -x[0])
    
    if not results:
        print("NO RESULTS above IoC 1.15 threshold!")
    else:
        for ic, wscore, desc, preview in results[:50]:
            print(f"  IoC={ic:.4f} WScore={wscore:3d}  {desc}")
            if wscore > 30:
                print(f"    Text: {preview}")
    
    # === SPECIAL: Check if P19 key matches any literary pattern ===
    print("\n" + "=" * 80)
    print("P19 KEY PATTERN ANALYSIS (43 known values)")
    print("=" * 80)
    
    p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
    
    print(f"Key as Latin: {'.'.join(LATIN[v] for v in p19_key)}")
    
    # Check: is the key the GP values of an English text?
    # key[33:43] = N.O.T.C.OE.E.R.C.E.D = "NOT COERCED"
    print(f"\nPositions 33-42: {'.'.join(LATIN[v] for v in p19_key[33:43])}")
    print("  = 'NOT COERCED' in runeglish")
    
    # Check: are there other English words hidden at different positions?
    key_latin = ''.join(LATIN[v] for v in p19_key)
    print(f"\nFull key as string: {key_latin}")
    
    # Search for words in the key string
    found_words = []
    for w in COMMON_WORDS:
        if w in key_latin:
            pos = key_latin.index(w)
            found_words.append((pos, w))
    found_words.sort()
    print(f"English words found in key: {found_words}")


if __name__ == '__main__':
    main()
