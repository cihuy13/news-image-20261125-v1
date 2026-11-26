#!/usr/bin/env python3
"""Copy the pre-rendered entry image to the output directory."""
import os
import shutil
import sys


def run():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print("error: entry.png missing next to main.py", file=sys.stderr)
        return 1
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    if not os.path.isfile(dst) or os.path.getsize(dst) != os.path.getsize(src):
        print("error: copied entry.png is missing or incomplete", file=sys.stderr)
        return 1
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(run())
