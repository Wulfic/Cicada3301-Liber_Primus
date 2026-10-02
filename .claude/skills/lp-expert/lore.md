# Cicada motifs and key-source leads, with status

Snapshot as of 2026-10-01 (C1–C19, stage V). **Status comes from tracker §4 and the findings doc. If they disagree with
this file, they win, so update this file.** "Open" means no test in this repo has scored it, not that it is
promising.

Status legend: **✗ excluded** (by a test or a cited ledger) · **◐ partly** (some readings excluded) ·
**○ open** · **? unverified** (the lead itself has not been confirmed to exist).

## Motifs in the book itself (verified in canonical data)

| Motif | Where | Status as an LP2 key |
|---|---|---|
| Primes p(n), φ(p(n)), p ± c, 3301 − p | AN END's key; "THE PRIMES ARE SACRED" 0.1.2.1 | ✗ every mode and constant shift, drift-tolerant (stage I K-A, findings §8) |
| Solved text as a running key (rune values, word sums) | all LP1 | ✗ K-C, K-D (§8); any English running key is ✗ by C10 |
| DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, other single key words | segs 1, 5 | ✗ every period ≤ 1000 (C9, C5); ledger: ~200 key texts; as Quagmire keyword alphabets, ✗ with English, digit or hex keys and ◐ with uniform A–Z (C19, §20) |
| 3301 / 1033 (reversal; LP1 magic sums) | scans 05, 16 | ✗ as a period or short key (C9); not tested as a seed of a generator |
| Fibonacci and spiral reading | scan 32 square = \|3301 − p(F+1)\| | ✗ the square as a key (period 16, C9); Pisano period mod 29 = 14 ✗ |
| 4×4 square numbers on the segment 10 title | scan 32 | ✗ 0 of 30 decodes give English (§8) |
| Base-60 grid, 256 bytes | scans 66–68, inside seg 15 | ✗ as a key (§12); ✗ as LP ciphertext or XOR/Vigenère under LP-native keys (§13); uniform bytes; ✗ English/rune/hex text under any repeating byte key, period ≤ 102; ✗ RSA modulus, prime, compressed stream (§22); **○ what it encodes (OTP-class)** |
| AN END deep-web hash (512-bit) | scan 73; `keys.an_end_hash` | ✗ as a byte key for the grid (§13); ✗ as a cyclic LP2 key from any phase (§16); the page itself was never found (community) |
| Instar / emergence / circumference / "within" | 0.1.0.7, PARABLE | thematic only: no falsifiable key proposed |
| "EITHER THE WORDS OR THEIR NUMBERS" | 0.0.0.8 | word sums ✗ (K-C); other word→number maps ○ |
| Section sizes 729, 1729, 1021, 3316 | tracker §5 | curiosities; no prediction stated |

## Leads from Cicada's other material (from `reference/community/community_research.md` §2, *unverified there*)

Confirm each lead against a primary source in `reference/sources/` or `data/outguess/` (or a PGP-verified
message) before investing in it.

| Lead | Claimed content | Status |
|---|---|---|
| 2012 P.S. number | a 131-digit decimal integer (both repo copies agree; `echo446ghq_analysis.md`'s "128-digit" is wrong). Provenance conflicts between docs (2012 end message vs posted with the LP); confirm against a primary source | ✗ one digit per rune (C13); ✗ pairs and triples, both 131- and 132-digit forms, any phase (stage R, findings §16). Base conversions and factors ○ |
| 2013–2014 numbers | 2014 RSA n (130 digits), second-onion hex (256 bytes), in `people_2014.md` | ✗ pairs, triples, bytes, any phase (§16). Others not on disk ○ |
| OutGuess payloads | `data/outguess/` (`page_*.txt`, `*.bin`, wisdom/folly hints) | ✗ every payload on disk, as bytes (mod or rejection), any phase, with drift (§16). The three `.bin` are 58,152 random-looking bytes. Scans not on disk ○ |
| Telnet "primes" output with a gap (73 … 1223 missing) | ? | ○ the gap as an index set or permutation; prime *values* are ✗ |
| Onion cookies 167 / 761 (reversal pair) with 256-bit hex values | ? | ✗ hex digits (C13); ✗ as bytes, any phase (§16) |
| Trailing-whitespace prime sequences in signed messages | ? | ○ but short, so C9 kills any periodic use |
| Wisdom / folly files (identical, from `/tmp` on the Cicada ISO) | binary in `data/outguess/` | ✗ as a key, both directions (§16); `folly_rev_hint` is the exact reverse; content undeciphered ○ |
| LFSR or PRNG keystream seeded from Cicada numbers | community §7a | ◐ ledger: common KDFs/PRNGs ✗. A *named* LFSR (taps + seed) ○, and it needs a declared mapping to mod 29 |
| Public random archives (Bitcoin, NIST Beacon, RANDOM.ORG, RAND) | Dukotah ledger | ✗ ~14.5 billion offsets |

## What any key source must satisfy (filter before testing)

A candidate is worth a declared test only if it can meet all of these. Each constraint is tracker §3.2:

- At least ~12,956 values, or a stated reuse rule. A reused segment shows up as a lag repeat (C9: lags ≤ 1000 are normal).
- Values near-flat mod 29 under the stated mapping. A 10-, 16- or 26-symbol alphabet is ✗ (C13). English-like
  sources are ✗ (C10).
- Not computable from earlier ciphertext (C11, C12).
- Paired with an anti-doublet rule whose replacement value is independent of the next key value (C14), or with
  ~19 % hand-check misses. Whatever the mechanism, it must reproduce L1–L4 without fitting.

## Lore discipline

- Dates, people and onion addresses from memory are tier "Memory". Use them for orientation, never as evidence.
- The 2017 "Beware false paths. Always verify PGP signature from 7A35090F" warning is the reason to treat
  unsigned "new hints" as noise.
- The Echo446Ghq "full solution" is debunked (`reference/community/echo446ghq_analysis.md`). It is the model
  for how a fitted "solve" looks; see `lp-claim-audit`.
