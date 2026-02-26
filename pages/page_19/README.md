# Liber Primus - Page 19

**Status:** ✅ SOLVED

---

## Overview

**Description:** Standard content page  
**Rune Count:** 271  
**Image File:** 19.jpg

---

## Images

| File | Description |
|------|-------------|
| [19.jpg](images/19.jpg) | Original scan |


## Rune Text

```
ᚾᚩᛟᚾᚠ-ᚩᛁᚠᚢᛋᚾ-ᛞᚹᛠᛇᛈ-ᚱᚩᚩᛄ-ᚪᛟ-ᛇᛠ

ᛄᛁ-ᛟᛄᛞᚢᚳᛝᚩ-ᚱᛝᛋ-ᛄᛁᛈᛉᛖ-ᛞᛁᚾᛗᛗᚳ

.ᛉᚩᛁᛄᛞᚳ-ᚢᚪᛇ-ᚦᛡᛇᚻᛠᚣ-ᛠᚻ-ᚠᚩ-ᛡ

ᛠᛋᛟᚪ-ᚹ-ᚫᚻᚩᛄᚢᚱᚩᚣ-ᛏᚫᚪᛡᚷ-ᛄᛚᛄ-ᛝᛏ

ᛖᛒᛚᛉᚻ-ᚱᚩᚫᛇᛈᛄᛠ-ᚳᛈᛚᚣᛈ-ᚪᛠᚻᚻᛋ

ᚫ-ᚩᛝᚹ-ᛋᛞᚠᚳᛠ-ᚩᛇᚫᚪᚩᚹᛗᚪ-ᚣᚫᚷᚫᛄᚱᚹ

ᛞ-ᚱ-ᚦᚷᚳᚹ-ᚾᚷᛡ-ᛚᛒᚳ-ᛄᚷᚹᚹ.ᚱᛁᚠᛏ-ᚠᛚ-ᛋᛄ

ᛚᚪᛄᚱᛏ-ᛞᚷᚫᛠᚠᛉᛞ-ᚫᚷᚻᛏ-ᛗᚣᛈ-ᛏᛒᛟ

ᛝ-ᛄᛋᚾ-ᛝᛁᚹ-ᚦ-ᛠᛝᛞᚾᛟᚷᚫ-ᛁᛗ-ᛝᛉᚱᛞᛋ

ᛗ-ᚠᚫᚹ-ᛟᛋ-ᚦᛞᛞᛈᛝ-ᛞᛡᚷᛒ-ᚪᛟ.ᚦᛡᛒ-ᚪᚹ-

ᚾᛉᚫ-ᛚᛈᛁ-ᛒ-ᚠᚾᚠ-ᛡᚩᛏᛞᚾᛋᛖᚳᚻ-ᛖᚻ-ᚢᛟ-

ᚪᛖᛗᛝ-ᛠᚫ-ᛈᚩᚪᛞ-ᚠᚫᚻ-ᚠᛏᚦᛄᛚᛄᛒ-ᛗᛇ

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
daethhngtheaaeodtheailepealeooethuileathpcowaeththeaththttheouajmaethleoeatheath
efaeoenheofmnguimeatheodileaojyxhathiluileoealmolcxmeawpwatheoheahtleaaceoleatha
thdthgirtiltheatheoeodthaericxtheathetheaeomaleaththearilthththxaethetheocethceu
mleheagoexthiaeoththdoeteaaleaecdtpxotheotletaleawetthaththxauioleoeueomleartheo
ethewtheonthariotheatheoleoeooseooesenjeallatheaythoeujngoethghleayl
```

## Solution

- **Method:** Hill Climbing (Index of Coincidence / Bigram Scoring)
- **Key Length:** 83
- **Key:** `[15, 7, 20, 1, 8, 1, 11, 4, 27, 21, 7, 24, 26, 8, 23, 0, 5, 12, 20, 18, 22, 21, 2, 8, 12, 8, 9, 6, 20, 23, 9, 19, 1, 5, 19, 13, 24, 8, 1, 13, 23, 12, 20, 13, 17, 28, 22, 15, 1, 11, 9, 5, 5, 5, 2, 3, 23, 15, 12, 18, 7, 25, 18, 18, 1, 1, 15, 5, 5, 2, 25, 4, 14, 11, 18, 3, 6, 2, 22, 6, 15, 15, 4]`
