---
name: lp-claim-audit
description: "Skeptical audit of a claimed Liber Primus decryption, key, or 'pattern' — ours, the community's, or an LLM's. Use when: someone (including you) reports English coming out of unsolved runes, a GitHub/Reddit/Discord 'full solution', a gematria-sum coincidence, a crib that 'fits', a hidden message in Cicada numbers, or any result that looks too good. Produces a verdict with reasons and a write-up in reference/community/."
argument-hint: "The claim and its source (URL, file, commit, or pasted method)"
---

# LP Claim Audit: Too Good Is Guilty Until Reproduced

Thousands of people have looked at this book since 2014, and nobody has a verified LP2 decryption. The prior on
any new "solve" being real is tiny. The usual explanation is that the solver's choices manufactured the English.
Your job is to measure those choices, not to admire the output. Load `lp-expert` first.

Applies to our own results too, and most of all to them. Tracker §4.3 is a list of our own past "solves".

## Procedure

### 1. Pin the claim exactly

Write down: the runes (segment, start and end offsets), the method as an equation, the key as concrete values,
every free choice made (mode per word, skip positions, spelling variants, which excerpt), and the claimed plaintext.
Get their code if it exists. **If it can't be stated precisely enough to rerun, the verdict is "unreproducible".**
Stop there.

### 2. Reproduce on canonical runes

Load the runes with `load_corpus().segment_runes(s)`, never their copy. Diff their input runes against canonical.
Transcription drift, old misaligned page files (tracker §4.3) and LP1 text placed in LP2 slots explain many
"solves" all by themselves. Run their method exactly as stated. Do not fix their bugs to make it work.

### 3. Count the degrees of freedom

Rough unicity rule. A rune carries log₂ 29 ≈ 4.86 bits. English carries roughly 1–1.5 bits per letter, so each
rune of real plaintext gives about **3.3–3.9 bits of evidence**. A method with K bits of free choice can make
roughly K / 3.5 runes "decrypt" by itself, whatever the truth. (This is an approximation: state it as one,
and simulate when the case is close.) Count:

- every key value chosen to fit (≈ 4.86 bits each, so **a free key per position gives zero evidence**);
- each per-word mode, shift or spelling choice (log₂ of the number of options);
- each skip or interrupter placed where convenient;
- the choice among N tried methods, offsets or excerpts (log₂ N), **including the ones they didn't report**.

If the explained runes don't greatly exceed K / 3.5, the claim is fitting. Say so with the numbers.

### 4. Run the fixed method on the whole section

A real key decrypts everything, not just the excerpt. Freeze the method and key as stated, then score the
**entire** section with `detect.log_lr` (or `stats.unigram_llr` on the decoded stream). A true key scores hundreds
of nats on any LP2 section with ≥ 729 runes. The pass mark is 30. A claim confined to 20 runes that collapses on
the other 1,500 is falsified.

### 5. Test on held-out runes

Did the method get developed on these runes? Then declare, before running, a held-out region it must also decrypt
(the next paragraph, another section if the claim says the system is shared, given C6). Use the same threshold as
step 4.

### 6. Check it against the known fingerprint

A real LP2 method must reproduce, from its own definition and without fitting:
86 doublets in 12,947 pairs (0.66 %, C1–C6), flat ᚠ (C2), L1–L4 (how the survivors are spread), and the
≈ 19 % survival (C8). Its key must satisfy C9–C16 (the findings §0 register lists each with its test). A method that predicts 3.4 % doublets is wrong, however
good the excerpt reads. Check the catalog in `lp-attack/attack-catalog.md`. If the family is already excluded,
cite the C-number.

### 7. Check whether the plaintext is plausibly LP-English

Use `verify.compare_words` and `gematria.word_matches` against the claimed English. Watch for flexible spelling
(NG/ING, C/K/Q, IA/IO, U/V) used differently word by word. The solved plaintext never uses AE, EO or OE. "Sounds
like Cicada" is not evidence. Their vocabulary is public, and an LLM will happily produce it.

### 8. Check provenance

A claimed new Cicada hint must be PGP-signed by 7A35090F (`reference/sources/cicada_pgp_key.asc`, `gpg --verify`).
For a numerical coincidence (gematria sums hitting 3301, primes, palindromes), estimate the chance rate with a
seeded simulation over the same freedom before treating it as signal.

## Verdicts

| Verdict | Meaning | Next |
|---|---|---|
| **Unreproducible** | method or key can't be pinned down | record and stop |
| **Excluded** | the family is already ruled out (C-number or ledger) | cite it, record, stop |
| **Fitting** | reproduces on the excerpt, fails step 3, 4 or 5 | record the DOF count and the full-section score |
| **Survives** | passes steps 2–7 with a declared threshold | extraordinary. Hand to `lp-attack` step 6 as a formal stage: declare, controls, test, findings section. Tell the owner |

## Record

Write `reference/community/<source>_analysis.md`, modelled on `echo446ghq_analysis.md`: source and date, the claim,
the method as an equation, steps 2–7 with numbers, verdict. Then add one line to tracker §4.1 (theirs) or §4.2
(ours). Any number in the write-up must come from a command you show or a test.

## Red flags that justify going straight to step 4

Per-position or per-word free choices · an excerpt under 100 runes · "probability < 0.001" computed after choosing
the transformation · outputs that need interpretation (coordinates, timestamps, "commands") · reliance on
`pages/*/runes.txt` or pre-2026-09-29 numbering · an optimiser anywhere in the pipeline · no code.
