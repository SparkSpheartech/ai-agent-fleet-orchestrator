import subprocess, base64

HOST = "192.0.2.100"
# Build OCR skill dir on host to push to each VM
ocr_script = '''#!/usr/bin/env python3
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
        text = "\\n".join(res)
        results.append(f"=== {os.path.basename(f)} ===\\n{text}")
    out_text = "\\n\\n".join(results)
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(out_text)
        print(f"wrote {out}")
    else:
        print(out_text)
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
skill_md = '''---
name: ocr
description: Extract text from images/screenshots/scans (incl. Arabic+English) using easyocr. Use when the user sends a photo of a document, receipt, whiteboard, or any image with text.
---

# OCR Skill

Run `ocr.py` on any image to get its text.

```bash
python /usr/local/lib/hermes-agent/venv/bin/python ~/.hermes/skills/ocr/ocr.py <image> [--lang en,ar] [--out result.txt]
```

- Default language: English. For Arabic+English mixed: `--lang en,ar`.
- Pairs well with the vision toolset for images sent in chat.
- First run downloads ~50MB model weights (cached after).
'''

# Write OCR skill to host
import os
os.makedirs("/tmp/ocr_skill/ocr", exist_ok=True)
with open("/tmp/ocr_skill/ocr/ocr.py","w") as f: f.write(ocr_script)
with open("/tmp/ocr_skill/ocr/SKILL.md","w") as f: f.write(skill_md)
# scp to host
r = subprocess.run(f'scp -o StrictHostKeyChecking=no -r "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\..\\..\\..\\tmp\\ocr_skill" root@{HOST}:/tmp/ 2>&1', shell=True, capture_output=True, text=True, timeout=30)
print("ocr skill to host:", r.stderr.strip()[:80])

# Actually write to a local temp and scp properly
local_skill = r"C:\Users\shaza\Desktop\SparkSphear_App\ocr_skill_pkg\ocr"
os.makedirs(local_skill, exist_ok=True)
with open(os.path.join(local_skill,"ocr.py"),"w") as f: f.write(ocr_script)
with open(os.path.join(local_skill,"SKILL.md"),"w") as f: f.write(skill_md)
r2 = subprocess.run(f'scp -o StrictHostKeyChecking=no -r "C:\\Users\\shaza\\Desktop\\SparkSphear_App\\ocr_skill_pkg" root@{HOST}:/tmp/ocr_skill_pkg', shell=True, capture_output=True, text=True, timeout=30)
print("scp pkg:", r2.stderr.strip()[:80])