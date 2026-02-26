# Liber Primus - Page 52

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 179  
**Image File:** 52.jpg

---

## Images

| File | Description |
|------|-------------|
| [52.jpg](images/52.jpg) | Original scan |


## Rune Text

```
ᛇᚫᛠᚫᚣ-ᚢᛗᛈ-ᛉᛁᚢᚾᚩᛟᚾ-ᚷᛞᚦ-ᛡᚫᚹ-ᛞ

ᛟᛖᚱ-ᛗᚾᛖᚻᚷᛒᚢᛄ-ᚢᚦᛗᛖᛞᛝ-ᛒᚷᚣᚱ-ᛖ

ᛁᚢᛄ-ᚣᛡᛚᚢ-ᛄᛟ.ᛠᛉᚣᛇᚱ-ᚩᛈᛋᚳᚫᛗ

ᛇ-ᚾᛄ-ᛖᚠᛋ-ᛖᚠᚪᛝ-ᚢᛝᛄᛇᚷᚠᛝᚱᛁᚦ-ᛄᚢᚫ-

ᚣᛋᚠᛖᚢᛋᚫᚣᛠ-ᛁᛏᛟᚱᛏᛟᚩ-ᚷᚾᚻ-ᛞᛗᚩᚳ

ᛞᛖᛏ-ᚹᛉᛞᛚ-ᚩᚫᛄ-ᛇᚢᛒ-ᛗᛏ-ᛞᛗᛖ.ᛏ

ᛈᚹᛇᛋ-ᚹᛒᛇᚦ-ᚾᚻᚷᛄ-ᚱᛡᛞᛡᚦᚪᛁᛇᚫᛉᛚ-ᛇ

ᛠ-ᛡᚪᛄ-ᚻᚱ-ᚦᛈᛞᛄᛝᚩ-ᚷᚠᛇᛗᚳ-ᚻᛞᚩᛏᚳ

-ᚢᚱ-ᛈᚾ.

&
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
easheaththesthjaeaaethatheobratheoileatheodngtheoeatheoioaeththmtheaeonuilethaea
eoetheathealethuiodtheoyleatheothealeotheongmththealeaththeuieathtealetleongmthe
oetheathuioaeaexsheatheotheoxtheathaleatheotheathegleoileahecdtheontheothaetheth
thoeaeuiththeathoeottheauiottheahpatheoetheaeath
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[13, 10, 20, 26, 24, 28, 1, 27, 12, 28, 5, 14, 7, 20, 14, 4, 11, 14, 23, 1, 5, 11, 12, 27, 5, 17, 26, 24, 16, 4, 5, 2, 9, 18, 4, 23, 16, 21, 2, 15, 7, 14, 24, 17, 0, 10, 22, 24, 2, 24, 8, 9, 23, 26, 15, 6, 23, 2, 2, 15, 21, 3, 13, 22, 21, 10, 9, 6, 27, 16, 27, 17, 22, 9, 9, 2, 9, 10, 7, 9, 22, 2, 8]`
