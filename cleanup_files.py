#!/usr/bin/env python3
from pathlib import Path
import os

TARGET_EXT = {".tmp", ".log", ".bak", ".old"}
MIN_SIZE_MB = 50


def candidates(root: Path):
    min_bytes = MIN_SIZE_MB * 1024 * 1024
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            try:
                if p.suffix.lower() in TARGET_EXT or p.stat().st_size >= min_bytes:
                    yield p
            except OSError:
                continue


def main():
    root = Path.home()
    print(f"Scanning {root} for cleanup candidates...")
    files = list(candidates(root))[:200]
    if not files:
        print("No cleanup candidates found.")
        return

    for p in files:
        size_mb = p.stat().st_size / (1024 * 1024)
        ans = input(f"Delete {p} ({size_mb:.1f} MB)? [y/N]: ").strip().lower()
        if ans == "y":
            try:
                p.unlink()
                print("Deleted.")
            except OSError as e:
                print(f"Could not delete: {e}")


if __name__ == "__main__":
    main()
