---
name: lp-expert
description: "Cicada 3301 and Liber Primus domain expert, grounded in this repo's evidence. Use when: answering any question about Cicada 3301, the Liber Primus (LP1/LP2), runes, the Gematria Primus, solved or unsolved pages, scan vs page numbering, Cicada lore, number motifs (3301, primes, totient, Fibonacci, base 60), OutGuess, the PGP key, community theories, or when deciding which lead to work on next. Load it before lp-attack or lp-claim-audit."
argument-hint: "The question or lead (e.g. 'what does the doublet deficit rule out', 'is the P.S. number tested')"
---

# Liber Primus Expert: Answer From Evidence, Not Folklore

The Liber Primus attracts more confident nonsense than any other puzzle. The repo's edge is that every claim it
makes is reproducible. Your edge as an expert is the same: **know which tier each fact comes from and say so.**
The book's own first page is the house rule: *"BELIEVE NOTHING FROM THIS BOOK EXCEPT WHAT YOU KNOW TO BE TRUE.
TEST THE KNOWLEDGE."* (canonical translation, 0.0.0.1–0.0.0.3).

## Step 0: Load current state before answering anything substantive

The snapshot below goes stale. These files do not:

1. `MASTER_TRACKER.md` §1 (where things stand, next actions), §3.2 (the constraints C1…Cn), §4 (ruled out).
   **If the tracker lists a constraint number higher than C19, this skill is out of date: trust the tracker.**
2. `reference/findings/lp2_logic_findings_2026-09-29.md`. **Its §0 register is the fastest lookup:** one row per
   C- and L-number with the observed value, the declared line, and the test that pins it. The numbered sections
   below it hold the evidence. `tests/test_docs.py` keeps the register complete, so a row you cite exists.
3. `data/canonical/liber_primus_translation.txt`: the whole solved plaintext (239 lines). Read it rather than
   quoting LP lines from memory. Misquotes circulate widely, and one has already reached a findings doc.

## Evidence tiers: label every claim

| Tier | Source | How to cite |
|---|---|---|
| ★ Proven | `data/canonical/` through `tools/lpcore`, asserted by `tests/` | "test `test_x` shows…" |
| Tested here | findings doc C1–Cn, L1–L5, stage runners `tools/run_stage_*.py` | "C12 (findings §10)" |
| Ledger | Leo-Y-Zhang and Dukotah 2026 exclusion ledgers (findings §1) | "excluded by the Leo-Y-Zhang ledger, not re-run here" |
| Unverified | `reference/community/*` (incl. `community_research.md` §1–§9), wiki, IRC logs, Discord | "community-reported, unverified" |
| Artifact | anything before 2026-09-29, `tools/legacy/`, `data/archive/`, tracker §4.3 | don't cite as evidence; say why it is invalid |
| Memory | your training data about Cicada | lowest tier; verify in-repo or flag it |

**Never upgrade a tier silently.** "Cicada used X in 2013" from memory is not a constraint on LP2.

## The alphabet (Gematria Primus): `tools/lpcore/gematria.py`

29 runes, index 0–28 in futhorc order. All cipher arithmetic is mod 29. Each rune's value is the n-th prime.

```
 0 ᚠ F    2 |  1 ᚢ U    3 |  2 ᚦ TH   5 |  3 ᚩ O    7 |  4 ᚱ R   11 |  5 ᚳ C/K 13
 6 ᚷ G   17 |  7 ᚹ W   19 |  8 ᚻ H   23 |  9 ᚾ N   29 | 10 ᛁ I   31 | 11 ᛄ J   37
12 ᛇ EO  41 | 13 ᛈ P   43 | 14 ᛉ X   47 | 15 ᛋ S/Z 53 | 16 ᛏ T   59 | 17 ᛒ B   61
18 ᛖ E   67 | 19 ᛗ M   71 | 20 ᛚ L   73 | 21 ᛝ NG  79 | 22 ᛟ OE  83 | 23 ᛞ D   89
24 ᚪ A   97 | 25 ᚫ AE 101 | 26 ᚣ Y  103 | 27 ᛡ IA 107 | 28 ᛠ EA 109
```

Spelling traps (`ALTERNATE_SPELLINGS`): U/V share a rune, C/K/Q share one (QUESTION is written CWESTION; the
translation even keeps "KWESTION"), NG can stand for ING, IA for IO, and S covers Z. Never hand-transliterate. Use
`gematria.spellings_of(word)` and `gematria.word_matches(indices, word)`. `indices_to_latin` prints one spelling per
rune (ᚳ → C, so KNOW reads CNOW). To display solved text use `verify.render_words`, which takes the spelling from
the English.

**The plaintext uses 26 of the 29 runes.** In the 2,901 solved plaintext runes, AE, EO and OE never occur, and
J (3), X (5) and IA (16) are rare (test `test_letter_counts`). A claimed LP2 decryption that is rich in AE/EO/OE
is not LP-English. The same gap is why no homophonic substitution can flatten LP-English (C15).

**Windows console:** printing runes crashes under cp1252. Set `PYTHONIOENCODING=utf-8` (or run `python -X utf8`).

## Numbering: three systems that are easy to confuse

- **Scan** 00–74 (`pages/page_XX/`, `images/XX.jpg`): the folder key.
- **LP page** (LP1 / LP2 p0–57): `corpus.lp_location(scan)`. LP2 p0 = scan 17; AN END = scan 73 = LP2 p56.
- **Segment** 0–17 (`$` breaks in the master): the cipher unit. Unsolved = 7–15 (`stats.UNSOLVED_SEGMENTS`).
  Segment 10 is only 9 runes plus the 4×4 square. The base-60 grid (256 cells) sits on scans 66–68 *inside* segment 15.

Before 2026-09-29, `pages/page_N/runes.txt` held the wrong text. Any older claim that names a page number is
suspect until it has been re-derived from canonical data (tracker §4.3).

## What the solved sections teach about the author

From `tools/lpcore/solved.py` (tracker §3.1). These are style priors, **not** constraints on LP2:

- **Every solved cipher is additive mod 29** (atbash, atbash + 3, Vigenère, φ(prime) stream), or plaintext.
- **Keys come from the book's own vocabulary and its "sacred" maths.** DIVINITY; CIRCUMFERENCE written with
  F for C (FIRFUMFERENFE); φ of the primes. Compare 0.1.2.1–0.1.2.3: "THE PRIMES ARE SACRED / THE TOTIENT
  FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED."
- **Interrupters:** in LP1, plaintext F is left unenciphered and consumes no key. **LP2 does not do this (C2).**
- **The book contains human errors** (WIDSOM survives decryption). Expect slips in LP2 too. Any decoder that
  needs perfect sync is broken by design (AGENTS.md: "key tests must handle skips").
- Keys run continuously across word, quote and paragraph breaks (FIRFUMFERENFE never resets).

## The unsolved cipher in one paragraph (snapshot: C1–C19, 2026-10-01)

LP2 segments 7–15 total 12,956 runes. They are flat at every order except one: **86 adjacent doublets where 447
are expected** (z = −17.4). One system runs throughout (C6), acting on the continuous stream regardless of words,
lines or pages (C1, L2). The survivors mark no plaintext letter (C3). It is not homophonic substitution (C15). An
additive stream alone cannot make the deficit (C4), so a rule acts at the output and re-keys about 81 % of
would-be doublets. The replacement is not "skip to the next key value" (C14). The key is
near-flat mod 29 and aperiodic (C9). It is not English text in any mapping (C10), and not single digits, hex or
letters (C13). Its values cannot be chosen by earlier ciphertext alone (C11, C12). It is not primes, φ(primes),
the solved text's word sums or its rune values (stage I). It is not the base-60 grid (§12). It is not any Cicada
number or OutGuess payload in the repo, read as pairs, triples or bytes from any phase (§16). **The open space:**
a wide-alphabet key from an *unnamed* source scored with `detect.log_lr`, or a per-position alphabet that is
either a Latin-square tabula (Quagmire-type) or keyed by more than ~150 effective classes. A random tabula over
fewer classes is excluded by flatness alone, under any alignment (C16). A Quagmire tabula is the additive cipher
renamed, so its alphabets are invisible to key-free tests. Even so, no iid key with V_eff ≥ 17 makes the deficit
under any alphabets (C17), and under random alphabets the key is still not English, digits or hex (C18). Uniform
A–Z letters are excluded only for straight alphabets (§19). With named alphabets from 34 LP keywords, scored with
labels, English and digit keys are excluded under all 314,432 triples, hex under all but 431, and uniform A–Z under a
third of them (C19, §20).

## Cicada motifs and leads

`lore.md` (next to this file) lists every motif and community lead with its current test status. **Read it
before proposing a "Cicada would have used X" key.** Most obvious X have already been run.

## How to answer

1. Answer the question first, then give its tier and source (C-number, test name, file, or "unverified").
2. When the honest answer is "unknown" or "untestable this way", say so. C13 lists alphabets that are
   *untestable* by marginals. That is not the same as excluded.
3. If a question implies an attack, check it against tracker §4 and `lore.md`. If it is open, hand off to
   `lp-attack`. If someone claims a solve, hand off to `lp-claim-audit`.
4. Treat number coincidences (729 = 9³, 1729 = 9³ + 10³, 3316 = 4 × 829) as curiosities. A coincidence becomes
   evidence only when it makes a falsifiable prediction that a declared test then confirms.
5. Anything claiming to come from Cicada after 2014 is false unless it is PGP-signed by **7A35090F**
   (full fingerprint `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`, key in
   `reference/sources/cicada_pgp_key.asc`). Verify with `gpg --verify` before using it as a hint.
