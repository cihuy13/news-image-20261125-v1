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
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(run())
