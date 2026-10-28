#!/usr/bin/env python3
"""The Xbox launcher: the app built without the game's code, so that it needs no ROM to
build and holds nothing of the game. It runs the game on melonDS's interpreter instead of
recompiled code; the player puts their own ROM in the app's folder on the console.
.github/workflows/xbox-launcher.yml builds it on GitHub, for players without a Windows PC.

Usage (Windows, Visual Studio as in xbox.py): python tools/xbox/launcher.py --build-dir <dir>
The package and its certificate end up in <dir>/package.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'xbox'))
sys.path.insert(0, str(ROOT / 'tests'))
import recomp
import xbox
import clang_cl_smoke


def write_gen(gen):
    """Generated sources without any of the game: no sections are read, so only melonDS's
    own free BIOS is recompiled. The table of the game's screens comes from the layout,
    which holds addresses only (the frontend finds nothing to watch without the code)."""
    gen.mkdir(parents=True, exist_ok=True)
    with patch.object(recomp, 'load_sections', return_value=[]), patch.object(
            sys, 'argv', ['recomp.py', 'none', str(ROOT / 'melonDS' / 'src'), str(gen)]):
        recomp.main()
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'apps.py'), '--layout',
                    str(ROOT / 'layouts' / 'soulsilver-us.json'), str(gen)], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build-dir', type=Path, required=True)
    args = ap.parse_args()
    build = args.build_dir.resolve()
    gen = build / 'gen-launcher'
    write_gen(gen)
    vs = xbox.find_visual_studio()
    msix = clang_cl_smoke.uwp(build, gen, vs, '-DSSR_LAUNCHER=ON')
    print('Xbox launcher: ' + msix, flush=True)
    for name in sorted(os.listdir(os.path.dirname(msix))):
        print('  ' + name, flush=True)


if __name__ == '__main__':
    main()
