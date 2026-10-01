"""lpcore — tested, deterministic core for Liber Primus analysis.

    corpus    canonical text loader (data/canonical/liber_primus_master.txt)
    gematria  the 29-rune alphabet, transliteration, prime values
    ciphers   deterministic cipher primitives (no search, no scoring)
    verify    check a decryption against known English
    stats     statistics of rune streams
    leak      the doublet leak: where the 86 surviving doublets fall (findings §7)
    detect    drift-tolerant likelihood ratio that a key stream decrypts a rune stream (findings §8)
    keys      candidate key streams and a reference anti-doublet encryptor for controls

Every solved section of the book is reproduced from canonical data by tests/test_lpcore.py.
"""
