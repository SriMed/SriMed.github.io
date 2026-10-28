"""Publish only explicitly selected Notion content as a static Quarto include."""

import argparse
from datetime import date
from html import escape
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
from uuid import UUID


ROOT = Path(__file__).resolve().parents[1]
INCLUDE = Path("_includes/reading.qmd")
LIMIT = 5


def rich_text(value):
    return "".join(part.get("plain_text", part.get("text", {}).get("content", "")) for part in value)


def public_readings(pages):
    """Allowlist public fields and discard unchecked, archived, or unsafe entries."""
    selected = []
    for page in pages:
        props = page.get("properties", {})
        if page.get("archived") or page.get("in_trash") or props.get("Show on website", {}).get("checkbox") is not True:
            continue
        title = rich_text(props.get("Title", {}).get("title", []))
        link = props.get("Link", {}).get("url", "") or ""
        parsed = urllib.parse.urlparse(link)
        if not title or parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError("Selected content needs a title and a public HTTP(S) link")
        period = props.get("Date Read", {}).get("date") or {}
        start, end = period.get("start"), period.get("end")
        for day in (start, end):
            if day:
                date.fromisoformat(day)  # This site displays calendar dates, not timestamps.
        selected.append({
            "title": title,
            "authors": rich_text(props.get("Authors", {}).get("rich_text", [])),
            "link": link,
            "progress": (props.get("Progress", {}).get("select") or {}).get("name", ""),
            "type": (props.get("Type", {}).get("select") or {}).get("name", ""),
            "published": rich_text(props.get("Published", {}).get("rich_text", [])),
            "start": start,
            "end": end,
        })
    # Stable ties avoid shuffling readings that share a reading date.
    selected.sort(key=lambda item: (item["title"].casefold(), item["link"]))
    selected.sort(key=lambda item: item["start"] or "", reverse=True)
    return selected[:LIMIT]


def query_notion(token, data_source_id):
    source = str(UUID(data_source_id))
    request = urllib.request.Request(
        f"https://api.notion.com/v1/data_sources/{source}/query",
        data=json.dumps({
            "filter": {"property": "Show on website", "checkbox": {"equals": True}},
            "sorts": [{"property": "Date Read", "direction": "descending"}, {"property": "Title", "direction": "ascending"}],
            "page_size": LIMIT,
        }).encode(),
        headers={"Authorization": f"Bearer {token}", "Notion-Version": "2025-09-03", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["results"]
    except urllib.error.HTTPError as error:
        # Never echo the credential or the private response body into build logs.
        raise RuntimeError(f"Notion sync failed (HTTP {error.code}); check the connection and database schema") from None


def date_label(start, end):
    if not start:
        return ""
    first = date.fromisoformat(start)
    label = f"{first:%b} {first.day}"
    if not end or end == start:
        return f"{label}, {first.year}"
    last = date.fromisoformat(end)
    if first.year != last.year:
        return f"{label}, {first.year} – {last:%b} {last.day}, {last.year}"
    if first.month == last.month:
        return f"{label}–{last.day}, {first.year}"
    return f"{label} – {last:%b} {last.day}, {first.year}"


def write_include(readings, root=ROOT):
    lines = ["```{=html}", '<ul class="reading-list" aria-label="Selected content">']
    for item in readings:
        media_type = item.get("type", "")
        complete = {"Podcast": "Listened", "Video": "Watched"}.get(media_type, "Read")
        interacted = date_label(item.get("start"), item.get("end"))
        published = item.get("published", "")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", published):
            published = date_label(published, None)
        metadata = [escape(item["authors"])] if item.get("authors") else []
        if media_type:
            metadata.append(escape(media_type))
        if published:
            metadata.append(escape(published))
        lines.extend([
            '<li class="reading-item">',
            f'<h2><a href="{escape(item["link"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(item["title"])}</a></h2>',
            f'<p class="reading-meta">{" · ".join(metadata)}</p>',
            '<div class="reading-dates">',
            f'<span class="reading-activity-date">{complete}: {interacted}</span>' if interacted else "",
            '</div></li>',
        ])
    lines.extend(['</ul>', "```", ""])
    if not readings:
        lines = ["Selected content will appear here soon.\n"]
    path = root / INCLUDE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-file", type=Path, help="Local Notion API response for an offline preview")
    parser.add_argument("--empty", action="store_true", help="Generate an empty list for local preview without credentials")
    args = parser.parse_args()
    if args.empty:
        pages = []
    elif args.from_file:
        pages = json.loads(args.from_file.read_text())["results"]
    else:
        token = os.environ.get("NOTION_TOKEN")
        source = os.environ.get("NOTION_READING_DATA_SOURCE_ID")
        if not token or not source:
            parser.error("Set NOTION_TOKEN and NOTION_READING_DATA_SOURCE_ID, or use --empty for local preview")
        pages = query_notion(token, source)
    readings = public_readings(pages)
    write_include(readings)
    print(f"Prepared {len(readings)} selected content items")


if __name__ == "__main__":
    main()
