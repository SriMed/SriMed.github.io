"""Gate production posts by date and avoid unchanged scheduled deployments."""

import argparse
from datetime import date, datetime, time
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

import yaml


ROOT = Path(__file__).resolve().parents[1]
TIMEZONE = ZoneInfo("America/New_York")
STATE_FILE = "publication-state.json"


def publication_plan(root, now):
    """Return published paths and draft paths using an 8 a.m. local cutoff."""
    published, hidden = [], []
    for path in sorted((root / "posts").rglob("*.qmd")):
        parts = path.read_text().splitlines()
        if not parts or parts[0] != "---" or "---" not in parts[1:]:
            raise ValueError(f"{path}: missing YAML front matter")
        end = parts.index("---", 1)
        metadata = {}
        for directory in reversed(path.parent.relative_to(root).parents):
            inherited = root / directory / "_metadata.yml"
            if inherited.exists():
                metadata.update(yaml.safe_load(inherited.read_text()) or {})
        inherited = path.parent / "_metadata.yml"
        if inherited.exists():
            metadata.update(yaml.safe_load(inherited.read_text()) or {})
        metadata.update(yaml.safe_load("\n".join(parts[1:end])) or {})
        draft = metadata.get("draft", False)
        if not isinstance(draft, bool):
            raise ValueError(f"{path}: draft must be true or false")
        relative = path.relative_to(root).as_posix()
        if draft:
            hidden.append(relative)
            continue
        value = metadata.get("date")
        # A strict date avoids ambiguous timestamps and locale-dependent dates.
        if isinstance(value, datetime):
            raise ValueError(f"{path}: date must be YYYY-MM-DD")
        try:
            day = date.fromisoformat(str(value))
            if day.isoformat() != str(value):
                raise ValueError("Noncanonical date")
        except ValueError as error:
            raise ValueError(f"{path}: date must be YYYY-MM-DD") from error
        release = datetime.combine(day, time(8), TIMEZONE)
        (published if now >= release else hidden).append(relative)
    return {"posts": published}, hidden


def needs_publication(state, url):
    request = urllib.request.Request(
        url + "?check=" + datetime.now().strftime("%Y%m%d%H%M%S%f"),
        headers={"Cache-Control": "no-cache", "User-Agent": "site-publication-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            deployed = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return True  # Bootstrap sites published before the manifest existed.
        raise
    return deployed != state


def render(root, state, hidden):
    profile = root / "_quarto-publication.yml"
    profile.write_text(yaml.safe_dump({"website": {"drafts": hidden}}))
    try:
        subprocess.run(["quarto", "render", "--profile", "publication"], cwd=root, check=True)
        (root / "_site" / STATE_FILE).write_text(json.dumps(state, indent=2) + "\n")
    finally:
        profile.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "render"])
    parser.add_argument("--state-url", default="https://srimed.github.io/" + STATE_FILE)
    args = parser.parse_args()
    state, hidden = publication_plan(ROOT, datetime.now(TIMEZONE))
    if args.command == "render":
        render(ROOT, state, hidden)
    else:
        needed = needs_publication(state, args.state_url)
        print("Publication due" if needed else "No publication due; skipping build")
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                output.write(f"needed={str(needed).lower()}\n")


if __name__ == "__main__":
    main()
