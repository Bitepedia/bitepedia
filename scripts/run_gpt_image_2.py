"""Run GPT-Image-2 (snapshot gpt-image-2-2026-04-21) on all 3 genres × 2 reps.

Requires OPENAI_API_KEY in env or in drilldown/.dev.vars.
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _load_env import load as load_env

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "output" / "gpt-image-2"
PROMPTS = json.loads((ROOT / "prompts" / "built_prompts.json").read_text())

MODEL = "gpt-image-2"
PRICE_PER_IMAGE_USD = 0.21  # rough estimate; refine after first response


def run_one(genre: str, seed: int, client):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    stem = f"{genre}_seed{seed}"
    png_path = OUTDIR / f"{stem}.png"
    meta_path = OUTDIR / f"{stem}.json"
    if png_path.exists() and meta_path.exists():
        print(f"  [skip] {stem}")
        return json.loads(meta_path.read_text())

    prompt = PROMPTS[genre]["prompt"]
    t0 = time.time()
    err = None
    raw = None
    try:
        raw = client.images.generate(
            model=MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="high",
            n=1,
        )
    except Exception as e:
        err = repr(e)
    dt = time.time() - t0

    meta = {
        "model": MODEL,
        "provider": "openai",
        "genre": genre,
        "seed_label": f"seed{seed}",
        "prompt": prompt,
        "params": {"size": "1024x1024", "quality": "high"},
        "price_usd_est": PRICE_PER_IMAGE_USD,
        "latency_s": round(dt, 2),
        "error": err,
    }

    if raw and raw.data:
        img = raw.data[0]
        if hasattr(raw, "model") and raw.model:
            meta["response_model_snapshot"] = raw.model
        if getattr(img, "b64_json", None):
            png_path.write_bytes(base64.b64decode(img.b64_json))
            meta["png_path"] = str(png_path.relative_to(ROOT))
            meta["bytes"] = png_path.stat().st_size
        elif getattr(img, "url", None):
            import urllib.request
            with urllib.request.urlopen(img.url, timeout=60) as r:
                png_path.write_bytes(r.read())
            meta["image_url"] = img.url
            meta["png_path"] = str(png_path.relative_to(ROOT))
            meta["bytes"] = png_path.stat().st_size
        if hasattr(raw, "usage") and raw.usage:
            try:
                meta["usage"] = raw.usage.model_dump() if hasattr(raw.usage, "model_dump") else dict(raw.usage)
            except Exception:
                meta["usage"] = str(raw.usage)

    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    status = "OK" if (png_path.exists() and not err) else f"FAIL {err}"
    print(f"  [{status}] {stem}  {dt:.1f}s")
    return meta


def main():
    env = load_env()
    if env.get("OPENAI_API_KEY") != "<set>":
        print("ERROR: OPENAI_API_KEY not loaded. Append to drilldown/.dev.vars.", file=sys.stderr)
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI()

    total_cost = 0.0
    for g in ["anatomy", "component", "ingredient"]:
        for s in [1, 2]:
            print(f"-> {g} seed{s}")
            m = run_one(g, s, client)
            if not m.get("error"):
                total_cost += PRICE_PER_IMAGE_USD

    print(f"\nEstimated cost: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
