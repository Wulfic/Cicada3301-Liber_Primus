# Liber Primus - Page 22

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 131  
**Image File:** 22.jpg

---

## Images

| File | Description |
|------|-------------|
| [22.jpg](images/22.jpg) | Original scan |


## Rune Text

```
ᛝᛗ-ᛁᚷ-ᛄᚷ-ᚳᚩᚦᛖᚦᛄ-ᚣᚠ-ᚦᚳᛄᛡᛖᚢ-ᛉᛄ

ᚳᚻᛄᚱᛄ-ᚪᚻᚾᚦ-ᛚᚷ-ᚱᚦ.ᛒᚪᚩᛖᚢᛡᛄᚹᛏᚱᚹ

ᛟ-ᚦᚳᛗᚦᚠᚫᚻ-ᛡᚠᛠᚣᚪᚦᛚᛏᛒᚢᛝ-ᛖᛋᛗᚱ-

ᚪᚹᛒ-ᚹᛒᛗᚱᚾᛗᚻᛗᛁᚾᚪᛞ-ᛡᛖᚩ-ᚾᚹᛡ-ᚢᛄ

ᚦᛠ-ᛚᚳᚷᛚᛇ-ᛟᛠᛠᚪ.ᛇᛉᚣᚪ-ᚷᛏᚩ-ᛖ

ᚹᛒᛈᚷᛝᛒ.ᛡᚦᚠᛋᚾ-ᛒᚦᚠ-ᛇᛝᛠ-ᚠᚾᛉ.

&
$
```

---


## Cryptanalysis Status

This page has not yet been analyzed with the proven methodology.

### Recommended Next Steps
1. Run IoC analysis to find candidate key lengths
2. Test SUB mod 29 with top candidates
3. Verify 100% reversibility
4. Check for interleaving patterns
5. Document results


---

## Notes

*Add research notes, hypotheses, and observations here.*

---

## References

- [Master Solving Document](../../MASTER_SOLVING_DOCUMENT.md)
- [Gematria Primus](../../GEMATRIA_PRIMUS.md)

---

**Last Updated:** January 5, 2026


## Decrypted Text (Runeglish)

```text
ileothetheartheththeooethngluthhlealeoaeteaetheouilethytjeogthwtheantheththeathe
atheatheatheatheatheatheaileatheatheatheaththeaththeatheatheoealeatongthjtheajle
aleaththeothetheoealealeouleoaegtheooetheatheaileowdtheu
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[11, 28, 27, 4, 22, 4, 6, 28, 0, 0, 0, 9, 14, 7, 0, 13, 20, 26, 16, 22, 23, 12, 14, 25, 15, 17, 12, 6, 6, 26, 1, 10, 15, 15, 15, 9, 27, 16, 7, 18, 21, 9, 0, 14, 5, 27, 20, 13, 3, 17, 3, 27, 26, 6, 28, 27, 0, 24, 25, 0, 21, 14, 18, 28, 22, 8, 24, 20, 2, 25, 5, 18, 5, 18, 17, 2, 10, 17, 6, 20, 8, 10, 22]`
