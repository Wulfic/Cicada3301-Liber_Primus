#!/usr/bin/env python3
"""
Lightweight orchestrator to run multiple CPU-based theory tests across pages.

By default this runs:
 - combined_cipher_test (quick combined keyword+totient checks)
 - autokey_comprehensive Phase 1 (P63 keywords only)
 - mono_sub_solver quick runs across a small page set

This script avoids the very heavy exhaustive phases (length-2/3 autokey
brute-force and wide keyword-stepped offsets) unless explicitly requested.

Outputs are written to `data/theory_runs/<timestamp>/`.
"""

import sys
import os
import argparse
import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / 'data'
OUT_ROOT = DATA / 'theory_runs'
OUT_ROOT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE / 'tools'))


def capture_module_main(mod):
    """Call mod.main() and capture printed output as a string."""
    import io
    old = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        mod.main()
    finally:
        sys.stdout = old
    return buf.getvalue()


def run_combined(out_path):
    import combined_cipher_test as comb
    out = []
    out.append(f"Running combined_cipher_test at {datetime.datetime.now()}\n")
    try:
        txt = capture_module_main(comb)
        out.append(txt)
    except Exception as e:
        out.append(f"ERROR running combined_cipher_test: {e}\n")
    out_path.write_text('\n'.join(out), encoding='utf-8')


def run_autokey_keywords(out_path, pages):
    import autokey_comprehensive as ak
    lines = []
    lines.append(f"Autokey (P63 keywords) quick pass — {datetime.datetime.now()}\n")

    for pg in pages:
        try:
            data = ak.load_page(pg)
            if data[0] is None:
                lines.append(f"P{pg:02d}: missing page file or empty")
                continue
            cipher, singletons, _ = data
            hits = []
            for kw_name, kw_seed in ak.ALL_KEYWORDS.items():
                for mode_name, mode_func in ak.MODES:
                    result = ak.test_seed(cipher, singletons, kw_seed, mode_func)
                    if result is not None:
                        ioc, sp, st, plain = result
                        if ioc > 1.3:
                            txt = ak.to_runeglish(plain)[:200]
                            hits.append((ioc, mode_name, kw_name, sp, st, txt))

            if hits:
                hits.sort(key=lambda x: -x[0])
                lines.append(f"P{pg:02d}: {len(hits)} hits (IoC>1.3)")
                for ioc, mode, kw, sp, st, txt in hits[:5]:
                    lines.append(f"  IoC={ioc:.4f} {mode:10s} {kw:15s} sing={sp}/{st} | {txt}")
            else:
                lines.append(f"P{pg:02d}: NO hits (IoC>1.3)")
        except Exception as e:
            lines.append(f"P{pg:02d}: ERROR {e}")

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def run_mono_sub_quick(out_path, pages, variants=None, iters=20000, restarts=3):
    import mono_sub_solver as ms
    import solve_p21_30 as sol
    sol.load_wordlist()
    corpus = ms.load_corpus_text()
    qg, floor = ms.build_quadgram(corpus)

    lines = []
    lines.append(f"Mono-sub quick runs — {datetime.datetime.now()}\n")

    for pg in pages:
        try:
            res = sol.analyze_page(pg, verbose=False)
            if not res or not res.get('char_results'):
                lines.append(f"P{pg:02d}: no char-level variants available")
                continue

            for name, text, ioc, indices in res['char_results']:
                if variants and name not in variants:
                    continue
                cipher_text = text.upper()
                best_score = -1e9
                best_plain = None
                for r in range(restarts):
                    try:
                        plain, mapping, score = ms.run_hillclimb(cipher_text, qg, floor, corpus, iters=iters, fixed=None)
                        if score > best_score:
                            best_score = score
                            best_plain = plain
                    except Exception as e:
                        lines.append(f"  P{pg:02d} {name}: hillclimb error: {e}")
                lines.append(f"P{pg:02d} [{name}] best_score={best_score}")
                lines.append(best_plain if best_plain else "")
                lines.append("")
        except Exception as e:
            lines.append(f"P{pg:02d}: ERROR {e}")

    out_path.write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', '-p', nargs='*', type=int, help='Pages to test (default 21-30)')
    parser.add_argument('--run-combined', action='store_true', help='Run combined_cipher_test')
    parser.add_argument('--run-autokey', action='store_true', help='Run autokey P63-keyword pass')
    parser.add_argument('--run-mono', action='store_true', help='Run mono-sub quick sweeps')
    parser.add_argument('--all', action='store_true', help='Run combined+autokey+mono')
    parser.add_argument('--iters', type=int, default=20000, help='Mono-sub iterations (per restart)')
    parser.add_argument('--restarts', type=int, default=3, help='Mono-sub restarts')
    args = parser.parse_args()

    pages = args.pages if args.pages else list(range(21, 31))
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = OUT_ROOT / ts
    run_dir.mkdir(parents=True)

    print(f"Theory run directory: {run_dir}")

    if args.all or args.run_combined:
        outp = run_dir / 'combined_cipher_test.txt'
        print('Running combined_cipher_test ->', outp)
        run_combined(outp)

    if args.all or args.run_autokey:
        outp = run_dir / 'autokey_keywords.txt'
        print('Running autokey P63-keyword pass ->', outp)
        run_autokey_keywords(outp, pages)

    if args.all or args.run_mono:
        outp = run_dir / 'mono_sub_quick.txt'
        print('Running mono-sub quick sweeps ->', outp)
        run_mono_sub_quick(outp, pages, iters=args.iters, restarts=args.restarts)

    print('Done. Outputs saved to', run_dir)


if __name__ == '__main__':
    main()
