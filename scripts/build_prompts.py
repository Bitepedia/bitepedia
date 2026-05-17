"""Assemble final prompts by interpolating style anchors into genre templates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = json.loads((ROOT / "prompts" / "prompts.json").read_text())

anchors = spec["style_anchors"]
tpl = spec["prompt_template"]

built = {}
for genre_key, g in spec["genres"].items():
    prompt = tpl.format(
        subject_clause=g["subject_clause"],
        composition_clause=g["composition_clause"],
        anchor_1=anchors[0],
        anchor_2=anchors[1],
        anchor_3=anchors[2],
        anchor_4=anchors[3],
    )
    built[genre_key] = {
        "label": g["label"],
        "prompt": prompt,
        "negative": ", ".join(spec["negative_anchors"]),
    }

out = ROOT / "prompts" / "built_prompts.json"
out.write_text(json.dumps(built, indent=2, ensure_ascii=False))
print(f"Wrote {out}")
for k, v in built.items():
    print(f"\n=== {k} ===\n{v['prompt']}\n")
