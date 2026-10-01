#!/usr/bin/env python3
"""Simple monitor: tail the GPU hillclimber output file and print key events.

Usage:
  python tools/monitor_gpu_output.py --file data/gpu_hill_gpu0.txt --lines 200 --filter

This prints the last N lines (filtered if requested) and then tails the file,
printing new lines that look important (Step, PROMISING!, HIGH SCORE, Best text).
"""
import time
import os
import sys
import argparse

KEYWORDS = ('Step', 'PROMISING!', 'HIGH SCORE', 'Best text', 'HIGH SCORE FULL TEXT')

def print_tail(path, n=200, filtered=True):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f'File not found: {path}', flush=True)
        return
    tail = lines[-n:] if n > 0 else lines
    for ln in tail:
        if not filtered or any(k in ln for k in KEYWORDS):
            print(ln.rstrip(), flush=True)

def follow(path, interval=2.0, filtered=True):
    # wait for file
    while not os.path.exists(path):
        print(f'Waiting for {path}...', flush=True)
        time.sleep(1.0)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        f.seek(0, os.SEEK_END)
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(interval)
                    continue
                if not filtered or any(k in line for k in KEYWORDS):
                    print(line.rstrip(), flush=True)
        except KeyboardInterrupt:
            print('\nMonitor stopped by user', flush=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', '-f', default='data/gpu_hill_gpu0.txt')
    p.add_argument('--lines', '-n', type=int, default=200)
    p.add_argument('--interval', '-i', type=float, default=2.0)
    p.add_argument('--filter', action='store_true', help='Only print key lines')
    args = p.parse_args()

    # print recent tail
    print_tail(args.file, n=args.lines, filtered=args.filter)
    print('--- now following for new lines ---', flush=True)
    follow(args.file, interval=args.interval, filtered=args.filter)

if __name__ == '__main__':
    main()
