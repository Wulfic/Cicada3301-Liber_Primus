# Liber Primus - Page 42

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 272  
**Image File:** 42.jpg

---

## Images

| File | Description |
|------|-------------|
| [42.jpg](images/42.jpg) | Original scan |


## Rune Text

```
ᛞ-ᛉᚾᛗᚦ-ᛁᛄᚱ-ᛈᛉᚢᚫᚦᛒᚠᛄᚦ-ᚠᚪᛝᛖ-ᚹᚹᚣ

ᛚᛇ-ᚢᚣ-ᚾᚱᚪ-ᛈᚾᚹ-ᛚᚾᛏᛚᚢᛒᚱᛝᚪᛋ-ᚫᛈ-ᛄᛚ

ᚢᚳᚷ-ᛚᛏᛄᚹᛈ-ᚫᛗᛚ-ᛉᛚᛗᛏᛞᚠᛈᛁ.ᚠᚳᚦ

ᛗᛄᚹᚱᚪᛚ-ᚩᛝᚱᚢᛈᚱᛟᛡ-ᚳᛉᚱ-ᛇᛏᚦᚾ-ᚱᛇᚫ

ᛞᛟᚻ-ᛒᚾᚣ-ᚠᛡᚪᛡᛖᚫᛞᛄᚢᛖ-ᚦᚱ-ᚩᛇᚱᛡ-

ᚣᛁᛉᛇᚻᚩᛠ-ᚫᚻᛡᛝᛠᚦ-ᚾᚣ-ᚾᚠᛁᛝ.ᛏ

ᚻᚹᚫ-ᛒᛇ-ᛡᚻᛉᛒ-ᛞᛝᚱᛄᚦᚻ-ᚪᚷᚣᛁᚠᚷ-ᛁᛏᛞ

ᛠᛒᚠᚩᛈ-ᛇᛡᛟᚹᚱᚾᚩᛏ-ᛋᚹᚢ.ᛖᛡᛖᛡᚦ-ᛉ

ᚪᚷᛈᚾ-ᛋᚱᚠᛞᛝᚻᛖᛄᛞ-ᛄᛡ-ᚱᚹ-ᚷᛝᚪᛒ-ᛄᛈ

ᛄ-ᛏᚠᛉ-ᚪᛄ-ᛁᚠᛉᚢᚩᚣᚻᚦ-ᚻᚾᛁᛒ-ᛡᛟᛡᛋᛈᚣ

ᛉ-ᛠᚢᛠᛚ-ᚠᛝᛗᚻ-ᚦᛒᚩ-ᛗᛚ-ᚩᛠᛋᚦᛠ-ᛇ

ᛋᛉ-ᚠᛗᛒ-ᚫᛋᛇᚾᛡᚾ-ᚢᚫᚹ-ᛞᛠᚢᚾᛝᚠᚾᛖᚫ

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
leolbthaeioletheoftheotheanoetheajbpthmthaybtheajileoleojfuieoeaoeppthathaeheath
ththeoiilethrngrheoealeoaththbetojlealeooeoaoaetheotheaenfwiooeomyroecthleatheai
leotheouttheaithaeheatheotheatheatthfuileoftheathathoioeoaetheatheoileatheanuilt
heathioeomtheothalethneotheoeftheoerththealthxgealioeojthnththhmpgptheoaoelethea
ilethdeatbearntheoethyiothawfbjwxtheaeothatheathdcuiotheoeojbbjtheaxslcaethaetht
heawtheath
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[3, 2, 18, 2, 0, 14, 13, 13, 24, 12, 18, 25, 0, 5, 27, 12, 22, 7, 22, 22, 7, 19, 23, 24, 1, 10, 6, 0, 21, 2, 25, 2, 28, 16, 8, 18, 4, 9, 1, 16, 23, 9, 25, 22, 12, 0, 9, 25, 28, 9, 27, 21, 14, 9, 5, 1, 15, 9, 0, 25, 18, 15, 24, 19, 21, 1, 11, 9, 22, 7, 17, 9, 19, 15, 8, 17, 21, 1, 5, 10, 1, 1, 10]`
