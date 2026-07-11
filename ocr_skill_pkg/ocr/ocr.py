#!/usr/bin/env python3
"""OCR a single image or a folder of images and print extracted text.

Usage:
  python ocr.py <image_or_folder> [--lang en,ar] [--out result.txt]

Depends on easyocr (installed in the hermes venv).
"""
import sys, os, glob

def main():
    args = sys.argv[1:]
    if not args:
        print("usage: ocr.py <image_or_folder> [--lang en,ar] [--out file.txt]")
        return 1
    target = args[0]
    lang = "en"
    out = None
    if "--lang" in args:
        lang = args[args.index("--lang")+1]
    if "--out" in args:
        out = args[args.index("--out")+1]
    import easyocr
    reader = easyocr.Reader(lang.split(","), gpu=False)
    files = []
    if os.path.isdir(target):
        for ext in ("*.png","*.jpg","*.jpeg","*.bmp","*.tiff","*.webp"):
            files += glob.glob(os.path.join(target, ext))
    else:
        files = [target]
    results = []
    for f in files:
        res = reader.readtext(f, detail=0, paragraph=True)
        text = "\n".join(res)
        results.append(f"=== {os.path.basename(f)} ===\n{text}")
    out_text = "\n\n".join(results)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(out_text)
        print(f"wrote {out}")
    else:
        print(out_text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
