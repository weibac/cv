#!/usr/bin/env python3
"""
main.py – Flexible LaTeX‑CV generator with i18n
================================================

This script converts a single multilingual JSON file into a LaTeX résumé.
Usage
-----
```bash
python main.py cv.json              # English (default) -> stdout
python main.py cv.json -l es -o cv.tex  # Spanish -> cv.tex
```

JSON Schema (excerpt)
---------------------
```json
{
  "contact": { … },
  "sections": [
    {
      "id": "dev‑technologies",
      "label": { "en": "Stack", "es": "Stack" },
      "type": "items‑compact",
      "items": [
        { "label": "Python", "url": "https://python.org" },
        { "label": "Docker", "url": "https://docker.com" }
      ]
    }
  ]
}
```
"""

from __future__ import annotations
import argparse
import json
import pathlib
import sys
from typing import Dict, List, Any

SPECIALS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}

PREAMBLE = [
    r"\documentclass{article}",
    r"\usepackage[colorlinks=true, urlcolor=blue]{hyperref}",
    r"\usepackage[margin=1in]{geometry}",
    r"\usepackage[margin=1in]{geometry}"
    r"\begin{document}"
]

def tex_escape(s: str) -> str:
    """Escape LaTeX special chars."""
    return "".join(SPECIALS.get(c, c) for c in s)

def pick(lang: str, field: Any) -> Any:
    """Return language‑specific value or fallback to English/str."""
    if isinstance(field, dict):
        return field.get(lang) or field.get("en") or next(iter(field.values()))
    return field

def href(url: str | None, text: str) -> str:
    text = tex_escape(text)
    return f"\\href{{{url}}}{{{text}}}" if url else text

# ────────────────────────────────────────────────────────────────────────────────
# Rendering helpers
# ────────────────────────────────────────────────────────────────────────────────

def render_paragraph(p: str) -> str:
    return tex_escape(p) + "\\par\n"

def render_items(section: Dict[str, Any], lang: str) -> str:
    """Bulleted list."""
    lines: List[str] = [pick(lang, section.get("label", section["id"]))]
    for item in section["items"]:
        label = pick(lang, item.get("label", ""))
        value = pick(lang, item.get("value", ""))
        url = pick(lang, item.get("url"))
        bullet = href(url, label)
        if value:
            bullet += f" — {tex_escape(str(value))}"
        lines.append(f"\\item {bullet}")
    return "\\section*{" + tex_escape(lines[0]) + "}" + "\n\\begin{itemize}\n" + "\n".join(lines[1:]) + "\n\\end{itemize}\n"

def render_items_compact(section: Dict[str, Any], lang: str) -> str:
    """Comma‑separated list on a single line."""
    header = tex_escape(pick(lang, section.get("label", section["id"])))
    rendered: List[str] = []
    for item in section["items"]:
        label = pick(lang, item.get("label", ""))
        value = pick(lang, item.get("value"))
        url = pick(lang, item.get("url"))
        piece = href(url, label)
        if value:
            piece += f" ({tex_escape(str(value))})"
        rendered.append(piece)
    body = ", ".join(rendered) + "."
    return f"\\section*{{{header}}}\n{body}\n"

def render_section(section: Dict[str, Any], lang: str) -> str:
    stype = section.get("type", "content")
    if stype == "content":
        header = tex_escape(pick(lang, section.get("label", section["id"])))
        return f"\\section*{{{header}}}\n" + render_paragraph(pick(lang, section["content"]))
    if stype == "items":
        return render_items(section, lang)
    if stype == "items-compact":
        return render_items_compact(section, lang)
    raise ValueError(f"Unknown section type: {stype}")

# ────────────────────────────────────────────────────────────────────────────────
# Main assembly
# ────────────────────────────────────────────────────────────────────────────────

def build_cv(data: Dict[str, Any], lang: str) -> str:
    parts: List[str] = PREAMBLE
    # Name heading
    c = data.get("contact", {})
    name_parts = [c.get("name", {}).get(k, "") for k in ("first", "middle", "last")]
    parts.append("\\begin{center}\n{\\Large "+ " ".join(tex_escape(p) for p in name_parts if p)+"}\\\n\\end{center}\n")
    # Sections
    for sec in data.get("sections", []):
        parts.append(render_section(sec, lang))
    parts.append(r"\end{document}")
    return "\n".join(parts)

# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSON → LaTeX CV generator (i18n)")
    parser.add_argument("cv_json", type=pathlib.Path, help="Path to CV JSON file")
    parser.add_argument("-l", "--lang", default="en", choices=["en", "es"], help="Locale to render")
    parser.add_argument("-o", "--output", type=pathlib.Path, help="Write LaTeX to this file")
    args = parser.parse_args()

    with args.cv_json.open() as fp:
        data = json.load(fp)

    latex = build_cv(data, args.lang)

    if args.output:
        args.output.write_text(latex, encoding="utf-8")
    else:
        sys.stdout.write(latex)

