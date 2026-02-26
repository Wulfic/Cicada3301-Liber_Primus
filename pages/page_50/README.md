# Liber Primus - Page 50

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 92  
**Image File:** 50.jpg

---

## Images

| File | Description |
|------|-------------|
| [50.jpg](images/50.jpg) | Original scan |


## Rune Text

```
ᚹᚹᛈ-ᚠᛡᛚᛉᛒᚾ-ᚳᛗᚾᚱᛗ-ᚻᚦᚫᛞᛄ-ᛒᛡᚫ-ᛇᚹ

ᛗᚢ-ᚪᛈᛡ-ᛈᛁᛄ-ᚪᚢᚾᛠᛖᛞᛗᚪ-ᛏᛟᛗ-ᛋᛞ

ᛝᚷᛚᛋᛞᛝ-ᛟ-ᛋᛄᛞ-ᛚᛟᚠᛄᚫᚠᚪ-ᛝᛟᚣᛈ-ᚣᚩ

ᛒᚷᚳᛖᛏᚹ-ᚪᛋᛒ-ᛗᛠᚣᛇᛗᚫᛚᚱ-ᚹᛇᛄᛒ-ᛈᛚᚠ

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
ethealeththeatheatheatheatheatheatheaileaththeatheaththeatheaththeatheatheatheat
heatheatheaileaththeatheatheatheaththeatheaththeatheatheatheaththeatheatheatheat
heaoeotheauthoe
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[18, 5, 14, 9, 9, 18, 12, 18, 7, 6, 17, 10, 2, 20, 6, 3, 23, 24, 9, 18, 17, 5, 13, 5, 17, 2, 22, 14, 25, 11, 11, 9, 25, 28, 7, 0, 16, 24, 17, 25, 14, 23, 17, 16, 21, 22, 4, 21, 5, 3, 22, 20, 13, 12, 21, 21, 20, 1, 9, 26, 27, 22, 22, 20, 27, 11, 24, 4, 15, 7, 3, 19, 14, 8, 22, 13, 18, 17, 0, 24, 13, 17, 26]`
