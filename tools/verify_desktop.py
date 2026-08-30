#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
html = (root / 'src' / 'index.html').read_text(encoding='utf-8')
manifest = json.loads((root / 'tools' / 'tts_manifest.json').read_text(encoding='utf-8'))
audio = root / 'src' / 'audio'


package = json.loads((root / 'package.json').read_text(encoding='utf-8'))
main_js = (root / 'main.js').read_text(encoding='utf-8')
preload_js = (root / 'preload.js').read_text(encoding='utf-8')
if package.get('version') != '11.4.1':
    raise SystemExit('Desktop package version mismatch')
if package.get('build',{}).get('nsis',{}).get('createDesktopShortcut') is not True:
    raise SystemExit('NSIS desktop shortcut is not enabled')
if 'frame: false' not in main_js or 'ensureDesktopShortcut()' not in main_js:
    raise SystemExit('Custom frame or packaged desktop shortcut hook is missing')
if 'data-window-action="minimize"' not in html or 'data-window-action="maximize"' not in html or 'data-window-action="close"' not in html:
    raise SystemExit('Custom window controls are incomplete')

checks = {
    'desktop version marker': 'name="matlex-version" content="11.4.1-desktop"' in html,
    'desktop layout layer': 'id="matlex-desktop-layout"' in html,
    'desktop v11.4 layer': 'id="matlex-desktop-v114-layout"' in html,
    'desktop v11.4.1 polish': 'id="matlex-desktop-v1141-polish"' in html,
    'custom desktop titlebar': 'id="matlexDesktopTitlebar"' in html,
    'desktop module aside': 'desktop-module-aside' in html,
    'desktop study return': 'desktop-study-return' in html,
    'desktop local audio path': "location.protocol==='file:'?'./audio/'" in html,
    'shared navigation preserved': 'id=\'mlSharedNav\'' in html or 'id="mlSharedNav"' in html,
    'three study modules preserved': all(x in html for x in ['data-module="english"','data-module="interview"','data-module="concept"']),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('Desktop architecture check failed: ' + ', '.join(failed))

# Reject the old formulaic concept filler and verify several concrete examples.
start = html.index('const V10_CONCEPT_BASE=') + len('const V10_CONCEPT_BASE=')
end = html.index('];', start) + 1
concepts = json.loads(html[start:end])
boilerplate = [
    '是分析晶体缺陷与界面时的重要概念。',
    '是固态相变与热处理中的重要概念。',
    '是半导体、薄膜和功能材料研究中的重要概念。',
    '常用于热力学、相图和凝固分析。',
    '常用于粉末冶金与硬质合金制备。',
    '常用于原子尺度模拟和分子动力学分析。',
    '常用于断裂、腐蚀和失效分析。',
]
for phrase in boilerplate:
    if any(phrase in c.get('explanation','') for c in concepts):
        raise SystemExit('Formulaic concept filler remains: ' + phrase)
by_id = {str(c['id']): c for c in concepts}
required_examples = {
    'c-46': 'FCC晶体中的{111}晶面族',
    'c-59': '四个基体原子围成的四面体间隙',
    'c-271': '几十纳米',
    'c-490': '旋涂成膜后再退火结晶',
    'c-509': '带隙中引入缺陷能级',
}
for cid, fragment in required_examples.items():
    if fragment not in by_id.get(cid,{}).get('explanation',''):
        raise SystemExit(f'Concrete concept example missing: {cid} -> {fragment}')
print(f'Concept quality verified: {len(concepts)} concepts, no formulaic filler.')

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
