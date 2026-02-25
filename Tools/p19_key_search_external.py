#!/usr/bin/env python3
"""
Search for P19 Key in External Texts
======================================
The P19 key (ADD mode) seems to contain English text. The last 10 values 
map to "NOT COERCED" via GP. Search for this key pattern in:
1. Emerson's Self-Reliance
2. Other Cicada-referenced texts

Also: Search for the ENGLISH WORDS "NOT COERCED" in candidate texts,
then check if the surrounding GP encoding matches the full P19 key.
"""
import sys, os, re
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

E2GP = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,'K':5,'L':20,'M':19,
        'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':15}

# P19 confirmed key (ADD mode, positions 0-42)
P19_KEY = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]

def text_to_gp_digraph(text):
    """Convert English text to GP values with digraph detection (greedy left-to-right)."""
    result = []
    text = text.upper()
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            digraph = text[i:i+2]
            if digraph == 'TH':
                result.append(2); i += 2; continue
            elif digraph == 'NG':
                result.append(21); i += 2; continue
            elif digraph == 'OE':
                result.append(22); i += 2; continue
            elif digraph == 'AE':
                result.append(25); i += 2; continue
            elif digraph == 'IA':
                result.append(27); i += 2; continue
            elif digraph == 'EA':
                result.append(28); i += 2; continue
            elif digraph == 'EO':
                result.append(12); i += 2; continue
            elif digraph == 'IO':
                result.append(27); i += 2; continue  # IO → IA
        ch = text[i]
        if ch in E2GP:
            result.append(E2GP[ch])
        i += 1
    return result

def text_to_gp_simple(text):
    """Convert English text to GP values WITHOUT digraph detection (letter by letter)."""
    result = []
    for ch in text.upper():
        if ch in E2GP:
            result.append(E2GP[ch])
    return result

def find_subsequence(haystack, needle, max_mismatches=0):
    """Find positions where needle matches in haystack with at most max_mismatches."""
    results = []
    h_len = len(haystack)
    n_len = len(needle)
    for start in range(h_len - n_len + 1):
        mismatches = 0
        for j in range(n_len):
            if haystack[start + j] != needle[j]:
                mismatches += 1
                if mismatches > max_mismatches:
                    break
        if mismatches <= max_mismatches:
            results.append((start, mismatches))
    return results

def get_text_context(text, gp_vals, pos, window=50):
    """Get the original text context around a GP position."""
    # This is approximate - count characters to find text position
    gp_count = 0
    text_upper = text.upper()
    i = 0
    while i < len(text_upper) and gp_count < pos:
        ch = text_upper[i]
        if ch in E2GP:
            gp_count += 1
        i += 1
    start = max(0, i - window)
    end = min(len(text), i + window)
    return text[start:end].replace('\n', ' ')

def main():
    print("=" * 70)
    print("P19 KEY SEARCH IN EXTERNAL TEXTS")
    print("=" * 70)
    
    # Print the key
    key_letters = ' '.join(IDX2LAT[v] for v in P19_KEY)
    print(f"P19 key (43 values): {P19_KEY}")
    print(f"P19 key as GP letters: {key_letters}")
    
    # Confirm "NOT COERCED" at end
    print(f"\nPositions 33-42: {[IDX2LAT[v] for v in P19_KEY[33:]]}")
    print(f"= {''.join(IDX2LAT[v] for v in P19_KEY[33:])}")
    
    # Load Self-Reliance
    emerson_path = 'Tools/emerson_self_reliance.txt'
    with open(emerson_path, 'r', encoding='utf-8') as f:
        emerson_text = f.read()
    print(f"\nSelf-Reliance: {len(emerson_text)} characters")
    
    # Convert to GP both ways
    emerson_digraph = text_to_gp_digraph(emerson_text)
    emerson_simple = text_to_gp_simple(emerson_text)
    print(f"  Digraph encoding: {len(emerson_digraph)} GP values")
    print(f"  Simple encoding: {len(emerson_simple)} GP values")
    
    # Search for "NOT COERCED" in the raw text
    not_coerced_positions = []
    upper = emerson_text.upper()
    for m in re.finditer(r'NOT\s+COERCED', upper):
        not_coerced_positions.append(m.start())
    print(f"\n'NOT COERCED' found in Self-Reliance: {len(not_coerced_positions)} times")
    for pos in not_coerced_positions:
        context = emerson_text[max(0,pos-80):pos+80].replace('\n', ' ')
        print(f"  Position {pos}: ...{context}...")
    
    # Also search for just "COERCED"
    for m in re.finditer(r'COERCED', upper):
        context = emerson_text[max(0,m.start()-50):m.start()+50].replace('\n', ' ')
        print(f"  'COERCED' at {m.start()}: ...{context}...")
    
    # Search for the last 10 key values in digraph encoding
    last10 = P19_KEY[33:]  # N, O, T, C, OE, E, R, C, E, D
    print(f"\nSearching for last 10 key values {last10} in Self-Reliance...")
    
    matches = find_subsequence(emerson_digraph, last10, max_mismatches=0)
    print(f"  Digraph exact matches: {len(matches)}")
    for pos, mm in matches[:5]:
        context = get_text_context(emerson_text, emerson_digraph, pos)
        print(f"    At GP position {pos}: ...{context}...")
    
    matches = find_subsequence(emerson_simple, last10, max_mismatches=0)
    print(f"  Simple exact matches: {len(matches)}")
    
    # Search for full key (43 values) with increasing mismatch tolerance
    print(f"\nSearching for FULL key (43 values) in Self-Reliance...")
    for max_mm in range(0, 15):
        matches_d = find_subsequence(emerson_digraph, P19_KEY, max_mismatches=max_mm)
        matches_s = find_subsequence(emerson_simple, P19_KEY, max_mismatches=max_mm)
        if matches_d or matches_s:
            tag = f"mm≤{max_mm}"
            if matches_d:
                print(f"  Digraph {tag}: {len(matches_d)} matches")
                for pos, mm in matches_d[:3]:
                    context = get_text_context(emerson_text, emerson_digraph, pos)
                    print(f"    pos={pos} mm={mm}: ...{context}...")
            if matches_s:
                print(f"  Simple {tag}: {len(matches_s)} matches")
                for pos, mm in matches_s[:3]:
                    context = get_text_context(emerson_text, emerson_simple, pos)
                    print(f"    pos={pos} mm={mm}: ...{context}...")
            if max_mm > 5:
                break  # Don't search too far
    
    # Also try searching for just the first 10 values
    first10 = P19_KEY[:10]  # A, S, TH, A, R, NG, J, I, L, T
    print(f"\nSearching for first 10 key values {first10}...")
    for max_mm in range(0, 6):
        matches_d = find_subsequence(emerson_digraph, first10, max_mismatches=max_mm)
        if matches_d:
            print(f"  Digraph mm≤{max_mm}: {len(matches_d)} matches")
            for pos, mm in matches_d[:5]:
                context = get_text_context(emerson_text, emerson_digraph, pos)
                print(f"    pos={pos} mm={mm}: ...{context}...")
            if max_mm > 2:
                break
    
    # ============================================
    # Now try Aleister Crowley's Liber AL vel Legis
    # ============================================
    print("\n" + "=" * 70)
    print("SEARCH IN LIBER AL VEL LEGIS (Crowley)")
    print("=" * 70)
    
    # Common text of Liber AL - Chapter 1 (first few verses)
    liber_al = """Had! The manifestation of Nuit.
The unveiling of the company of heaven.
Every man and every woman is a star.
Every number is infinite; there is no difference.
Help me, o warrior lord of Thebes, in my unveiling before the Children of men!
Be thou Hadit, my secret centre, my heart & my tongue!
Behold! it is revealed by Aiwass the minister of Hoor-paar-kraat.
The Khabs is in the Khu, not the Khu in the Khabs.
Worship then the Khabs, and behold my light shed over you!
Let my servants be few & secret: they shall rule the many & the known.
These are fools that men adore; both their Gods & their men are fools.
Come forth, o children, under the stars, & take your fill of love!
I am above you and in you. My ecstasy is in yours. My joy is to see your joy.
Above, the gemmed azure is the naked splendour of Nuit;
She bends in ecstasy to kiss the secret ardours of Hadit.
The winged globe, the starry blue, are mine, O Ankh-af-na-khonsu!
Now ye shall know that the chosen priest & apostle of infinite space is the prince-priest the Beast;
and in his woman called the Scarlet Woman is all power given.
They shall gather my children into their fold:
they shall bring the glory of the stars into the hearts of men.
For he is ever a sun, and she a moon.
But to him is the winged secret flame, and to her the stooping starlight.
But ye are not so chosen.
Burn upon their brows, o splendrous serpent!
O azure-lidded woman, bend upon them!
The key of the rituals is in the secret word Abrahadabra.
The Book of the Law is Written and Concealed.
Aiwaz is not of the slaves that perish. Be it known that if the 
ritual be aught but joyous, there is a lie therein. There is help & hope 
in other spells. Wisdom says: be strong! Then canst thou bear more joy. 
Be not animal; refine thy rapture! If thou drink, drink by the eight 
and ninety rules of art: if thou love, exceed by delicacy; and if thou 
do aught joyous, let there be subtlety therein!
But exceed! exceed!
Strive ever to more! and if thou are truly mine -- and doubt it not, 
and if thou art ever joyous! -- death is the crown of all.
Ah! Ah! Death! Death! thou shalt long for death. Death is forbidden, 
o man, unto thee.
The length of thy longing shall be the strength of its glory. 
He that lives long & desires death much is ever the King among the Kings.
Aye! listen to the numbers & the words:
What meaneth this, o prophet? Thou knowest not; nor shalt thou know ever.
There cometh one to follow thee: he shall expound it.
But remember, o chosen one, to be me; to follow the love of Nu in 
the star-lit heaven; to look forth upon men, to tell them this glad word.
O Nuit, continuous one of Heaven, let it be ever thus;
that men speak not of Thee as One but as None; and let them speak 
not of thee at all, since thou art continuous!
None, breathed the light, faint & faery, of the stars,
and two.
For I am divided for love's sake, for the chance of union.
This is the creation of the world, that the pain of division is 
as nothing, and the joy of dissolution all.
For these fools of men and their woes care not thou at all! 
They feel little; what is, is balanced by weak joys; 
but ye are my chosen ones.
Obey my prophet! follow out the ordeals of my knowledge! 
seek me only! Then the joys of my love will redeem ye from all pain.
This is so: I swear it by the vault of my body; 
by my sacred heart and tongue; by all I can give, by all I desire of ye all.
Then the priest answered & said unto the Queen of Space, kissing 
her lovely brows, and the dew of her light bathing his whole body 
in a sweet-smelling perfume of sweat: O Nuit, continuous one of Heaven,
let it be that utter failure is impossible.
I am the flame that burns in every heart of man, and in the core 
of every star. I am Life, and the giver of Life, yet therefore is 
the knowledge of me the knowledge of death.
I am the Magician and the Exorcist. I am the axle of the wheel, 
and the cube in the circle. Come unto me is a foolish word: for it 
is I that go.
Who worshipped Heru-pa-kraath have worshipped me; ill, for I am 
the worshipper.
Remember all ye that existence is pure joy; that all the sorrows 
are but as shadows; they pass & are done; but there is that which remains.
O prophet! thou hast ill will to learn this writing.
I see thee hate the hand & the pen; but I am stronger.
Because of me in Thee which thou knewest not.
for why? Because thou wast the knower, and me.
Now let there be a veiling of this shrine: now let the light 
devour men and eat them up with blindness!
For I am perfect, being Not; and my number is nine by the fools;
but with the just I am eight, and one in eight: Which is vital,
for I am none indeed. The Empress and the King are not of me;
for there is a further secret.
I am The Empress & the Hierophant. Thus eleven, as my bride is eleven.
Hear me, ye people of sighing! The sorrows of pain and regret
Are left to the dead and the dying, The folk that not know me as yet.
These are dead, these fellows; they feel not. We are not for 
the poor and sad: the lords of the earth are our kinsfolk.
Is a God to live in a dog? No! but the highest are of us. 
They shall rejoice, our chosen; who sorroweth is not of us.
Beauty and strength, leaping laughter and delicious languor,
force and fire, are of us.
We have nothing with the outcast and the unfit: let them die in 
their misery. For they feel not. Compassion is the vice of kings:
stamp down the wretched & the weak: this is the law of the strong:
this is our law and the joy of the world.
Dost thou fail? Art thou sorry? Is fear in thine heart?
Where I am these are not.
Pity not the fallen! I never knew them. I am not for them.
I console not: I hate the consoled & the consoler.
I am unique & conqueror. I am not of the slaves that perish.
Be it known: if the body of the King dissolve, he shall
remain in pure ecstasy for ever. Nuit! Hadit! Ra-Hoor-Khuit!"""

    print(f"Liber AL text: {len(liber_al)} characters")
    
    al_digraph = text_to_gp_digraph(liber_al)
    al_simple = text_to_gp_simple(liber_al)
    print(f"  Digraph: {len(al_digraph)} GP values, Simple: {len(al_simple)} GP values")
    
    # Search for "NOT COERCED" / "COERCED" in Liber AL
    upper_al = liber_al.upper()
    for pattern in ['NOT COERCED', 'COERCED', 'NOT OF THE SLAVES']:
        count = upper_al.count(pattern)
        if count > 0:
            idx = upper_al.find(pattern)
            context = liber_al[max(0,idx-40):idx+60].replace('\n', ' ')
            print(f"  '{pattern}' found {count}x: ...{context}...")
    
    # Search for key in Liber AL
    print(f"\nSearching for P19 key in Liber AL...")
    for max_mm in range(0, 15):
        matches = find_subsequence(al_digraph, P19_KEY, max_mismatches=max_mm)
        if matches:
            print(f"  Digraph mm≤{max_mm}: {len(matches)} matches")
            for pos, mm in matches[:3]:
                context = get_text_context(liber_al, al_digraph, pos)
                print(f"    pos={pos} mm={mm}: ...{context}...")
            if max_mm > 5:
                break
    
    # ============================================
    # Try using Self-Reliance as running key to DECRYPT P19
    # ============================================
    print("\n" + "=" * 70)
    print("DECRYPT P19 USING SELF-RELIANCE AS RUNNING KEY")
    print("=" * 70)
    
    with open('LiberPrimus/pages/page_19/runes.txt', 'r', encoding='utf-8') as f:
        rtext = f.read()
    p19 = [GP[ch] for ch in rtext if ch in GP]
    n = len(p19)
    
    # Try various offsets into Self-Reliance
    best_results = []
    for encoding_name, key_stream in [("digraph", emerson_digraph), ("simple", emerson_simple)]:
        for offset in range(0, len(key_stream) - n, 10):  # Step by 10 for speed
            key = key_stream[offset:offset + n]
            if len(key) < n:
                break
            
            for mode_name, mode_fn in [("SUB", lambda c,k: (c-k)%29), ("ADD", lambda c,k: (c+k)%29), ("BEAU", lambda c,k: (k-c)%29)]:
                plain = [mode_fn(p19[i], key[i]) for i in range(n)]
                text = ''.join(IDX2LAT[v] for v in plain)
                
                # Quick score
                score = 0
                for w in ['THE', 'AND', 'FOR', 'ARE', 'NOT', 'BUT', 'ALL', 'ONE']:
                    score += text.count(w) * 10
                for w in ['THAT', 'WITH', 'THIS', 'WILL', 'FROM', 'THEY', 'HAVE']:
                    score += text.count(w) * 20
                for w in ['REARRANGING', 'PRIMES', 'NUMBERS', 'PATH', 'DEOR', 'SACRED']:
                    score += text.count(w) * 50
                
                if score > 100:
                    ioc = sum(c*(c-1) for c in Counter(plain).values()) / (n*(n-1)/29)
                    best_results.append((score, ioc, encoding_name, mode_name, offset, text[:80]))
    
    # Also try single-offset (every position)
    print("  Trying every offset for first 100 positions (ADD mode, digraph)...")
    for offset in range(min(100, len(emerson_digraph) - n)):
        key = emerson_digraph[offset:offset + n]
        plain = [(p19[i] + key[i]) % 29 for i in range(n)]
        text = ''.join(IDX2LAT[v] for v in plain)
        # Check if first word is "REARRANGING" 
        if text.startswith('REARRANGING') or text.startswith('REARRANG'):
            print(f"    !!! MATCH at offset {offset}: {text[:80]}")
            best_results.append((999, 0, "digraph", "ADD", offset, text[:80]))
    
    best_results.sort(key=lambda x: -x[0])
    print(f"\n  Top 10 results:")
    for score, ioc, enc, mode, offset, text in best_results[:10]:
        print(f"    score={score} ioc={ioc:.3f} {enc}_{mode} off={offset}")
        print(f"      {text}")
    
    # ============================================
    # Special test: What if key comes from Self-Reliance
    # but with a DIFFERENT GP encoding (reversed gematria, etc.)?
    # ============================================
    print("\n" + "=" * 70)
    print("ALTERNATIVE GP ENCODINGS FOR SELF-RELIANCE")
    print("=" * 70)
    
    # Test: map a→0, b→1, c→2, ... z→25 (standard alphabetical, NOT Gematria)
    def text_to_alphabetical(text):
        return [ord(ch) - ord('A') for ch in text.upper() if 'A' <= ch <= 'Z']
    
    emerson_alpha = text_to_alphabetical(emerson_text)
    # Reduce mod 29
    emerson_alpha29 = [v % 29 for v in emerson_alpha]
    
    # Search for P19 key
    print(f"  Alphabetical mod 29: {len(emerson_alpha29)} values")
    for max_mm in range(0, 15):
        matches = find_subsequence(emerson_alpha29, P19_KEY, max_mismatches=max_mm)
        if matches:
            print(f"    mm≤{max_mm}: {len(matches)} matches")
            for pos, mm in matches[:3]:
                # Get text context
                text_pos = 0
                gp_count = 0
                for ch in emerson_text:
                    if 'A' <= ch.upper() <= 'Z':
                        if gp_count == pos:
                            break
                        gp_count += 1
                    text_pos += 1
                ctx = emerson_text[max(0,text_pos-40):text_pos+60].replace('\n', ' ')
                print(f"      pos={pos} mm={mm}: ...{ctx}...")
            if max_mm > 5:
                break

    # Test: reversed GP (F=28, U=27, ..., EA=0)
    def text_to_rev_gp(text):
        result = []
        for ch in text.upper():
            if ch in E2GP:
                result.append((28 - E2GP[ch]) % 29)
        return result
    
    emerson_rev = text_to_rev_gp(emerson_text)
    print(f"\n  Reversed GP: {len(emerson_rev)} values")
    for max_mm in range(0, 10):
        matches = find_subsequence(emerson_rev, P19_KEY, max_mismatches=max_mm)
        if matches:
            print(f"    mm≤{max_mm}: {len(matches)} matches")
            for pos, mm in matches[:3]:
                ctx = get_text_context(emerson_text, emerson_rev, pos)
                print(f"      pos={pos} mm={mm}: ...{ctx}...")
            if max_mm > 5:
                break

if __name__ == '__main__':
    main()
