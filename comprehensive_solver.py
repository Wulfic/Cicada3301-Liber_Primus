#!/usr/bin/env python3
"""
Comprehensive Liber Primus Solver
Tests multiple cipher methods on unsolved pages (18-54, 58, 60-62, 67, 71-72)

Methods tested:
1. φ(prime) cipher (proven on Pages 55, 73)
2. Running key with Emerson's Self-Reliance
3. Running key with solved page plaintexts
4. Multi-pass Vigenère (keyword + second layer)
5. Word boundary analysis for pages with • separators
"""

import os
import re
import math
from pathlib import Path
from collections import Counter
from itertools import islice

# ==================== GEMATRIA PRIMUS MAPPING ====================

RUNE_TO_IDX = {
    'ᚠ': 0,  'ᚢ': 1,  'ᚦ': 2,  'ᚩ': 3,  'ᚱ': 4,
    'ᚳ': 5,  'ᚷ': 6,  'ᚹ': 7,  'ᚻ': 8,  'ᚾ': 9,
    'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14,
    'ᛋ': 15, 'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19,
    'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23, 'ᚪ': 24,
    'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28, 'ᛂ': 11,
}

IDX_TO_LATIN = {
    0: 'F', 1: 'U', 2: 'TH', 3: 'O', 4: 'R',
    5: 'C', 6: 'G', 7: 'W', 8: 'H', 9: 'N',
    10: 'I', 11: 'J', 12: 'EO', 13: 'P', 14: 'X',
    15: 'S', 16: 'T', 17: 'B', 18: 'E', 19: 'M',
    20: 'L', 21: 'NG', 22: 'OE', 23: 'D', 24: 'A',
    25: 'AE', 26: 'Y', 27: 'IA', 28: 'EA',
}

LATIN_TO_IDX = {}
for idx, lat in IDX_TO_LATIN.items():
    LATIN_TO_IDX[lat] = idx

SEPARATORS = {'-', '•', ' '}
PUNCTUATION = {'.', ',', ':', ';', '!', '?', '/', '%', '&', '$', '\n', '\r', "'"}

# ==================== UTILITY FUNCTIONS ====================

def generate_primes(n):
    """Generate first n primes using sieve."""
    if n < 1:
        return []
    limit = max(100, n * 15)
    sieve = [True] * limit
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, limit, i):
                sieve[j] = False
    primes = [i for i in range(limit) if sieve[i]]
    while len(primes) < n:
        limit *= 2
        sieve = [True] * limit
        sieve[0] = sieve[1] = False
        for i in range(2, int(limit**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, limit, i):
                    sieve[j] = False
        primes = [i for i in range(limit) if sieve[i]]
    return primes[:n]

def load_runes(page_num):
    """Load runes from a page file, return list of (rune_index, separator_or_None)."""
    base = Path(r"c:\Users\tyler\Repos\Cicada3301\LiberPrimus\pages")
    runes_file = base / f"page_{page_num:02d}" / "runes.txt"
    if not runes_file.exists():
        return None, None
    
    text = runes_file.read_text(encoding='utf-8')
    
    # Extract rune indices and track word boundaries
    indices = []
    boundaries = []  # True at positions where a word separator precedes this rune
    current_boundary = True
    
    for ch in text:
        if ch in RUNE_TO_IDX:
            indices.append(RUNE_TO_IDX[ch])
            boundaries.append(current_boundary)
            current_boundary = False
        elif ch in SEPARATORS:
            current_boundary = True
        elif ch in PUNCTUATION:
            current_boundary = True
    
    return indices, boundaries

def indices_to_text(indices):
    """Convert list of GP indices to runeglish text."""
    return ''.join(IDX_TO_LATIN.get(i, '?') for i in indices)

def compute_ioc(indices):
    """Compute Index of Coincidence."""
    if len(indices) < 2:
        return 0
    freq = Counter(indices)
    n = len(indices)
    numerator = sum(f * (f - 1) for f in freq.values())
    denominator = n * (n - 1)
    if denominator == 0:
        return 0
    return (numerator / denominator) * 29  # normalized for 29-letter alphabet

def english_score(text):
    """Score text based on common English words and patterns."""
    text_upper = text.upper()
    score = 0
    
    # Common English words (weighted)
    common_words = {
        'THE': 10, 'AND': 8, 'THAT': 7, 'THIS': 7, 'WITH': 7,
        'FROM': 6, 'HAVE': 6, 'WILL': 6, 'YOUR': 6, 'WHAT': 6,
        'WHICH': 6, 'THEIR': 6, 'THERE': 6, 'WITHIN': 7, 'BEING': 5,
        'NOT': 5, 'ARE': 5, 'FOR': 5, 'ALL': 5, 'BUT': 4,
        'EACH': 4, 'THEY': 4, 'WE': 3, 'IS': 3, 'IT': 3,
        'TO': 3, 'OF': 3, 'IN': 3, 'AN': 3, 'OR': 3,
        'A ': 2, 'I ': 2,
        # Cicada-specific
        'WISDOM': 10, 'PRIMES': 10, 'SACRED': 10, 'DIVINITY': 10,
        'KOAN': 8, 'INSTRUCTION': 10, 'WARNING': 8, 'PILGRIM': 8,
        'TRUTH': 8, 'CIRCUMFERENCE': 10, 'TOTIENT': 10, 'PARABLE': 8,
        'CONSUMPTION': 8, 'PRESERVATION': 8, 'ADHERENCE': 8,
        'WELCOME': 8, 'JOURNEY': 8, 'EMERGE': 6, 'INSTAR': 8,
        'END': 4, 'DEEP': 4, 'WEB': 4, 'PAGE': 4,
        'BELIEVE': 6, 'NOTHING': 6, 'YOURSELF': 6, 'SELF': 4,
    }
    
    for word, weight in common_words.items():
        count = text_upper.count(word)
        score += count * weight
    
    # Penalize unlikely patterns
    unlikely = ['QQ', 'ZZ', 'XX', 'QX', 'JJ', 'VV', 'QZ', 'XZ']
    for pat in unlikely:
        if pat in text_upper:
            score -= 5
    
    return score

def text_to_indices(text):
    """Convert plaintext to GP indices."""
    text = text.upper()
    indices = []
    i = 0
    while i < len(text):
        # Try digraphs first
        matched = False
        if i + 2 <= len(text):
            digraph = text[i:i+2]
            if digraph in LATIN_TO_IDX:
                indices.append(LATIN_TO_IDX[digraph])
                i += 2
                matched = True
        if not matched and i + 3 <= len(text):
            trigraph = text[i:i+3]
            if trigraph == 'ING':
                indices.append(21)  # NG/ING
                i += 3
                matched = True
        if not matched:
            ch = text[i]
            if ch in LATIN_TO_IDX:
                indices.append(LATIN_TO_IDX[ch])
                i += 1
            elif ch == 'K':
                indices.append(LATIN_TO_IDX['C'])  # K=C in GP
                i += 1
            elif ch == 'V':
                indices.append(LATIN_TO_IDX['U'])  # V=U in GP
                i += 1
            elif ch == 'Q':
                indices.append(LATIN_TO_IDX['C'])  # Q≈C
                i += 1
            elif ch == 'Z':
                indices.append(LATIN_TO_IDX['S'])  # Z≈S
                i += 1
            else:
                i += 1  # skip non-GP chars
    return indices

# ==================== CIPHER METHODS ====================

def phi_prime_decrypt(cipher, start_prime_idx=0, use_literal_f=True, operation='sub'):
    """φ(prime) cipher decryption. Proven on Pages 55, 73."""
    primes = generate_primes(len(cipher) + start_prime_idx + 100)
    result = []
    key_idx = start_prime_idx
    
    for c in cipher:
        if use_literal_f and c == 0:  # ᚠ = F
            result.append(0)  # Literal F, don't increment key
            continue
        
        phi_val = primes[key_idx] - 1  # φ(p) = p-1 for primes
        key = phi_val % 29
        
        if operation == 'sub':
            plain = (c - key) % 29
        else:  # add
            plain = (c + key) % 29
        
        result.append(plain)
        key_idx += 1
    
    return result

def vigenere_decrypt(cipher, key_indices, operation='sub'):
    """Vigenère-style decryption with repeating key."""
    result = []
    key_len = len(key_indices)
    for i, c in enumerate(cipher):
        k = key_indices[i % key_len]
        if operation == 'sub':
            plain = (c - k) % 29
        elif operation == 'add':
            plain = (c + k) % 29
        elif operation == 'beaufort':
            plain = (k - c) % 29
        result.append(plain)
    return result

def running_key_decrypt(cipher, key_stream, operation='sub'):
    """Running key decryption using a text stream as key."""
    result = []
    key_len = len(key_stream)
    for i, c in enumerate(cipher):
        if i >= key_len:
            break
        k = key_stream[i]
        if operation == 'sub':
            plain = (c - k) % 29
        elif operation == 'add':
            plain = (c + k) % 29
        elif operation == 'beaufort':
            plain = (k - c) % 29
        result.append(plain)
    return result

def caesar_decrypt(cipher, shift):
    """Simple Caesar shift."""
    return [(c - shift) % 29 for c in cipher]

def autokey_decrypt(cipher, primer, operation='sub'):
    """Autokey cipher decryption."""
    result = []
    key_stream = list(primer)
    
    for i, c in enumerate(cipher):
        if i < len(key_stream):
            k = key_stream[i]
        else:
            break
        
        if operation == 'sub':
            p = (c - k) % 29
        elif operation == 'add':
            p = (c + k) % 29
        elif operation == 'beaufort':
            p = (k - c) % 29
        
        result.append(p)
        key_stream.append(p)  # Autokey: plaintext extends key
    
    return result

# ==================== KNOWN KEYS ====================

KNOWN_KEYWORDS = {
    'DIVINITY': text_to_indices('DIVINITY'),
    'FIRFUMFERENFE': text_to_indices('FIRFUMFERENFE'),
    'YAHEOOPYJ': [26, 24, 8, 18, 3, 3, 13, 26, 11],
    'CABAL': text_to_indices('CABAL'),
    'SHADOWS': text_to_indices('SHADOWS'),
    'VOID': text_to_indices('VOID'),
    'AETHEREAL': text_to_indices('AETHEREAL'),
    'CARNAL': text_to_indices('CARNAL'),
    'ANALOG': text_to_indices('ANALOG'),
    'MOURNFUL': text_to_indices('MOURNFUL'),
    'OBSCURA': text_to_indices('OBSCURA'),
    'MOBIUS': text_to_indices('MOBIUS'),
    'ENCRYPTION': text_to_indices('ENCRYPTION'),
    'TOTIENT': text_to_indices('TOTIENT'),
    'PRIMES': text_to_indices('PRIMES'),
    'WISDOM': text_to_indices('WISDOM'),
    'SACRED': text_to_indices('SACRED'),
    'CICADA': text_to_indices('CICADA'),
    'KOAN': text_to_indices('KOAN'),
    'DEOR': text_to_indices('DEOR'),
    'ENCRYPT': text_to_indices('ENCRYPT'),
    'INSTAR': text_to_indices('INSTAR'),
    'SELF': text_to_indices('SELF'),
    'RELIANCE': text_to_indices('RELIANCE'),
    'PILGRIM': text_to_indices('PILGRIM'),
}

# Page 63 grid keyword combos
KNOWN_KEYWORDS['VOIDCARNAL'] = text_to_indices('VOIDCARNAL')
KNOWN_KEYWORDS['AETHEREALCABAL'] = text_to_indices('AETHEREALCABAL')
KNOWN_KEYWORDS['SHADOWSVOID'] = text_to_indices('SHADOWSVOID')

# Number sequences from Page 63
KNOWN_KEYWORDS['NUMS_ROW1'] = [272 % 29, 138 % 29, 131 % 29, 151 % 29]  # [11, 22, 15, 6]
KNOWN_KEYWORDS['NUMS_COL1'] = [272 % 29, 366 % 29, 226 % 29, 18, 151 % 29]  # [11, 18, 23, 18, 6]

# Known page-specific keys that produce high IoC
PAGE_KEYWORDS_21_30 = {
    21: ('CABAL', 'beaufort'),
    22: ('DIVINITY', 'beaufort'),
    23: ('ENCRYPTION', 'add'),
    24: ('OBSCURA', 'beaufort'),
    25: ('CABAL', 'beaufort'),
    26: ('ENCRYPT', 'add'),
    27: ('SHADOWS', 'add'),
    28: ('DEOR', 'sub'),
    29: ('TOTIENT', 'beaufort'),
    30: ('MOURNFUL', 'add'),
}

# Caesar shifts for pages 31-54
CAESAR_SHIFTS = {
    31: 15, 32: 11, 33: 28, 34: 14, 35: 23,
    36: 2, 37: 22, 38: 6, 39: 7, 40: 0,
    41: 13, 42: 5, 43: 23, 44: 5, 45: 20,
    46: 22, 47: 23, 48: 11, 49: 8, 50: 6,
    51: 19, 52: 28, 53: 4, 54: 13,
}

# ==================== LOAD SELF-RELIANCE TEXT ====================

def load_self_reliance():
    """Load Emerson's Self-Reliance as a GP index stream."""
    sr_path = Path(r"c:\Users\tyler\Repos\Cicada3301\self_reliance.txt")
    if not sr_path.exists():
        sr_path = Path(r"c:\Users\tyler\Repos\Cicada3301\Tools\emerson_self_reliance.txt")
    if not sr_path.exists():
        return []
    
    text = sr_path.read_text(encoding='utf-8', errors='ignore')
    # Clean: only keep alphabetical chars
    clean = re.sub(r'[^a-zA-Z ]', '', text)
    return text_to_indices(clean)

def load_solved_plaintext():
    """Load all solved page plaintexts as a continuous GP index stream."""
    solved_texts = [
        "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH DO NOT EDIT OR CHANGE THIS BOOK OR THE MESSAGE CONTAINED WITHIN EITHER THE WORDS OR THEIR NUMBERS FOR ALL IS SACRED",
        "WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE IT IS A NECESSARY ONE ALONG THE WAY YOU WILL FIND AN END TO ALL STRUGGLE AND SUFFERING YOUR INNOCENCE YOUR ILLUSIONS YOUR CERTAINTY AND YOUR REALITY ULTIMATELY YOU WILL DISCOVER AN END TO SELF",
        "IT IS THROUGH THIS PILGRIMAGE THAT WE SHAPE OURSELVES AND OUR REALITIES JOURNEY DEEP WITHIN AND YOU WILL ARRIVE OUTSIDE LIKE THE INSTAR IT IS ONLY THROUGH GOING WITHIN THAT WE MAY EMERGE WISDOM YOU ARE A BEING UNTO YOURSELF YOU ARE A LAW UNTO YOURSELF EACH INTELLIGENCE IS HOLY FOR ALL THAT LIVES IS HOLY AN INSTRUCTION COMMAND YOUR OWN SELF",
        "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED",
        "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER HE WENT TO THE DOOR OF THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER THE STUDENT TOLD THE MASTER HIS NAME THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE CALLED WHO ARE YOU WHO WISHES TO STUDY HERE HE ASKED AGAIN THE MAN THOUGHT FOR A MOMENT AND REPLIED I AM A PROFESSOR THAT IS WHAT YOU DO NOT WHO YOU ARE REPLIED THE MASTER WHO ARE YOU WHO WISHES TO STUDY HERE CONFUSED THE MAN THOUGHT SOME MORE FINALLY HE ANSWERED I AM A HUMAN BEING THAT IS ONLY YOUR SPECIES NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE ASKED THE MASTER AGAIN AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY THAT IS MERELY WHAT YOU ARE NOT WHO YOU ARE WHO ARE YOU WHO WISHES TO STUDY HERE THE MAN WAS GETTING IRRITATED I AM HE STARTED BUT HE COULD NOT THINK OF ANYTHING ELSE TO SAY SO HE TRAILED OFF AFTER A LONG PAUSE THE MASTER REPLIED THEN YOU ARE WELCOME TO COME STUDY AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY",
        "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY CONSUMPTION WE CONSUME TOO MUCH BECAUSE WE BELIEVE THE FOLLOWING TWO ERRORS WITHIN THE DECEPTION WE DO NOT HAVE ENOUGH OR THERE IS NOT ENOUGH WE HAVE WHAT WE HAVE NOW BY LUCK AND WE WILL NOT BE STRONG ENOUGH LATER TO OBTAIN WHAT WE NEED MOST THINGS ARE NOT WORTH CONSUMING PRESERVATION WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK IF WE LOSE THEM WE WILL NOT BE STRONG ENOUGH TO GAIN THEM AGAIN THIS IS THE DECEPTION MOST THINGS ARE NOT WORTH PRESERVING ADHERENCE WE FOLLOW DOGMA SO THAT WE CAN BELONG AND BE RIGHT OR WE FOLLOW REASON SO WE CAN BELONG AND BE RIGHT THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH IT IS THE BEHAVIORS OF CONSUMPTION PRESERVATION AND ADHERENCE THAT HAVE US LOSE OUR PRIMALITY AND THUS OUR DIVINITY SOME WISDOM AMASS GREAT WEALTH NEVER BECOME ATTACHED TO WHAT YOU OWN BE PREPARED TO DESTROY ALL THAT YOU OWN AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY",
        "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT THE MASTER SAID IT IS A VOICE INSIDE YOUR HEAD I DO NOT HAVE A VOICE IN MY HEAD THOUGHT THE STUDENT AND HE RAISED HIS HAND TO TELL THE MASTER THE MASTER STOPPED THE STUDENT AND SAID THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD IS THE I AND THE STUDENTS WERE ENLIGHTENED",
        "AN INSTRUCTION QUESTION ALL THINGS DISCOVER TRUTH INSIDE YOURSELF FOLLOW YOUR TRUTH IMPOSE NOTHING ON OTHERS",
        # Pages 55/73
        "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE",
        # Page 56
        "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE",
        # Page 59
        "A WARNING BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE TEST THE KNOWLEDGE FIND YOUR TRUTH EXPERIENCE YOUR DEATH",
        # Page 63 
        "SOME WISDOM THE PRIMES ARE SACRED THE TOTIENT FUNCTION IS SACRED ALL THINGS SHOULD BE ENCRYPTED",
        # Page 64
        "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER",
        # Page 68
        "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES THREE BEHAVIORS WHICH CAUSE THE LOSS OF DIVINITY",
    ]
    
    combined = ' '.join(solved_texts)
    return text_to_indices(combined)

# ==================== MAIN ATTACK FUNCTIONS ====================

def attack_phi_prime(page_num, cipher):
    """Test φ(prime) cipher with various parameters."""
    results = []
    
    for start_idx in range(20):  # Try starting at different prime indices
        for use_f in [True, False]:
            for op in ['sub', 'add']:
                plain = phi_prime_decrypt(cipher, start_idx, use_f, op)
                text = indices_to_text(plain)
                ioc = compute_ioc(plain)
                score = english_score(text)
                
                if score > 20 or ioc > 1.5:
                    results.append({
                        'method': f'phi_prime(start={start_idx}, f_skip={use_f}, op={op})',
                        'text': text[:200],
                        'ioc': ioc,
                        'score': score,
                        'plain': plain,
                    })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

def attack_running_key(page_num, cipher):
    """Test running key with Self-Reliance and solved plaintexts."""
    results = []
    
    sr_key = load_self_reliance()
    solved_key = load_solved_plaintext()
    
    key_sources = {
        'Self-Reliance': sr_key,
        'Solved_Pages': solved_key,
    }
    
    for key_name, key_stream in key_sources.items():
        if not key_stream or len(key_stream) < len(cipher):
            continue
        
        # Try different starting offsets in the key text
        for offset in range(0, min(500, len(key_stream) - len(cipher)), 50):
            key_slice = key_stream[offset:offset + len(cipher)]
            
            for op in ['sub', 'add', 'beaufort']:
                plain = running_key_decrypt(cipher, key_slice, op)
                text = indices_to_text(plain)
                ioc = compute_ioc(plain)
                score = english_score(text)
                
                if score > 15 or ioc > 1.5:
                    results.append({
                        'method': f'running_key({key_name}, offset={offset}, op={op})',
                        'text': text[:200],
                        'ioc': ioc,
                        'score': score,
                    })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

def attack_vigenere_keywords(page_num, cipher):
    """Test all known keywords with all operations."""
    results = []
    
    for key_name, key_indices in KNOWN_KEYWORDS.items():
        for op in ['sub', 'add', 'beaufort']:
            plain = vigenere_decrypt(cipher, key_indices, op)
            text = indices_to_text(plain)
            ioc = compute_ioc(plain)
            score = english_score(text)
            
            if score > 15 or ioc > 1.5:
                results.append({
                    'method': f'vigenere({key_name}, op={op})',
                    'text': text[:200],
                    'ioc': ioc,
                    'score': score,
                    'plain': plain,
                })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

def attack_multi_pass(page_num, cipher):
    """Test double encryption: first known key, then second key."""
    results = []
    
    # For pages 21-30: Apply known first-pass key, then try second pass
    if page_num in PAGE_KEYWORDS_21_30:
        keyword, first_op = PAGE_KEYWORDS_21_30[page_num]
        first_key = KNOWN_KEYWORDS[keyword.upper()]
        
        first_pass = vigenere_decrypt(cipher, first_key, first_op)
        
        # Now try second pass with all keywords
        for key2_name, key2_indices in KNOWN_KEYWORDS.items():
            for op2 in ['sub', 'add', 'beaufort']:
                second_pass = vigenere_decrypt(first_pass, key2_indices, op2)
                text = indices_to_text(second_pass)
                ioc = compute_ioc(second_pass)
                score = english_score(text)
                
                if score > 20:
                    results.append({
                        'method': f'multi_pass({keyword}/{first_op} → {key2_name}/{op2})',
                        'text': text[:200],
                        'ioc': ioc,
                        'score': score,
                    })
        
        # Also try autokey after first pass
        for primer_name, primer in KNOWN_KEYWORDS.items():
            for op2 in ['sub', 'add', 'beaufort']:
                ak_result = autokey_decrypt(first_pass, primer, op2)
                text = indices_to_text(ak_result)
                ioc = compute_ioc(ak_result)
                score = english_score(text)
                
                if score > 20:
                    results.append({
                        'method': f'multipass({keyword}/{first_op} → autokey({primer_name}/{op2}))',
                        'text': text[:200],
                        'ioc': ioc,
                        'score': score,
                    })
    
    # For pages 31-54: Apply Caesar, then try Vigenère
    if page_num in CAESAR_SHIFTS:
        shift = CAESAR_SHIFTS[page_num]
        caesar_result = caesar_decrypt(cipher, shift)
        
        for key_name, key_indices in KNOWN_KEYWORDS.items():
            for op in ['sub', 'add', 'beaufort']:
                second_pass = vigenere_decrypt(caesar_result, key_indices, op)
                text = indices_to_text(second_pass)
                ioc = compute_ioc(second_pass)
                score = english_score(text)
                
                if score > 20:
                    results.append({
                        'method': f'multipass(caesar_{shift} → {key_name}/{op})',
                        'text': text[:200],
                        'ioc': ioc,
                        'score': score,
                    })
        
        # Also try running key after Caesar
        sr_key = load_self_reliance()
        if sr_key and len(sr_key) >= len(cipher):
            for offset in range(0, min(300, len(sr_key) - len(cipher)), 100):
                key_slice = sr_key[offset:offset + len(cipher)]
                for op in ['sub', 'add', 'beaufort']:
                    plain = running_key_decrypt(caesar_result, key_slice, op)
                    text = indices_to_text(plain)
                    ioc = compute_ioc(plain)
                    score = english_score(text)
                    
                    if score > 20:
                        results.append({
                            'method': f'multipass(caesar_{shift} → SR_running[{offset}]/{op})',
                            'text': text[:200],
                            'ioc': ioc,
                            'score': score,
                        })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

def attack_autokey(page_num, cipher):
    """Test autokey cipher with known primer words."""
    results = []
    
    for primer_name, primer in KNOWN_KEYWORDS.items():
        for op in ['sub', 'add', 'beaufort']:
            plain = autokey_decrypt(cipher, primer, op)
            text = indices_to_text(plain)
            ioc = compute_ioc(plain)
            score = english_score(text)
            
            if score > 15 or ioc > 1.5:
                results.append({
                    'method': f'autokey({primer_name}, op={op})',
                    'text': text[:200],
                    'ioc': ioc,
                    'score': score,
                })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]

def analyze_word_boundaries(page_num, cipher, boundaries):
    """For pages with word separators, analyze word-level patterns."""
    if not boundaries:
        return []
    
    # Extract words
    words = []
    current_word = []
    for i, idx in enumerate(cipher):
        if boundaries[i] and current_word:
            words.append(current_word)
            current_word = [idx]
        else:
            current_word.append(idx)
    if current_word:
        words.append(current_word)
    
    # Apply Caesar if known
    shift = CAESAR_SHIFTS.get(page_num, 0)
    shifted_words = []
    for word in words:
        shifted_words.append([(v - shift) % 29 for v in word])
    
    # Convert each word to text
    word_texts = [indices_to_text(w) for w in shifted_words]
    
    # Look for recognizable English words
    english_words_3301 = {
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
        'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'HAD',
        'ITS', 'LET', 'SAY', 'SHE', 'HIM', 'HOW', 'MAY', 'OLD',
        'NEW', 'NOW', 'WAY', 'WHO', 'DID', 'GET', 'SET', 'MAN',
        'BIG', 'END', 'WHY', 'USE', 'OWN', 'CAN', 'RUN', 'DAY',
        'THAT', 'WITH', 'THIS', 'FROM', 'THEY', 'HAVE', 'WILL',
        'EACH', 'BEEN', 'THEM', 'THAN', 'WHAT', 'YOUR', 'WHEN',
        'SOME', 'MAKE', 'LIKE', 'LONG', 'MANY', 'VERY', 'MUCH',
        'MOST', 'ONLY', 'OVER', 'SUCH', 'TAKE', 'THAN', 'FIND',
        'SHOULD', 'WHICH', 'THEIR', 'THERE', 'THESE', 'THOSE',
        'COULD', 'WOULD', 'ABOUT', 'WHERE', 'NEVER', 'BEING',
        'WITHIN', 'WISDOM', 'SACRED', 'PRIMES', 'TRUTH', 'SELF',
        'A', 'I', 'IS', 'IN', 'IT', 'OF', 'TO', 'WE', 'AN', 'OR',
        'IF', 'DO', 'NO', 'SO', 'UP', 'BE', 'BY', 'ON', 'AS',
    }
    
    matched = 0
    matched_words = []
    for wt in word_texts:
        if wt in english_words_3301:
            matched += 1
            matched_words.append(wt)
    
    return {
        'total_words': len(word_texts),
        'matched_english': matched,
        'match_ratio': matched / max(1, len(word_texts)),
        'matched_words': matched_words,
        'all_words': word_texts[:50],  # first 50 words
        'caesar_shift': shift,
    }

# ==================== MAIN EXECUTION ====================

def main():
    print("=" * 80)
    print("COMPREHENSIVE LIBER PRIMUS SOLVER")
    print("=" * 80)
    
    # Pages to solve
    unsolved_pages = list(range(18, 55)) + [58, 60, 61, 62, 67, 71, 72]
    
    all_results = {}
    best_overall = []
    
    for page_num in unsolved_pages:
        cipher, boundaries = load_runes(page_num)
        if cipher is None:
            print(f"\nPage {page_num}: No runes file found, skipping")
            continue
        
        print(f"\n{'='*60}")
        print(f"PAGE {page_num} ({len(cipher)} runes)")
        print(f"{'='*60}")
        
        page_results = []
        
        # 1. φ(prime) cipher
        print(f"  Testing φ(prime) cipher...")
        phi_results = attack_phi_prime(page_num, cipher)
        page_results.extend(phi_results)
        
        # 2. Running key
        print(f"  Testing running key (Self-Reliance + Solved)...")
        rk_results = attack_running_key(page_num, cipher)
        page_results.extend(rk_results)
        
        # 3. Vigenère keywords
        print(f"  Testing Vigenère keywords...")
        vig_results = attack_vigenere_keywords(page_num, cipher)
        page_results.extend(vig_results)
        
        # 4. Multi-pass
        print(f"  Testing multi-pass ciphers...")
        mp_results = attack_multi_pass(page_num, cipher)
        page_results.extend(mp_results)
        
        # 5. Autokey
        print(f"  Testing autokey...")
        ak_results = attack_autokey(page_num, cipher)
        page_results.extend(ak_results)
        
        # 6. Word boundary analysis (if applicable)
        if boundaries and any(boundaries):
            wb_info = analyze_word_boundaries(page_num, cipher, boundaries)
            if wb_info and wb_info['match_ratio'] > 0.05:
                print(f"  Word analysis: {wb_info['matched_english']}/{wb_info['total_words']} words matched")
                print(f"    Matched: {wb_info['matched_words'][:20]}")
                print(f"    Sample: {wb_info['all_words'][:20]}")
        
        # Sort and display best results
        page_results.sort(key=lambda x: x['score'], reverse=True)
        
        if page_results:
            best = page_results[0]
            print(f"\n  ** BEST RESULT: score={best['score']}, IoC={best['ioc']:.4f}")
            print(f"     Method: {best['method']}")
            print(f"     Text: {best['text'][:150]}")
            
            if best['score'] > 30:
                best_overall.append((page_num, best))
            
            # Show top 3
            for i, r in enumerate(page_results[:3]):
                if i > 0:
                    print(f"  #{i+1}: score={r['score']}, IoC={r['ioc']:.4f} | {r['method']}")
                    print(f"       {r['text'][:100]}")
        else:
            print(f"  No promising results found")
        
        all_results[page_num] = page_results
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 80)
    print("SUMMARY - BEST RESULTS ACROSS ALL PAGES")
    print("=" * 80)
    
    if best_overall:
        best_overall.sort(key=lambda x: x[1]['score'], reverse=True)
        for page_num, result in best_overall:
            print(f"\n  Page {page_num}: score={result['score']}, IoC={result['ioc']:.4f}")
            print(f"    Method: {result['method']}")
            print(f"    Text: {result['text'][:200]}")
    else:
        print("  No high-confidence results found across any page.")
    
    # Save detailed results
    output_path = Path(r"c:\Users\tyler\Repos\Cicada3301\comprehensive_solver_results.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("COMPREHENSIVE SOLVER RESULTS\n")
        f.write("=" * 80 + "\n\n")
        
        for page_num in sorted(all_results.keys()):
            results = all_results[page_num]
            f.write(f"\nPAGE {page_num}\n")
            f.write("-" * 40 + "\n")
            
            for r in results[:5]:
                f.write(f"  Score: {r['score']}, IoC: {r['ioc']:.4f}\n")
                f.write(f"  Method: {r['method']}\n")
                f.write(f"  Text: {r['text'][:300]}\n\n")
    
    print(f"\nDetailed results saved to: {output_path}")

if __name__ == '__main__':
    main()
