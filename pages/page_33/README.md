# Liber Primus - Page 33

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 214  
**Image File:** 33.jpg

---

## Images

| File | Description |
|------|-------------|
| [33.jpg](images/33.jpg) | Original scan |


## Rune Text

```
ᛞᛇ-ᛉᚳᚠᛁᚪᚹᚻᚷ.ᛇᛟ-ᚠᛏᛖᛟᛠᚪ

ᛡᛋᚷ-ᚣᛠᚾᚦᚫᚱ-ᚩᛡᛗ-ᚹᛉᛗ-ᚣ

ᛞᛒᛏᚱ-ᚢᛄᚻ-ᚫᛟ-ᛡᛝᚹᚻᛋᚠᛡ-ᛚᚦ

ᛏ-ᛁᚹᛏ-ᚩᚢᚾᚹᛗᛚ-ᛋᚦᛠᚹᛄ-ᚪᛄᚫᚷᚣᛗᚹᛞ-

ᛈᛡ-ᛖᛄᚹ-ᛖᚢ-ᚻᚹ-ᛝᛁ-ᛋᚫᚷ-ᛄᛚ.

&
ᛝᚦᛇ-ᛁᚠᚳᛟᛇ.ᛞᛒᚣᛡᚣᚢ-ᚣᚾᚦᚱᛖ

ᛗᛁ-ᛇᛞᚱᚹ-ᛉᛒᚻ-ᚳᛄᛡᚪ-ᚾᚹ-ᚾᛗ-ᚠ

ᛇᛁ-ᛇᚪ-ᚩᛋᛒᛟ-ᛏᛄ-ᛈ-ᛖᛈᛄᚩᚹᚢᛠ

ᛝᚹ-ᛗᚳᚩᛏᛏᚠᚢᛄ-ᛞᛠᛉᚩ-ᛉᚦᚷᛞ-ᛒᚩᛏᛚ

ᛇᛁᛒᛡᚪ-ᛖᚠᛠᚢᛖ-ᛈᛋᚹᛞᛞ-ᛋᛡ-ᚹᚦᛞᛋ-ᛝ

ᛄ-ᛚᚷᚢᛡ-ᚾᛉᚠ-ᚱᚪᚣᛗᚠᚦᚻ-ᚱᚪᚱ-ᚫᚪᚷᛟᛞ-ᛒ

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
thaeththeathaeuaeththetheaiaecleaththththetheadngtheouiothealeceoaethethuoetheoa
eolengiomealeathhumtheotheoeeathiaethxcoaleommcaxlrnrtheththeowbwsmfheouioiljnod
ileopiletheabmrcaethealeoaeoetheamthawathrththeaommjleaelealealeogaeodsthleaseth
ealeotdtheangletheouiomthdthxrnggtheoeathethjwyuioioeoothetheodaleaetileathae
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 71
- **Key:** `[21, 16, 12, 3, 1, 8, 28, 6, 12, 4, 10, 4, 27, 17, 8, 26, 23, 4, 28, 13, 4, 24, 26, 20, 0, 26, 10, 11, 25, 7, 6, 16, 17, 27, 3, 28, 11, 21, 5, 9, 19, 23, 21, 5, 19, 24, 13, 3, 9, 9, 28, 4, 26, 11, 16, 17, 1, 22, 8, 17, 17, 8, 13, 13, 6, 8, 9, 14, 15, 23, 21]`
