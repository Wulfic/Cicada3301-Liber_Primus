#!/usr/bin/env python3
"""
Comprehensive Running Key Attack on Unsolved Pages
===================================================
Tests multiple key sources:
1. Concatenated LP1+LP2 solved plaintext (as GP values)
2. Cross-page rune values (page N's runes as key for page M)
3. P19 recovered key extended via known texts
4. Deor poem (full and refrain) as running key  
5. Prime digit sequences
"""
import sys, os, math
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

GP = {'\u16A0':0,'\u16A2':1,'\u16A6':2,'\u16A9':3,'\u16B1':4,'\u16B3':5,'\u16B7':6,'\u16B9':7,
      '\u16BB':8,'\u16BE':9,'\u16C1':10,'\u16C2':11,'\u16C4':11,
      '\u16C7':12,'\u16C8':13,'\u16C9':14,'\u16CB':15,'\u16CF':16,'\u16D2':17,'\u16D6':18,
      '\u16D7':19,'\u16DA':20,'\u16DD':21,'\u16DF':22,'\u16DE':23,'\u16AA':24,'\u16AB':25,
      '\u16A3':26,'\u16E1':27,'\u16E0':28}
IDX2LAT = ['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']

def eng_to_gp(text):
    """Convert English text to GP values, handling digraphs."""
    text = text.upper().replace(' ', '').replace('\n', '')
    for ch in '.,;:!?\'"()[]{}0123456789':
        text = text.replace(ch, '')
    vals = []
    i = 0
    while i < len(text):
        if i + 1 < len(text):
            di = text[i:i+2]
            if di in ('TH','NG','EA','EO','OE','AE','IA'):
                mapping = {'TH':2,'NG':21,'EA':28,'EO':12,'OE':22,'AE':25,'IA':27}
                vals.append(mapping[di])
                i += 2
                continue
        ch = text[i]
        mapping = {'A':24,'B':17,'C':5,'D':23,'E':18,'F':0,'G':6,'H':8,'I':10,'J':11,
                   'K':5,'L':20,'M':19,'N':9,'O':3,'P':13,'Q':5,'R':4,'S':15,'T':16,
                   'U':1,'V':1,'W':7,'X':14,'Y':26,'Z':14}
        if ch in mapping:
            vals.append(mapping[ch])
        i += 1
    return vals

def load_runes(page_num):
    """Load rune GP values from a page."""
    path = f'LiberPrimus/pages/page_{page_num:02d}/runes.txt'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return [GP[ch] for ch in text if ch in GP]

def calc_ioc(vals):
    if len(vals) < 2: return 0
    counts = Counter(vals)
    n = len(vals)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1) / 29) if n > 1 else 0

def count_english_words(text):
    """Count English words in a decrypted text."""
    words_3 = {'THE','AND','FOR','ARE','BUT','NOT','YOU','ALL','CAN','HER','WAS','ONE',
               'OUR','OUT','HIS','HAS','ITS','WHO','HOW','MAN','OLD','NEW','NOW','WAY',
               'MAY','DAY','HAD','HIM','LET','SAY','SHE','TOO','USE'}
    words_4 = {'THAT','WITH','HAVE','THIS','WILL','YOUR','FROM','THEY','BEEN','SAID',
               'EACH','WHEN','THAN','WHAT','WERE','SOME','LIKE','SELF','KNOW','MIND',
               'MUST','FIND','SEEK','PATH','FREE','SOUL','BODY'}
    words_5 = {'THERE','THEIR','WHICH','THESE','THOSE','AFTER','EVERY','ABOUT','WOULD',
               'COULD','BEING','SHALL','TRUTH','LIGHT','WORLD','NEVER','THINK'}
    
    score = 0
    for w in words_3:
        c = text.count(w)
        score += c * 9
    for w in words_4:
        c = text.count(w)
        score += c * 16
    for w in words_5:
        c = text.count(w)
        score += c * 25
    return score

def test_running_key(cipher, key, offset=0):
    """Test running key at offset, return best mode result."""
    n = len(cipher)
    best = (0, 0, '', '')
    for mode in ['sub', 'beau', 'add']:
        plain = []
        for i in range(n):
            k = key[(i + offset) % len(key)]
            c = cipher[i]
            if mode == 'sub':
                plain.append((c - k) % 29)
            elif mode == 'beau':
                plain.append((k - c) % 29)
            else:
                plain.append((c + k) % 29)
        ioc = calc_ioc(plain)
        text = ''.join(IDX2LAT[v] for v in plain)
        score = count_english_words(text)
        if score > best[1] or (score == best[1] and ioc > best[0]):
            best = (ioc, score, mode, text)
    return best

# ===== BUILD KNOWN PLAINTEXT CORPUS =====
SOLVED_TEXT = {
    0: "LIBER PRIMUS",
    1: "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
    2: "CHAPTER I INTUS",
    3: "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF",
    4: "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
    5: "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED KNOW THIS",
    6: "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHAT YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHAT YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
    10: "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
    14: "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD I DONT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS WERE ENLIGHTENED",
    16: "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS KNOW THIS",
}

# Also add solved LP2 pages
SOLVED_LP2 = {
    55: "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
    56: "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
    61: "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE",
}

def main():
    print("=" * 70)
    print("COMPREHENSIVE RUNNING KEY ATTACK")
    print("=" * 70)
    
    # Build concatenated plaintext
    full_plain = []
    for page in sorted(SOLVED_TEXT.keys()):
        vals = eng_to_gp(SOLVED_TEXT[page])
        full_plain.extend(vals)
    print(f"LP1 plaintext (pages 0-16): {len(full_plain)} GP values")
    
    lp2_plain = []
    for page in sorted(SOLVED_LP2.keys()):
        vals = eng_to_gp(SOLVED_LP2[page])
        lp2_plain.extend(vals)
    print(f"LP2 solved plaintext: {len(lp2_plain)} GP values")
    
    all_plain = full_plain + lp2_plain
    print(f"Total known plaintext: {len(all_plain)} GP values")
    
    # Load unsolved pages
    test_pages = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 40, 44, 50]
    unsolved = {}
    for p in test_pages:
        vals = load_runes(p)
        if vals and len(vals) > 50:
            unsolved[p] = vals
    
    print(f"\nLoaded {len(unsolved)} unsolved pages")
    for p, v in sorted(unsolved.items()):
        print(f"  P{p}: {len(v)} runes")
    
    # Also load rune values from solved pages (to test cross-page keying)
    solved_runes = {}
    for p in list(range(1, 18)) + [55, 56, 61, 62, 63, 64, 67, 68, 74]:
        vals = load_runes(p)
        if vals:
            solved_runes[p] = vals
    
    hits = []
    
    # ============================================
    # TEST 1: LP1 plaintext as running key
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 1: LP1 Plaintext Running Key (all offsets)")
    print("=" * 70)
    
    for target_page, cipher in sorted(unsolved.items()):
        best_score = 0
        best_result = None
        for offset in range(0, len(full_plain), max(1, len(full_plain) // 50)):
            ioc, score, mode, text = test_running_key(cipher, full_plain, offset)
            if score > best_score:
                best_score = score
                best_result = (offset, mode, ioc, text[:80])
        if best_score > 50:
            print(f"  P{target_page}: score={best_score} off={best_result[0]} {best_result[1]} IoC={best_result[2]:.3f}")
            print(f"    {best_result[3]}")
            hits.append((best_score, f"LP1_P{target_page}", best_result))
    
    # ============================================
    # TEST 2: Cross-page rune values as key
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 2: Cross-page Rune Values as Key")
    print("=" * 70)
    
    for target_page, cipher in sorted(unsolved.items()):
        best_score = 0
        best_result = None
        for key_page, key_runes in sorted(solved_runes.items()):
            if len(key_runes) < len(cipher) // 2:
                continue  # Key too short
            for offset in [0]:
                ioc, score, mode, text = test_running_key(cipher, key_runes, offset)
                if score > best_score:
                    best_score = score
                    best_result = (key_page, 0, mode, ioc, text[:80])
        if best_score > 50:
            print(f"  P{target_page}: score={best_score} keyP={best_result[0]} {best_result[2]} IoC={best_result[3]:.3f}")
            print(f"    {best_result[4]}")
            hits.append((best_score, f"XPAGE_P{target_page}", best_result))
    
    # ============================================
    # TEST 3: P19 key match in known plaintext  
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 3: Search P19 key in known plaintext")
    print("=" * 70)
    
    p19_key = [24, 15, 2, 24, 4, 21, 11, 10, 20, 16, 9, 19, 26, 11, 7, 5, 11, 6, 27, 8, 22, 25, 21, 16, 25, 0, 27, 9, 21, 7, 27, 15, 21, 9, 3, 16, 5, 22, 18, 4, 5, 18, 23]
    
    # Search for consecutive match
    best_match_len = 0
    best_match_pos = -1
    for start in range(len(all_plain) - 10):
        match_len = 0
        for i in range(min(43, len(all_plain) - start)):
            if all_plain[start + i] == p19_key[i]:
                match_len += 1
            else:
                break
        if match_len > best_match_len:
            best_match_len = match_len
            best_match_pos = start
    
    print(f"  Best consecutive match: {best_match_len} values at position {best_match_pos}")
    if best_match_pos >= 0:
        match_text = ''.join(IDX2LAT[v] for v in all_plain[best_match_pos:best_match_pos+10])
        print(f"  Context: ...{match_text}...")
    
    # Search with edit distance
    best_fuzzy = 0
    best_fuzzy_pos = -1
    for start in range(len(all_plain) - 43):
        matches = sum(1 for i in range(43) if all_plain[start + i] == p19_key[i])
        if matches > best_fuzzy:
            best_fuzzy = matches
            best_fuzzy_pos = start
    
    print(f"  Best fuzzy match (of 43): {best_fuzzy}/43 at position {best_fuzzy_pos}")
    if best_fuzzy_pos >= 0:
        context = ''.join(IDX2LAT[v] for v in all_plain[best_fuzzy_pos:best_fuzzy_pos+20])
        print(f"  Context: {context}...")
    
    # ============================================
    # TEST 4: Prime digit sequence as key
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 4: Prime Digit Sequence as Key")
    print("=" * 70)
    
    # Generate first 2000 digits of primes
    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i+2) == 0: return False
            i += 6
        return True
    
    prime_digits = []
    p = 2
    while len(prime_digits) < 2000:
        if is_prime(p):
            for d in str(p):
                prime_digits.append(int(d))
        p += 1
    
    print(f"  First 30 prime digits: {prime_digits[:30]}")
    
    # Try various mappings of digits to GP values
    for target_page, cipher in [(20, unsolved.get(20, [])), (32, unsolved.get(32, []))]:
        if not cipher:
            continue
        for mapping_label, digit_key in [
            ("raw", prime_digits),                               # 0-9 raw
            ("mod29", [d % 29 for d in prime_digits]),           # mod 29
            ("x3", [(d * 3) % 29 for d in prime_digits]),       # ×3 mod 29
            ("x7", [(d * 7) % 29 for d in prime_digits]),       # ×7 mod 29
        ]:
            ioc, score, mode, text = test_running_key(cipher, digit_key)
            if score > 30:
                print(f"  P{target_page} prime_digits_{mapping_label} {mode}: score={score} IoC={ioc:.3f}")
                print(f"    {text[:80]}")
    
    # ============================================
    # TEST 5: Unsolved page runes as keys for each other
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 5: Unsolved Pages as Keys for Each Other")
    print("=" * 70)
    
    for target_page, cipher in sorted(unsolved.items()):
        best_score = 0
        best_result = None
        for key_page, key_runes in sorted(unsolved.items()):
            if key_page == target_page:
                continue
            if len(key_runes) < len(cipher) // 2:
                continue
            ioc, score, mode, text = test_running_key(cipher, key_runes)
            if score > best_score:
                best_score = score
                best_result = (key_page, mode, ioc, text[:80])
        if best_score > 50:
            print(f"  P{target_page} keyed by P{best_result[0]}: score={best_score} {best_result[1]} IoC={best_result[2]:.3f}")
            print(f"    {best_result[3]}")
    
    # ============================================
    # TEST 6: Verify P19 - check recovered key against Deor poem
    # ============================================
    print("\n" + "=" * 70)
    print("TEST 6: Compare P19 Key to Deor Poem GP Values")
    print("=" * 70)
    
    # Load and tokenize Deor
    deor_path = 'Analysis/Reference_Docs/deor_poem.txt'
    with open(deor_path, 'r', encoding='utf-8') as f:
        deor_text = f.read()
    if 'DEOR POEM (MODERN ENGLISH' in deor_text:
        deor_text = deor_text[:deor_text.index('DEOR POEM (MODERN ENGLISH')]
    deor_text = deor_text.replace('DEOR POEM (OLD ENGLISH)', '')
    deor_vals = eng_to_gp(deor_text.replace('Þ','TH').replace('þ','th').replace('Ð','TH').replace('ð','th').replace('Æ','AE').replace('æ','ae'))
    
    print(f"  Deor poem: {len(deor_vals)} GP values")
    print(f"  P19 key: {len(p19_key)} values")
    
    # Compare P19 key to Deor at each offset
    best_match = 0
    best_off = -1
    for off in range(len(deor_vals) - 43):
        matches = sum(1 for i in range(43) if deor_vals[off + i] == p19_key[i])
        if matches > best_match:
            best_match = matches
            best_off = off
    print(f"  Best match of P19 key in Deor: {best_match}/43 at offset {best_off}")
    
    # ============================================
    # SUMMARY
    # ============================================
    print("\n" + "=" * 70)
    print("ALL HITS (score > 50)")
    print("=" * 70)
    hits.sort(reverse=True)
    for score, label, result in hits[:20]:
        print(f"  Score={score}: {label} -> {result}")
    if not hits:
        print("  No results above threshold.")

if __name__ == '__main__':
    main()
