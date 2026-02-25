# Page 62 - SOLVED

## Title: WIDSOM (WISDOM)

## Cipher Method
- **Type:** Vigenère Subtraction with F-skip
- **Key:** DIVINITY = [23, 10, 1, 10, 9, 10, 16, 26]
- **Starting offset:** 3 (key begins at position 3 = I)
- **F-skip mask:** Positions 27, 49, 71, 120 are literal F (key doesn't advance)
  - F-mask binary: 010110001 (bit i = 1 means F at position f_positions[i] is literal)
  - F positions in cipher: [4, 27, 29, 49, 71, 76, 105, 111, 120]
- **Formula:** plaintext[i] = (cipher[i] - key[k % 8]) % 29, k++ for non-literal positions
  - For literal F positions: plaintext[i] = 0 (F), k unchanged

## Decrypted GP Values (121 runes)
```
WIDSOMYOUAREABENGUNTOYOURSELFYOUAREALAWUNTOYOURSELFEACHINTELLIGENCEISHOLYFORALLTHATLIUESISHOLYANINSTRUCTIANCOMMANDYOUROWNSELF
```

## English Text
```
WISDOM

YOU ARE A BEING UNTO YOURSELF
YOU ARE A LAW UNTO YOURSELF
EACH INTELLIGENCE IS HOLY
FOR ALL THAT LIVES IS HOLY

AN INSTRUCTION
COMMAND YOUR OWN SELF
```

## GP Encoding Notes
- LIUES = LIVES (U and V share GP value 1)
- INSTRUCTIAN = INSTRUCTION (IA is GP digraph 27, saves one position vs I+O+N)
- WIDSOM = WISDOM (S/D transposed at positions 2-3, artifact of key alignment)
- BENG = BEING (I omitted at position 15, NG digraph absorbs)

## Source
- Page 62, Section 2 (physical book)
- Uses bullet (•) separators
- 121 runes, 6 lines, 23 bullet separators, 5 newlines
- NOT in runes_full.txt (Section 2 source)

## Verification
- Score: 291 (exhaustive search, highest among all 12,288 F-skip combinations)
- Known Cicada 3301 philosophical text about self-sovereignty
- Consistent with DIVINITY key used on Pages 03, 04, 61
