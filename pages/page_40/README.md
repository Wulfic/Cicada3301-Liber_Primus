# Liber Primus - Page 40

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 231  
**Image File:** 40.jpg

---

## Images

| File | Description |
|------|-------------|
| [40.jpg](images/40.jpg) | Original scan |


## Rune Text

```
ᚠᚾᛗ-ᚣᚷᛞᚫᚻ.ᚪᛈᛉᚣᚻ-ᛇᛠᚩᛖ-ᛏᛝ

ᛠ-ᛚᛁᛏᚦᚠ-ᛗᚪᚳᛖ.ᛞᚳ-ᛏᚱᛟᚷᛠᚾ

ᚫᛒᚢᛖᛒᚢ-ᚦᚠᛟ-ᚷᛋᛟ-ᛁᛈ-ᛟᛉᛋᛒ-ᚹᛄᛒ

ᚣᛗᚢᛠ-ᚱᛁᚢᛟᛄᛁ-ᛗᛖᚫ-ᚱᛋᛉᛝ.ᛠᛈᛚ-

ᛞᚩᛚᛁᛉᛠᛝᛖᚱ-ᚾᛈᛖᚹᛡ-ᚾᛄᛏᚣ.ᛋᚩᛋ

ᛏᛝ-ᚢᚾᛇᚪ-ᛖᛏᚪᛄᚳᚣ-ᛟᛒ-ᛚᛋ-ᛒᛞᛄ-ᛁᛝᚣᛖ

ᚳ-ᛄᚻᛚᚣ-ᚷᚫᛚᛞ-ᛚᚫᛚᚦᛉ-ᛚ-ᛖᛉᚩᛉᛁᚳᚢᛗ

ᚾᚢ-ᚩᚾᛇ-ᚻᛡᛚᛇᚩᚫᚪ-ᚩᛟᚩ-ᚣᚱ-ᛖᚠᚢ.ᛁᚻ-ᛟᛚ

ᚾᛏ-ᚠᛞᚱᛠᚷ-ᛈᚩᛇᚩᛗᛠᛒ-ᛄᛡ-ᛋᛗᚠ-ᛏ

ᚠᚫᚩ-ᛟᚳᛚᛞᛡᛚ-ᚩᚳᛝᚢ-ᛈᚹᛏ-ᚷᚳᛋ-ᚢᛟᚷᚦ-

ᚠᛉᚠᛏ-ᚳᛋᛉᛟ-ᚷᚠᛉᚾᛞ-ᛒᛏᛠᛡ.ᛈᛡ

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
lejmtheootheagtheodeaiogrwoeththeoeruiththeeanngsuilenmanreoraeoetheoueoanthleat
heatheoththethethuilethotheoleoethetoetheomuiycthaeuththeatheoththetheotheodylea
etheodoeoealeathsthuileathatheathaetleaiothethaefnleathethoedoelethhealetheooeth
eoeoheaththoeheatheotheoeuiooeaueiomethotheaeuthethydfthleathaexpaeoeoelefaetheo
aththaejhetththiobathdsubtheocs
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[9, 20, 8, 7, 4, 11, 22, 6, 25, 7, 12, 14, 14, 13, 1, 26, 14, 9, 28, 26, 18, 27, 27, 27, 28, 9, 22, 3, 0, 24, 25, 24, 18, 21, 25, 8, 20, 16, 27, 6, 9, 13, 18, 27, 4, 0, 4, 3, 21, 27, 18, 13, 12, 24, 18, 5, 12, 15, 8, 16, 28, 26, 15, 8, 12, 20, 10, 0, 28, 0, 23, 1, 13, 2, 1, 10, 20, 18, 5, 16, 27, 8, 2]`
