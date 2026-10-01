import re
code = open('Tools/gpu_hillclimber_v2.py', encoding='utf-8').read()
for m in re.finditer(r"r'''(.+?)'''", code, re.DOTALL):
    s = m.group(1)
    found = False
    for i, ch in enumerate(s):
        if ord(ch) > 127:
            found = True
            print(f'  Non-ASCII at offset {i}: U+{ord(ch):04X} = {repr(ch)}')
    if not found:
        print(f'Kernel OK (length {len(s)})')
