import os
import requests

GH_TOKEN = os.getenv("GH_TOKEN")
GITHUB_USERNAME = "Kpranav-Kp"


def _headers():
    return {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}


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


def fetch_commit_count(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=1"
    resp = requests.get(url, headers=_headers())
    if resp.status_code not in (200, 201):
        return 0
    data = resp.json()
    if not isinstance(data, list) or len(data) == 0:
        return 0
    link = resp.headers.get("Link", "")
    if not link:
        return 1
    for part in link.split(","):
        if 'rel="last"' in part:
            import re
            m = re.search(r'[?&]page=(\d+)', part)
            if m:
                return int(m.group(1))
    return 1
