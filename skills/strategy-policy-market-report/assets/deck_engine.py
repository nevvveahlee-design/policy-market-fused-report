# -*- coding: utf-8 -*-
"""
Project-owned HTML deck rendering primitives for strategy-policy-market-report.

Adapted from an authorized internal deck engine and trimmed to the interfaces
this repository needs for optional HTML/PDF rendering.
"""

from __future__ import annotations

import html
import re
from pathlib import Path


BRAND = "Strategy Policy Market Report"

CSS = """
:root{
  --navy:#0f2740;
  --blue:#2769a7;
  --ink:#1f2933;
  --muted:#66788a;
  --hair:#d9e1ea;
  --wash:#f5f7fa;
  --serif:Georgia,'Times New Roman',serif;
  --sans:'Segoe UI',Arial,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:#425161}
.slide{
  width:1280px;height:720px;margin:0 auto;background:#fff;color:var(--ink);
  page-break-after:always;position:relative;overflow:hidden;font-family:var(--sans)
}
.slide.cover{background:linear-gradient(135deg,var(--navy),#163556);color:#fff}
.pad{padding:44px 52px 54px;height:100%;display:flex;flex-direction:column}
h1{margin:0;font:400 29px/1.2 var(--serif);color:var(--navy)}
.cover h1{color:#fff;font-size:46px;line-height:1.08}
.deck{margin-top:8px;color:var(--muted);font-size:14px}
.cover .deck{color:#dbe6f0}
.hr{height:2px;background:var(--navy);margin:14px 0 18px}
.lead{font:400 18px/1.6 var(--serif);color:var(--navy)}
.body{flex:1;display:flex;flex-direction:column;gap:18px;min-height:0}
.heroes{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:18px}
.hero{border-top:2px solid var(--navy);padding-top:10px}
.hero .n{font:400 30px/1 var(--serif);color:var(--blue)}
.hero .l{margin-top:7px;font-size:11px;line-height:1.45;color:var(--muted)}
.hero .t{margin-top:8px;font-size:12px;line-height:1.45;color:var(--navy);font-weight:700}
.hero p{margin:6px 0 0;font-size:11.5px;line-height:1.6}
.prose{display:grid;grid-template-columns:1fr 1fr;gap:26px;flex:1}
.block{background:var(--wash);border-left:3px solid var(--blue);padding:14px 16px}
.block h2{margin:0 0 8px;font-size:13px;line-height:1.45;color:var(--navy)}
.block p,.block li{font-size:12px;line-height:1.68}
.block p{margin:0}
.block ul{margin:0;padding-left:18px}
.sources{columns:2;column-gap:34px}
.source{break-inside:avoid;border-bottom:1px solid var(--hair);padding:6px 0;font-size:10.5px;line-height:1.5}
.source a{color:var(--ink);text-decoration:none;word-break:break-all}
.foot{
  position:absolute;left:52px;right:52px;bottom:0;padding:10px 0 16px;
  border-top:1px solid var(--hair);display:flex;font-size:9px;color:var(--muted)
}
.foot .brand{font-weight:700;color:var(--navy);letter-spacing:.06em}
.foot .pg{margin-left:auto;color:var(--navy);font-weight:700}
@media screen{
  html,body{height:100%;overflow:auto}
}
@media print{
  body{background:#fff}
}
"""


def _escape(value: object) -> str:
    return html.escape(str(value))


def _rich_text(text: str) -> str:
    escaped = _escape(text).replace("\r\n", "\n").replace("\r", "\n")
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    paragraphs = []
    for block in escaped.split("\n\n"):
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if not lines:
            continue
        if all(line.startswith("- ") for line in lines):
            items = "".join(f"<li>{line[2:]}</li>" for line in lines)
            paragraphs.append(f"<ul>{items}</ul>")
        else:
            body = "<br>".join(lines)
            paragraphs.append(f"<p>{body}</p>")
    return "".join(paragraphs) or "<p></p>"


def _head(title: str, deck_line: str | None = None) -> str:
    deck_html = f'<div class="deck">{_escape(deck_line)}</div>' if deck_line else ""
    return f"<h1>{_escape(title)}</h1>{deck_html}<div class=\"hr\"></div>"


def _foot(source_note: str, page_number: int) -> str:
    return (
        f'<div class="foot"><span><span class="brand">{_escape(BRAND)}</span> '
        f'&nbsp;&nbsp;Source: {_escape(source_note)}</span>'
        f'<span class="pg">{page_number:02d}</span></div>'
    )


def cover(title: str, subtitle: str) -> str:
    return (
        '<div class="slide cover"><div class="pad">'
        f"<h1>{_escape(title)}</h1>"
        f'<div class="deck">{_escape(subtitle)}</div>'
        '<div class="body"></div>'
        f"{_foot('Report scope', 1)}"
        "</div></div>"
    )


def answer_slide(title: str, deck_line: str, governing: str, pillars: list[dict], page_number: int) -> str:
    cells = []
    for pillar in pillars:
        cells.append(
            '<div class="hero">'
            f'<div class="n">{_escape(pillar["metric"])}</div>'
            f'<div class="l">{_escape(pillar["label"])}</div>'
            f'<div class="t">{_escape(pillar["title"])}</div>'
            f"<p>{_escape(pillar['support'])}</p>"
            "</div>"
        )
    return (
        '<div class="slide"><div class="pad">'
        f"{_head(title, deck_line)}"
        '<div class="body">'
        f'<div class="lead">{_escape(governing)}</div>'
        f'<div class="heroes" style="--n:{len(pillars)}">{"".join(cells)}</div>'
        "</div>"
        f"{_foot('Report synthesis', page_number)}"
        "</div></div>"
    )


def prose_slide(title: str, deck_line: str, blocks: list[tuple[str, str]], page_number: int) -> str:
    body = "".join(
        f'<div class="block"><h2>{_escape(heading)}</h2>{_rich_text(text)}</div>'
        for heading, text in blocks
    )
    return (
        '<div class="slide"><div class="pad">'
        f"{_head(title, deck_line)}"
        f'<div class="body"><div class="prose">{body}</div></div>'
        f"{_foot('Report sections', page_number)}"
        "</div></div>"
    )


def sources_slide(title: str, deck_line: str, sources: list[dict], page_number: int) -> str:
    if sources:
        items = "".join(
            '<div class="source">'
            f'<strong>{_escape(item["source_name"])}</strong><br>'
            f'{_escape(item["date"])}<br>'
            f'<a href="{_escape(item["url"])}">{_escape(item["url"])}</a><br>'
            f'{_escape(item["claim"])}'
            "</div>"
            for item in sources
        )
    else:
        items = '<div class="source">No structured sources were available for this run.</div>'
    return (
        '<div class="slide"><div class="pad">'
        f"{_head(title, deck_line)}"
        f'<div class="body"><div class="sources">{items}</div></div>'
        f"{_foot('Evidence register', page_number)}"
        "</div></div>"
    )


def render(slides: list[str], out_html: Path) -> Path:
    document = (
        "<!doctype html>"
        "<html><head><meta charset=\"utf-8\">"
        "<title>Strategy Policy Market Report</title>"
        f"<style>{CSS}</style>"
        "</head><body>"
        f"<div id=\"deck\">{''.join(slides)}</div>"
        "</body></html>"
    )
    out_html = Path(out_html)
    out_html.write_text(document, encoding="utf-8")
    return out_html
