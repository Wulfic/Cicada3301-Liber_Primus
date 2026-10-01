#!/usr/bin/env python3
import json, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
PAGES = BASE / 'pages'
RUNE_TO_IDX = {
    'ᚠ': 0, 'ᚢ': 1, 'ᚦ': 2, 'ᚩ': 3, 'ᚱ': 4, 'ᚳ': 5, 'ᚷ': 6, 'ᚹ': 7,
    'ᚻ': 8, 'ᚾ': 9, 'ᛁ': 10, 'ᛄ': 11, 'ᛇ': 12, 'ᛈ': 13, 'ᛉ': 14, 'ᛋ': 15,
    'ᛏ': 16, 'ᛒ': 17, 'ᛖ': 18, 'ᛗ': 19, 'ᛚ': 20, 'ᛝ': 21, 'ᛟ': 22, 'ᛞ': 23,
    'ᚪ': 24, 'ᚫ': 25, 'ᚣ': 26, 'ᛡ': 27, 'ᛠ': 28,
}
IDX_TO_LETTER = [
    'F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S',
    'T','B','E','M','L','NG','OE','D','A','AE','Y','IO','EA'
]

def load_verified_keys():
    vk_path = DATA / 'verified_keys.json'
    if not vk_path.exists():
        return {}
    with open(vk_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_page_runes(pn):
    path = PAGES / f'page_{int(pn):02d}' / 'runes.txt'
    if not path.exists():
        return None
    return path.read_text(encoding='utf-8')


def extract_indices(text):
    return [RUNE_TO_IDX[ch] for ch in text if ch in RUNE_TO_IDX]


def decrypt_indices(indices, key, mode='sub'):
    kl = len(key)
    out = []
    for i,c in enumerate(indices):
        k = key[i % kl]
        if mode == 'sub':
            p = (c - k) % 29
        elif mode == 'add':
            p = (c + k) % 29
        elif mode == 'beaufort':
            p = (k - c) % 29
        else:
            raise ValueError(mode)
        out.append(p)
    return out


def indices_to_runeglish(indices):
    return ''.join(IDX_TO_LETTER[i] for i in indices)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: decrypt_page_with_verified_key.py <page_num> [mode=sub|add|beaufort]')
        sys.exit(1)
    pn = int(sys.argv[1])
    mode = sys.argv[2] if len(sys.argv) > 2 else 'sub'
    vks = load_verified_keys()
    key = vks.get(str(pn))
    if not key:
        print('No verified key for page', pn)
        sys.exit(2)
    text = load_page_runes(pn)
    if not text:
        print('No runes.txt for page', pn)
        sys.exit(3)
    cipher_indices = extract_indices(text)
    plain = decrypt_indices(cipher_indices, key, mode)
    print('Page', pn, 'mode', mode, 'keylen', len(key))
    runeglish = indices_to_runeglish(plain)
    print(runeglish)
    # Simple transliteration from Runeglish tokens to ASCII phonetics
    TOKENS = ['TH','NG','EO','OE','AE','IO','EA', 'F','U','O','R','C','G','W','H','N','I','J','P','X','S','T','B','E','M','L','A','Y']
    PHON = {
        'F':'f','U':'u','TH':'th','O':'o','R':'r','C':'c','G':'g','W':'w',
        'H':'h','N':'n','I':'i','J':'j','EO':'e','P':'p','X':'x','S':'s',
        'T':'t','B':'b','E':'e','M':'m','L':'l','NG':'ng','OE':'o','D':'d',
        'A':'a','AE':'ae','Y':'y','IO':'io','EA':'ea'
    }
    # Greedy parse
    i = 0
    translit = []
    s = runeglish
    while i < len(s):
        matched = False
        for tok in TOKENS:
            if s.startswith(tok, i):
                translit.append(PHON.get(tok, tok.lower()))
                i += len(tok)
                matched = True
                break
        if not matched:
            # fallback: consume one char
            translit.append(s[i].lower())
            i += 1
    print('\n-- Transliteration --')
    print(''.join(translit))
    # Attempt monoalphabetic substitution hillclimb on transliterated text
    try:
        sys.path.insert(0, str(BASE / 'tools'))
        import mono_sub_solver as mss
        cipher_text = ''.join(''.join(translit)).upper()
        # keep only A-Z
        cipher_text = ''.join(ch for ch in cipher_text if 'A' <= ch <= 'Z')
        if len(cipher_text) >= 20:
            corpus = mss.load_corpus_text()
            qg, floor = mss.build_quadgram(corpus if corpus else 'THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG')
            best_score = -1e12
            best_plain = None
            best_map = None
            for r in range(6):
                plain, mapping, score = mss.run_hillclimb(cipher_text, qg, floor, corpus, iters=20000)
                if score > best_score:
                    best_score = score
                    best_plain = plain
                    best_map = mapping
            print('\n-- Mono-sub Hillclimb Result --')
            print('score=', best_score)
            print(best_plain)
            try:
                print('mapping=', mss.pretty_map(best_map))
            except Exception:
                pass
    except Exception:
        pass
    # Try segmentation using the repository segmenter
    try:
        sys.path.insert(0, str(BASE / 'tools'))
        import solve_p21_30 as solver
        import segment_runeglish as seg
        solver.load_wordlist()
        # use the prime-chars segmentation algorithm on the runeglish string
        score, words = seg.segment_text(runeglish, solver.COMMON_WORDS, solver.gp_word_matches_english)
        print('\n-- Segmentation --')
        print('score=', score)
        print(' '.join(words))
    except Exception:
        pass
    
