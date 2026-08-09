import os
import json
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from github_api import fetch_repos, fetch_topics, fetch_languages, fetch_repo_contents, fetch_releases, fetch_commit_history, fetch_commit_stats
from analytics import compute
from renderer import render_svg, render_city

ASSETS_DIR = "assets"
OUTPUT_SVG = os.path.join(ASSETS_DIR, "developer-dna.svg")
OUTPUT_CITY = os.path.join(ASSETS_DIR, "developer-city.svg")
DATA_FILE = os.path.join(ASSETS_DIR, "engineering-data.json")


def main():
    repos = fetch_repos()

    fetched_topics = {}
    fetched_langs = {}
    fetched_contents = {}
    fetched_releases = {}
    fetched_commit_dates = {}
    fetched_commit_stats = {}

    for repo in repos:
        if repo.get("fork", False):
            continue
        key = repo["url"]
        fetched_topics[key] = fetch_topics(key)
        fetched_langs[key] = fetch_languages(repo["languages_url"])
        fetched_contents[key] = fetch_repo_contents(repo["contents_url"])
        fetched_releases[key] = fetch_releases(repo["releases_url"])
        fetched_commit_dates[key] = [c.get("date") for c in fetch_commit_history(repo) if c.get("date")]
        fetched_commit_stats[key] = fetch_commit_stats(repo)

    old_data = None
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except Exception:
            pass

    data = compute(repos, fetched_topics, fetched_langs, fetched_contents, fetched_releases, fetched_commit_dates, fetched_commit_stats, old_data)

    svg = render_svg(data)
    city = render_city(data.get("activity", []))

    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)

    with open(OUTPUT_CITY, "w", encoding="utf-8") as f:
        f.write(city)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Profile Analytics SVG generated successfully.")


if __name__ == "__main__":
    main()
