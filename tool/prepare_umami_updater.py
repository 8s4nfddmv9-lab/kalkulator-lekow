from pathlib import Path

path = Path('tool/apply_umami_analytics.py')
source = path.read_text(encoding='utf-8')
old = '    if count != 1:\n'
new = '    if count < 1:\n'
if old not in source:
    raise SystemExit('Could not relax the one-off replacement helper safely.')
path.write_text(source.replace(old, new, 1), encoding='utf-8')
