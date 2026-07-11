---
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
