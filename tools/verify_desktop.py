#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'src' / 'index.html').read_text(encoding='utf-8')
manifest = json.loads((root / 'tools' / 'tts_manifest.json').read_text(encoding='utf-8'))
audio = root / 'src' / 'audio'

checks = {
    'desktop version marker': 'name="matlex-version" content="11.3.1-desktop"' in html,
    'desktop layout layer': 'id="matlex-desktop-layout"' in html,
    'desktop local audio path': "location.protocol==='file:'?'./audio/'" in html,
    'shared navigation preserved': 'id=\'mlSharedNav\'' in html or 'id="mlSharedNav"' in html,
    'three study modules preserved': all(x in html for x in ['data-module="english"','data-module="interview"','data-module="concept"']),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Desktop architecture check failed: ' + ', '.join(failed))

if audio.exists():
    wc = len(list(audio.glob('w_*.mp3')))
    ec = len(list(audio.glob('e_*.mp3')))
    if wc != len(manifest) or ec != len(manifest):
        raise SystemExit(f'Audio coverage mismatch: word={wc}/{len(manifest)}, example={ec}/{len(manifest)}')
    test = audio / 'test_ava.mp3'
    if not test.exists() or test.stat().st_size <= 700:
        raise SystemExit('Ava test audio missing or invalid')
    print(f'Desktop assets verified with Ava audio: {len(manifest)} vocabulary items')
else:
    print(f'Desktop source verified. Audio will be generated during build for {len(manifest)} vocabulary items.')
