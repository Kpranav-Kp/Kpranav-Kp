import os
import json
from github_api import fetch_repos, fetch_topics, fetch_languages, fetch_repo_contents, fetch_releases
from analytics import compute
from renderer import render_svg

ASSETS_DIR = "assets"
OUTPUT_SVG = os.path.join(ASSETS_DIR, "developer-dna.svg")
DATA_FILE = os.path.join(ASSETS_DIR, "engineering-data.json")


def main():
    repos = fetch_repos()

    fetched_topics = {}
    fetched_langs = {}
    fetched_contents = {}
    fetched_releases = {}

    for repo in repos:
        if repo.get("fork", False):
            continue
        key = repo["url"]
        fetched_topics[key] = fetch_topics(key)
        fetched_langs[key] = fetch_languages(repo["languages_url"])
        fetched_contents[key] = fetch_repo_contents(repo["contents_url"])
        fetched_releases[key] = fetch_releases(repo["releases_url"])

    old_data = None
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except Exception:
            pass

    data = compute(repos, fetched_topics, fetched_langs, fetched_contents, fetched_releases, old_data)

    svg = render_svg(data)

    os.makedirs(ASSETS_DIR, exist_ok=True)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)

    data_out = {k: v for k, v in data.items() if k != "network"}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data_out, f, indent=2)

    print("Engineering Insights SVG generated successfully.")


if __name__ == "__main__":
    main()
