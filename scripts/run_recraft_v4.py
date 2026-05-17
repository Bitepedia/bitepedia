"""Run Recraft V4 on all 3 genres × 2 reps via fal-ai/recraft/v4/text-to-image.

Outputs per-image PNG + sibling JSON metadata (cost, params, prompt, timing).
Idempotent: skips images already on disk.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _load_env import load as load_env

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "output" / "recraft-v4"
PROMPTS = json.loads((ROOT / "prompts" / "built_prompts.json").read_text())

MODEL_SLUG = "fal-ai/recraft/v4/text-to-image"
PRICE_PER_IMAGE_USD = 0.04   # per Ryan's spec
IMAGE_SIZE = "square_hd"      # 1024x1024 for cross-model comparability
STYLE = "any"                  # let prompt drive; no preset to keep fair vs FLUX/GPT


def fetch_url(url: str, dest: Path):
    with urllib.request.urlopen(url, timeout=60) as resp:
        dest.write_bytes(resp.read())


def run_one(genre: str, seed: int, fal_client):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    stem = f"{genre}_seed{seed}"
    png_path = OUTDIR / f"{stem}.png"
    meta_path = OUTDIR / f"{stem}.json"
    if png_path.exists() and meta_path.exists():
        print(f"  [skip] {stem} already exists")
        return json.loads(meta_path.read_text())

    prompt = PROMPTS[genre]["prompt"]
    arguments = {
        "prompt": prompt,
        "image_size": IMAGE_SIZE,
        "style": STYLE,
    }

    t0 = time.time()
    err = None
    result = None
    try:
        result = fal_client.subscribe(
            MODEL_SLUG,
            arguments=arguments,
            with_logs=False,
        )
    except Exception as e:
        err = repr(e)
    dt = time.time() - t0

    meta = {
        "model_slug": MODEL_SLUG,
        "model_snapshot": "recraft-v4 (fal-hosted, snapshot id pending in response)",
        "provider": "fal.ai",
        "genre": genre,
        "seed_label": f"seed{seed}",
        "prompt": prompt,
        "params": arguments,
        "price_usd": PRICE_PER_IMAGE_USD,
        "latency_s": round(dt, 2),
        "error": err,
        "raw_response_keys": list(result.keys()) if isinstance(result, dict) else None,
    }

    if result and isinstance(result, dict):
        imgs = result.get("images") or []
        if imgs and imgs[0].get("url"):
            url = imgs[0]["url"]
            meta["image_url"] = url
            try:
                fetch_url(url, png_path)
                meta["png_path"] = str(png_path.relative_to(ROOT))
                meta["bytes"] = png_path.stat().st_size
            except Exception as e:
                meta["download_error"] = repr(e)

    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    status = "OK" if (png_path.exists() and not err) else f"FAIL {err}"
    print(f"  [{status}] {stem}  {dt:.1f}s")
    return meta


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true", help="Run a single anatomy seed1 image only")
    args = p.parse_args()

    env = load_env()
    if env.get("FAL_KEY") != "<set>":
        print("ERROR: FAL_KEY not loaded", file=sys.stderr)
        sys.exit(1)

    import fal_client  # imported after env load

    genres = ["anatomy", "component", "ingredient"]
    seeds = [1, 2]
    if args.smoke:
        genres, seeds = ["anatomy"], [1]

    total_cost = 0.0
    results = []
    for g in genres:
        for s in seeds:
            print(f"-> {g} seed{s}")
            m = run_one(g, s, fal_client)
            results.append(m)
            if not m.get("error"):
                total_cost += PRICE_PER_IMAGE_USD

    summary_path = OUTDIR / "_run_summary.json"
    summary_path.write_text(json.dumps({
        "total_images": len(results),
        "successful": sum(1 for r in results if not r.get("error")),
        "estimated_total_cost_usd": round(total_cost, 4),
        "results": results,
    }, indent=2, ensure_ascii=False))
    print(f"\nWrote summary: {summary_path}")
    print(f"Estimated cost so far: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
