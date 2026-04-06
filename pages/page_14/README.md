# Page 14 (LP2 14.jpg + LP2 15.jpg combined in runes.txt)

**Status:** ✅ SOLVED — Full voice koan decoded (Session 18)

## Important Note on Page Boundaries
Our `runes.txt` file contains the **COMBINED rune text from both LP2 pages 14.jpg and 15.jpg**. The complete voice koan spans both physical pages. The repo split them across page_14 and page_15, but page_14/runes.txt has all 320 runes (full koan). page_15/runes.txt contains DIFFERENT, UNSOLVED content.

## Full Plaintext (LP2 14.jpg + 15.jpg combined)
```
A KOAN: DURING A LESSON, THE MASTER EXPLAINED THE I:
"THE I IS THE VOICE OF THE CIRCUMFERENCE," HE SAID.
WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT, THE MASTER SAID
"IT IS A VOICE INSIDE YOUR HEAD."
"I DON'T HAVE A VOICE IN MY HEAD," THOUGHT THE STUDENT,
AND HE RAISED HIS HAND TO TELL THE MASTER.
THE MASTER STOPPED THE STUDENT, AND SAID
"THE VOICE THAT JUST SAID YOU HAVE NO VOICE IN YOUR HEAD, IS THE I."
AND THE STUDENTS WERE ENLIGHTENED.
```

## Method
- **Cipher:** Vigenère SUB mode: `plain = (cipher - key[ki % 13]) % 29`
- **Key:** FIRFUMFERENFE → GP indices `[0, 10, 4, 0, 1, 19, 0, 18, 4, 18, 9, 0, 18]`
- **F-skip rule (corrected Session 18):** F-skip ONLY when BOTH cipher=ᚠ(0) AND key[ki%13]=F(0). When cipher=ᚠ but key≠0, decode normally: plain=(0-key)%29.
- **Quote key-reset:** The key counter RESETS to position 7 (key[7]=E=18) at each opening `"` quote mark in the LP text. This explains the garbled decode in the middle section with naive continuous key. The garbled section decodes to "THE I IS THE VOICE OF THE CIRCUMFERENCE, HE SAID WHEN ASKED BY A STUDENT TO EXPLAIN WHAT THAT MEANT, THE MASTER SAID IT IS" with ki_start=7.

## Key Stats
- 320 runes, IoC=1.126 (consistent with Vigenère period 13 on 320 runes)
- 88 cipher words (including word-boundary separators from LP2 image)
- 10 singleton words in cipher text
- 3 F-skip positions (cipher=ᚠ with key=F)

## Cross-References
- LP2 reference transcript: `FIRFUMFERENFE` key confirmed, "Shift up forward Gematria" (= SUB mode, just different notation)
- page_15/runes.txt: UNSOLVED cipher text (IoC=1.04, NOT LP2 15.jpg content)
- P72 also uses FIRFUMFERENFE key → decodes to "A KOAN" (title header only)

