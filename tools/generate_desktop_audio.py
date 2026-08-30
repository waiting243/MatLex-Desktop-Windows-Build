#!/usr/bin/env python3
import asyncio, json, os, shutil, re
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools" / "tts_manifest.json"
AUDIO_DIR = ROOT / "src" / "audio"
VOICE = os.environ.get("ML_TTS_VOICE", "en-US-AvaNeural")
# Matches the old browser helper when its UI speed is 1.00x:
# sentence/example = 1.00x; clicked individual word ≈ 0.88x.
WORD_RATE = os.environ.get("ML_TTS_WORD_RATE", "-12%")
EXAMPLE_RATE = os.environ.get("ML_TTS_EXAMPLE_RATE", "+0%")
CONCURRENCY = int(os.environ.get("ML_TTS_CONCURRENCY", "7"))
MAX_RETRIES = int(os.environ.get("ML_TTS_RETRIES", "6"))

async def synth_one(sem, text, out, rate, label):
    if out.exists() and out.stat().st_size > 700:
        return
    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
                c = edge_tts.Communicate(text=text, voice=VOICE, rate=rate, volume="+0%", pitch="+0Hz")
                await c.save(str(out))
                if out.exists() and out.stat().st_size > 700:
                    return
                raise RuntimeError("empty audio")
            except Exception as exc:
                try: out.unlink(missing_ok=True)
                except Exception: pass
                if attempt >= MAX_RETRIES:
                    raise RuntimeError(f"{label} failed: {exc}") from exc
                await asyncio.sleep(min(15, 1.6 * (2 ** (attempt - 1))))

async def main():
    data=json.loads(MANIFEST.read_text(encoding='utf-8'))
    AUDIO_DIR.mkdir(parents=True,exist_ok=True)
    sem=asyncio.Semaphore(CONCURRENCY)
    jobs=[]
    tokens=set()
    for item in data:
        ident=int(item['id']); word=str(item['word']).strip(); example=str(item.get('example') or word).strip()
        for text in (word, example):
            tokens.update(m.group(0).lower() for m in re.finditer(r"[A-Za-z]+(?:['-][A-Za-z]+)*", text))
        jobs.append(asyncio.create_task(synth_one(sem,word,AUDIO_DIR/f'w_{ident}.mp3',WORD_RATE,f'word {ident}')))
        jobs.append(asyncio.create_task(synth_one(sem,example,AUDIO_DIR/f'e_{ident}.mp3',EXAMPLE_RATE,f'example {ident}')))
    jobs.append(asyncio.create_task(synth_one(sem,'Materials science',AUDIO_DIR/'test_ava.mp3',EXAMPLE_RATE,'sound test')))
    for token in sorted(tokens):
        safe=re.sub(r'[^a-z0-9]+','_',token.lower()).strip('_')
        jobs.append(asyncio.create_task(synth_one(sem,token,AUDIO_DIR/f't_{safe}.mp3',WORD_RATE,f'token {token}')))
    await asyncio.gather(*jobs)
    wc=len(list(AUDIO_DIR.glob('w_*.mp3'))); ec=len(list(AUDIO_DIR.glob('e_*.mp3')))
    tc=len(list(AUDIO_DIR.glob('t_*.mp3')))
    test_ok=(AUDIO_DIR/'test_ava.mp3').exists() and (AUDIO_DIR/'test_ava.mp3').stat().st_size>700
    if wc != len(data) or ec != len(data) or tc != len(tokens) or not test_ok:
        raise RuntimeError(f'coverage mismatch words={wc}/{len(data)} examples={ec}/{len(data)} tokens={tc}/{len(tokens)} test={test_ok}')
    (AUDIO_DIR/'voice_pack.txt').write_text(
        f'friendly_name=Microsoft Ava Online (Natural) - English (United States)\nvoice={VOICE}\nword_rate={WORD_RATE}\nexample_rate={EXAMPLE_RATE}\nitems={len(data)}\ntokens={tc}\n',encoding='utf-8')
    print(f'Generated Microsoft Ava Online (Natural): {wc} words + {ec} examples + {tc} clickable tokens')

if __name__=='__main__': asyncio.run(main())
