# Attack catalog: cipher family → what distinguishes it → status on LP2

Snapshot 2026-10-01 (C1–C15). **Tracker §3.2 / §4 win over this file.** If you add a constraint, update the
matching rows here.

**Periodicity note.** C9 excludes periods ≤ 1000 when the re-key rule keeps the key in step, but only periods
≤ 25 when it drifts. The one drifting rule proposed so far (skip to the next key value) is itself excluded by C14.
So a *new* drifting mechanism would reopen periods 26–1000. Say so when you propose one.

Status: **✗** excluded (test or cited ledger) · **◐** partly · **○** open · **arg** excluded by an argument
written here, with no test yet. An "arg" row needs a test before it can go in the tracker.

## Classical and polyalphabetic families

| # | Family | Distinguishing statistic | Status | By |
|---|---|---|---|---|
| 1 | Monoalphabetic: Caesar, atbash, affine, keyed alphabet | unigram IoC stays at the plaintext's | ✗ | LP2 IoC and unigrams are flat (C2's χ² = 26.4 on 28 df) |
| 2 | Transposition only | English unigram survives | ✗ | same |
| 3 | Transposition, then an additive stream | none from transposition; the stream decides | reduces to the stream's row | `detect.log_lr` ignores plaintext order |
| 4 | Periodic Vigenère, Beaufort or variant | lag-L repeat rate | ✗ period ≤ 1000 in step; ≤ 25 drifting | C5, C9; ledger. See the periodicity note |
| 5 | Progressive (Trithemius) or any integer polynomial in i, mod 29 | periodic: f(i + 29) ≡ f(i) | ✗ in step | C9. See the periodicity note |
| 6 | Vigenère with an F-interrupter (LP1 style) | ᚠ excess about 190 | ✗ | C2; ledger |
| 7 | Running key from English text (letters, prime values, φ) | r = q ⊛ q is non-flat | ✗ | C10 |
| 8 | Plaintext autokey, any lag | same as 7 | ✗ | C10 |
| 9 | Ciphertext autokey c = p ± c_{i−L} | lag-L difference or sum histogram is English | ✗ L = 2–1000 | C11 |
| 10 | Alphabet chosen by c_{i−L} (keyed autokey, secret tables, affine chain) | lag-L transition rows are permuted English | ✗ L ≤ 1000 | C12 |
| 11 | Same as 10, plus a flat stream key | rows flat | ○ | not covered (findings §10) |
| 12 | Alphabet chosen by *plaintext* runes, or a 2-rune context | 841-row tables, too sparse for χ² | ○ | not covered |
| 13 | Key from a small alphabet: digits, hex, letters | r = q ⊛ k is uneven | ✗ | C13 |
| 14 | Key from a wide alphabet: bytes, 00–99, base 60, 000–999 | no marginal power | ◐ | every named source on disk ✗ (stage R §16, grid §12); others need a *named* source + `detect.log_lr(starts=)` |
| 15 | Integer sequences (46 OEIS-style, raw and chained) | — | ✗ | ledger |
| 16 | Primes, φ(p), p ± c, 3301 − p; solved text's sums and values | — | ✗ | stage I (§8) |
| 17 | Digraphic (Playfair-like; Hill n = 2) | bigram structure | ✗ | ledger ("digraphic"). Confirm Hill was in its scope before relying on this |
| 18 | Hill n ≥ 3 over Z₂₉ | block-aligned structure | ○ | untested. A plain Hill cipher has no reason to avoid doublets, so it would still need an output rule (arg) |
| 19 | Homophonic over the same 29 symbols | homophones must flatten English | ✗ | C15: 26 plaintext letters leave 3 spare runes; the flattest allocation still has χ² ≥ 4,802 (LP2 26.4). J and X alone decide it. With a flat stream on top, see row 3 |
| 20 | Section key reuse (two-time pad across sections) | cross-section difference statistics | ✗ | ledger. The pre-2026 "overlaps" were duplicated text (tracker §4.3) |
| 21 | Common PRNGs / KDFs; public random archives | — | ✗ | Dukotah ledger (~14.5 billion offsets) |
| 22 | *Named* custom generator (LFSR with stated taps and seed, hash chain of a stated phrase) | — | ○ | needs exact definition + mod-29 mapping + `detect.log_lr` |
| 23 | Two or more additive layers | only the sum is visible | constraints apply to the sum | test the composed stream, not one layer |
| 24 | Per-position alphabet c = σ_{k_i}(p), non-additive | label-free emissions (`alphabets.log_mean_lr`); uneven marginal | ◐ | ✗ any key of period ≤ 1000 in step (C9, §17). Long named keys: stage S **void** (§17), so open. Random σ over few classes leaves χ² ≫ 26.4: a flatness constraint is the next declared test. A re-run needs flat synthetic negatives |
| 25a | Chain-multiplicative c = c₋₁ + (p − x)·k (doublets mark plaintext x) | doublet count and word positions are x's | ✗ | C3, all 29 letters (findings §15) |
| 25 | Bitwise ops on 5-bit rune codes (XOR) | produces values 29–31 | arg | needs a stated reduction to 29 values, or it emits impossible runes |
| 26 | One-time pad, truly random | indistinguishable | consistent with all data | breakable only by finding the pad |

## The anti-doublet rule (any full model must include one)

| Mechanism | Prediction | Status | By |
|---|---|---|---|
| Nudge: re-encrypt as c ± 1 | missing doublets pile into Δc = ±1 | ✗ | L1 |
| Check only within a written line | survivors concentrate at line breaks | ✗ | L2 |
| Periodic lapse in checking | survivors on a period | ✗ | L3 |
| Key-switch (`reference/community/images/Algorithm.png`) | 0.21–0.35 % survival | ✗ | L5 |
| Skip to the next key value | key repeats ≈ 19 %, so Δc carries English bigram shape | ✗ | C14 |
| Re-draw independent of the key stream | flat Δc, constant 19 % survival | ○ consistent | C8 requires replacement = original ≈ 19 % of the time |
| Hand check missing ≈ 1 in 5 | random survivors at a constant rate | ○ consistent | can't be told apart from the previous row (§7) |

## Unworked data that could carry a key

| Object | Where | Status |
|---|---|---|
| Base-60 grid, 256 bytes (scans 66–68) | `keys.grid_bytes` | not a key (§12); not decrypted by LP-native keys (§13); **what it encodes ○** |
| OutGuess payloads | `data/outguess/` | ✗ as keys with drift, any phase (§16). Scans not on disk ○ |
| Cicada numbers in two-digit groups | `lp-expert/lore.md` | ✗ P.S. and 2014 n, pairs and triples, any phase (§16) |
| AN END hash | `keys.an_end_hash` | ✗ as a byte key for the grid (§13); ✗ as a cyclic LP2 key with drift, any phase (§16) |
