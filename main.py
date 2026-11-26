"""news-image-20261125-v1: copy the rendered entry image to the output dir.

The image is a pre-rendered 1024x1024 PNG committed in this repository
(entry.png). This program uses only the Python standard library, so it
runs in the grader's minimal environment with nothing installed.
"""

import os
import shutil
import sys

MAX_BYTES = 1048576


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    dst = os.path.join(out_dir, "entry.png")

    if not os.path.isfile(src):
        print("entry.png not found beside main.py", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, dst)

    size = os.path.getsize(dst)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the 1048576 byte limit",
              file=sys.stderr)
        return 1

    if size != os.path.getsize(src):
        print("copied entry.png does not match the committed file",
              file=sys.stderr)
        return 1

    print(f"wrote {dst} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
