"""Load credentials from drilldown/.dev.vars into os.environ."""
import os
import re
from pathlib import Path

DEV_VARS = Path("/Users/staff/Projects/AI创意作品/drilldown/.dev.vars")


def load():
    if not DEV_VARS.exists():
        raise FileNotFoundError(f"{DEV_VARS} not found")
    for line in DEV_VARS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^([A-Z_][A-Z0-9_]*)=(.*)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
        os.environ.setdefault(key, val)
    if "FAL_API_KEY" in os.environ and "FAL_KEY" not in os.environ:
        os.environ["FAL_KEY"] = os.environ["FAL_API_KEY"]
    return {k: ("<set>" if k in os.environ else "<missing>")
            for k in ("FAL_KEY", "FAL_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY")}


if __name__ == "__main__":
    print(load())
