import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor

GH_TOKEN = os.getenv("GH_TOKEN")
GITHUB_USERNAME = "Kpranav-Kp"

_SESSION = requests.Session()
_LIST_PAGES = {}


def _headers():
    return {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}


def _get(url):
    for attempt in range(4):
        resp = _SESSION.get(url, headers=_headers())
        if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
            retry = int(resp.headers.get("Retry-After", 30))
            time.sleep(retry)
            continue
        return resp
    return resp


def fetch_repos():
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100&type=owner&sort=pushed"
    resp = requests.get(url, headers=_headers())
    if resp.status_code != 200:
        print(f"Failed to fetch repos. Status: {resp.status_code}")
        exit(1)
    repos = resp.json()
    if not isinstance(repos, list):
        print("Failed to parse repositories.")
        exit(1)
    return repos


def fetch_topics(repo_url):
    resp = requests.get(repo_url + "/topics", headers=_headers())
    if resp.status_code == 200:
        return resp.json().get("names", [])
    return []


def fetch_languages(languages_url):
    resp = requests.get(languages_url, headers=_headers())
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict) and "message" not in data:
            return data
    return {}


def fetch_repo_contents(contents_url):
    url = contents_url.replace("{+path}", "")
    resp = requests.get(url, headers=_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def fetch_releases(releases_url):
    resp = requests.get(releases_url, headers=_headers())
    if resp.status_code == 200:
        return resp.json()
    return []


def fetch_commit_history(repo):
    url = f"https://api.github.com/repos/{repo['full_name']}/commits?per_page=100"
    items = []
    while url:
        resp = _get(url)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not isinstance(data, list) or len(data) == 0:
            break
        for c in data:
            if not isinstance(c, dict):
                continue
            sha = c.get("sha")
            commit = c.get("commit") or {}
            author = commit.get("author") or {}
            ts = author.get("date")
            if sha and ts:
                items.append({"sha": sha, "date": ts})
        if not resp.links.get("next"):
            break
        url = resp.links["next"]["url"]
    return items


def fetch_commit_stats(repo):
    """Accurate per-repo line totals via individual commit detail stats."""
    full_name = repo["full_name"]
    added = deleted = 0

    def detail(sha):
        resp = _get(f"https://api.github.com/repos/{full_name}/commits/{sha}")
        if resp.status_code != 200:
            return 0, 0
        stats = (resp.json() or {}).get("stats") or {}
        return int(stats.get("additions") or 0), int(stats.get("deletions") or 0)

    shas = []
    url = f"https://api.github.com/repos/{full_name}/commits?per_page=100"
    while url:
        resp = _get(url)
        if resp.status_code != 200:
            break
        data = resp.json()
        if not isinstance(data, list) or len(data) == 0:
            break
        for c in data:
            if isinstance(c, dict) and c.get("sha"):
                shas.append(c["sha"])
        if not resp.links.get("next"):
            break
        url = resp.links["next"]["url"]

    with ThreadPoolExecutor(max_workers=8) as pool:
        for add, dele in pool.map(detail, shas):
            added += add
            deleted += dele
    return {"added": added, "deleted": deleted}
