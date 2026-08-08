from datetime import datetime, timezone, timedelta
from collections import defaultdict

EXCLUDE_LANGUAGES = {"Jupyter Notebook"}

TOPIC_TO_CATEGORY = {
    "backend": "Backend", "ai-ml": "AI / ML", "ai": "AI / ML",
    "frontend": "Frontend", "research": "Research", "devops": "DevOps",
    "cli": "CLI", "security": "Security", "cybersecurity": "Security",
    "machine-learning": "AI / ML", "ai-security": "Security",
}

PACKAGE_FILES = {
    "requirements.txt", "package.json", "pyproject.toml", "Cargo.toml",
    "CMakeLists.txt", "go.mod", "Gemfile", "Pipfile", "setup.py",
}

TEST_DIRS = {"tests", "test", "__tests__", "spec"}

FRAMEWORK_MAP = {
    "fastapi": "FastAPI", "django": "Django", "django-rest-framework": "Django",
    "flask": "Flask", "react": "React", "node": "Node.js", "nodejs": "Node.js",
    "express": "Express", "nextjs": "Next.js", "vue": "Vue",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "transformers": "Transformers", "spring": "Spring",
    "celery": "Celery",
}

DATABASE_MAP = {
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mongodb": "MongoDB", "mysql": "MySQL", "redis": "Redis",
    "sqlite": "SQLite",
}

INFRA_MAP = {
    "docker": "Docker", "kubernetes": "Kubernetes",
    "vercel": "Vercel", "github-actions": "GitHub Actions",
    "aws": "AWS", "gcp": "GCP", "azure": "Azure",
    "supabase": "Supabase",
}

CONTENTS_FRAMEWORK = {
    "manage.py": "Django", "next.config.js": "Next.js", "nuxt.config.js": "Nuxt",
    "celery.py": "Celery",
}

CONTENTS_INFRA = {
    "Dockerfile": "Docker", "docker-compose.yml": "Docker",
    "nginx.conf": "Nginx", ".github": "GitHub Actions",
}

TECH_COLORS = {}

PALETTE = {
    "green": "#34D399",
    "indigo": "#6366F1",
    "amber": "#FBBF24",
    "rose": "#FB7185",
    "sky": "#38BDF8",
    "violet": "#A78BFA",
    "slate": "#94A3B8",
}

MAX_DAYS = 365


def _recency(last_push, now):
    days = (now - last_push).days
    return max(0, 1 - min(days, MAX_DAYS) / MAX_DAYS)


def _level(pct, score):
    combined = score * 0.6 + (pct / 100) * 0.4
    if combined >= 0.7: return "Advanced"
    if combined >= 0.4: return "Intermediate"
    return "Beginner"


LEVEL_COLORS = {
    "Advanced": PALETTE["indigo"],
    "Intermediate": PALETTE["sky"],
    "Beginner": PALETTE["slate"],
}

COMPLEXITY_COLORS = {
    "Small": PALETTE["indigo"],
    "Medium": PALETTE["amber"],
    "Large": PALETTE["rose"],
}

IST_OFFSET = timedelta(hours=5, minutes=30)
AI_GROUP = {"TensorFlow", "PyTorch", "Transformers", "NumPy", "Pandas"}


def _parse_ts(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def _format_hour(h):
    h = h % 24
    if h == 0: return "12 AM"
    if h < 12: return f"{h} AM"
    if h == 12: return "12 PM"
    return f"{h - 12} PM"


def _range_str(start, end):
    if start == end:
        return start.strftime("%b %d, %Y")
    if start.year == end.year and start.month == end.month:
        return f"{start.strftime('%b %d')} – {end:%d, %Y}"
    if start.year == end.year:
        return f"{start.strftime('%b %d')} – {end:%b %d, %Y}"
    return f"{start.strftime('%b %d, %Y')} – {end.strftime('%b %d, %Y')}"


def _profile_metrics(fetched_commit_dates, fetched_commit_stats, lang_pct, now):
    active_days = set()
    hour_hist = defaultdict(int)
    weekday_hist = defaultdict(int)
    week_set = set()
    total_commits = 0

    for ts in fetched_commit_dates:
        total_commits += 1
        dt = _parse_ts(ts) + IST_OFFSET
        active_days.add(dt.date())
        hour_hist[dt.hour] += 1
        weekday_hist[dt.strftime("%A")] += 1
        week_set.add((dt.isocalendar().year, dt.isocalendar().week))

    cargo = now + IST_OFFSET
    today = cargo.date()
    start = today if today in active_days else today - timedelta(days=1)
    current_streak = 0
    while start in active_days:
        current_streak += 1
        start -= timedelta(days=1)

    sorted_days = sorted(active_days)
    longest = 0
    longest_start = None
    longest_end = None
    cur = 0
    prev = None
    run_start = None
    for d in sorted_days:
        if prev is None or (d - prev).days == 1:
            cur += 1
            if run_start is None:
                run_start = d
        else:
            cur = 1
            run_start = d
        if cur > longest:
            longest = cur
            longest_start = run_start
            longest_end = d
        prev = d

    lines_added = 0
    lines_deleted = 0
    for stats in (fetched_commit_stats or {}).values():
        lines_added += int(stats.get("added", 0) or 0)
        lines_deleted += int(stats.get("deleted", 0) or 0)

    commit_frequency = round(total_commits / max(len(week_set), 1), 1) if week_set else 0

    peak_hour = max(hour_hist, key=hour_hist.get) if hour_hist else None
    peak_day = max(weekday_hist, key=weekday_hist.get) if weekday_hist else None

    habits = []
    if current_streak >= 3:
        habits.append({"label": "Consistent streak", "color": PALETTE["indigo"]})
    if longest >= 7:
        habits.append({"label": "Long streaks", "color": PALETTE["violet"]})
    if peak_hour is not None and (peak_hour >= 22 or peak_hour < 5):
        habits.append({"label": "Night coder", "color": PALETTE["rose"]})
    elif peak_hour is not None and peak_hour < 12:
        habits.append({"label": "Early riser", "color": PALETTE["amber"]})
    total_days = sum(weekday_hist.values())
    weekend_days = weekday_hist.get("Saturday", 0) + weekday_hist.get("Sunday", 0)
    if total_days and (weekend_days / total_days) >= 0.4:
        habits.append({"label": "Weekend warrior", "color": PALETTE["slate"]})
    if commit_frequency and commit_frequency >= 5:
        habits.append({"label": "Fast shipper", "color": PALETTE["sky"]})
    habits = habits[:3]

    return {
        "current_streak": current_streak,
        "longest_streak": longest,
        "longest_range": _range_str(longest_start, longest_end) if longest_start else None,
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "total_commits": int(total_commits),
        "commit_frequency": commit_frequency,
        "peak_hour": _format_hour(peak_hour) if peak_hour is not None else None,
        "peak_day": peak_day,
        "languages_count": 0,
        "habits": habits,
    }


def compute(repos, fetched_topics, fetched_langs, fetched_contents, fetched_releases, fetched_commit_dates=None, fetched_commit_stats=None, old_data=None):
    now = datetime.now(timezone.utc)

    lang_bytes = defaultdict(int)
    lang_repos = defaultdict(set)
    lang_last_push = defaultdict(lambda: datetime(2000, 1, 1, tzinfo=timezone.utc))
    cat_counts = defaultdict(int)
    total_repos = 0
    repo_details = []
    all_ages_days = []
    active_30_count = 0

    for repo in repos:
        if repo.get("fork", False):
            continue
        total_repos += 1
        repo_name = repo["full_name"]
        pushed_at = datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        created_at = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        age_days = (now - created_at).days
        all_ages_days.append(age_days)
        if (now - pushed_at).days < 30:
            active_30_count += 1

        repo_key = repo["url"]
        topics = fetched_topics.get(repo_key, [])
        langs = fetched_langs.get(repo_key, {})
        contents = fetched_contents.get(repo_key, [])
        releases = fetched_releases.get(repo_key, [])

        for t in topics:
            cat = TOPIC_TO_CATEGORY.get(t.lower())
            if cat:
                cat_counts[cat] += 1
                break

        for lang, size in langs.items():
            if lang in EXCLUDE_LANGUAGES or not isinstance(size, (int, float)):
                continue
            lang_bytes[lang] += int(size)
            lang_repos[lang].add(repo_name)
            if pushed_at > lang_last_push[lang]:
                lang_last_push[lang] = pushed_at

        content_names = [c.get("name", "") for c in contents if isinstance(c, dict)]
        content_types = {c.get("name", ""): c.get("type", "") for c in contents if isinstance(c, dict)}

        commit_count = len((fetched_commit_dates or {}).get(repo_key, []))
        repo_weight = max(0.1, 1 - (now - pushed_at).days / 730)
        repo_details.append({
            "name": repo_name,
            "url": repo_key,
            "size": repo.get("size", 0),
            "weight": repo_weight,
            "commit_count": commit_count,
            "topics": topics,
            "langs": [l for l in langs if l not in EXCLUDE_LANGUAGES],
            "num_langs": len([l for l in langs if l not in EXCLUDE_LANGUAGES]),
            "content_names": content_names,
            "has_package": any(f in content_names for f in PACKAGE_FILES),
            "has_tests": any(d in content_names and content_types.get(d) == "dir" for d in TEST_DIRS),
            "has_docker": "Dockerfile" in content_names,
            "has_cicd": ".github" in content_names and content_types.get(".github") == "dir",
            "has_readme": any(n.lower().startswith("readme") for n in content_names),
            "has_license": "LICENSE" in content_names,
            "has_releases": len(releases) > 0,
            "stargazers": repo.get("stargazers_count", 0),
        })

    total_bytes = sum(lang_bytes.values())
    lang_pct = {}
    for lang, b in lang_bytes.items():
        lang_pct[lang] = round((b / total_bytes) * 100, 1) if total_bytes > 0 else 0

    lang_sorted = sorted(lang_pct.items(), key=lambda x: x[1], reverse=True)
    max_repo_count = max((len(v) for v in lang_repos.values()), default=1)

    languages = []
    old_lang_map = {}
    if old_data and "languages" in old_data:
        old_lang_map = {l["name"]: l["percentage"] for l in old_data["languages"]}
    tech_rank_colors = [PALETTE["indigo"], PALETTE["sky"], PALETTE["violet"], PALETTE["amber"], PALETTE["slate"]]
    for i, (lang, pct) in enumerate(lang_sorted):
        trend = None
        if lang in old_lang_map:
            diff = round(pct - old_lang_map[lang], 1)
            trend = diff
        languages.append({
            "name": lang,
            "percentage": pct,
            "repos": len(lang_repos[lang]),
            "color": tech_rank_colors[i % len(tech_rank_colors)],
            "trend": trend,
        })

    complexity_buckets = {"Small": 0, "Medium": 0, "Large": 0}
    for rd in repo_details:
        s = 0
        if rd["has_package"]: s += 1
        if rd["has_tests"]: s += 1
        if rd["has_docker"]: s += 1
        if rd["has_cicd"]: s += 1
        if rd["num_langs"] >= 2: s += 1
        if s <= 1: complexity_buckets["Small"] += 1
        elif s <= 3: complexity_buckets["Medium"] += 1
        else: complexity_buckets["Large"] += 1

    complexity = []
    for label in ["Small", "Medium", "Large"]:
        count = complexity_buckets[label]
        pct = round((count / total_repos) * 100, 0) if total_repos > 0 else 0
        complexity.append({
            "label": label, "percentage": pct, "count": count,
            "color": COMPLEXITY_COLORS[label],
        })

    all_detected = defaultdict(int)

    for rd in repo_details:
        if not rd["langs"]:
            continue
        primary = rd["langs"][0]
        topics_lower = [t.lower() for t in rd["topics"]]
        cn = rd["content_names"]
        detected_this = set()

        for t in topics_lower:
            if t in FRAMEWORK_MAP:
                detected_this.add(FRAMEWORK_MAP[t])
            if t in INFRA_MAP:
                detected_this.add(INFRA_MAP[t])
            if t in DATABASE_MAP:
                detected_this.add(DATABASE_MAP[t])

        for fn, tech in CONTENTS_FRAMEWORK.items():
            if fn in cn:
                detected_this.add(tech)

        for fn, tech in CONTENTS_INFRA.items():
            if fn == ".github":
                if any(c == ".github" for c in cn):
                    detected_this.add(tech)
            elif fn in cn:
                detected_this.add(tech)

        if "package.json" in cn and primary in ("JavaScript", "TypeScript"):
            detected_this.add("Node.js")
        for fn in cn:
            fnl = fn.lower()
            if (fnl.endswith(".jsx") or fnl.endswith(".tsx")) and primary in ("JavaScript", "TypeScript"):
                detected_this.add("React")
                break

        for fn in cn:
            fnl = fn.lower()
            if "postgres" in fnl or "psql" in fnl:
                detected_this.add("PostgreSQL")
                break
        for fn in cn:
            fnl = fn.lower()
            if "mongo" in fnl:
                detected_this.add("MongoDB")
                break

        for tech in detected_this:
            all_detected[tech] += rd["weight"]

    total_weight = sum(rd["weight"] for rd in repo_details)
    all_candidates = []
    for lang, pct in lang_pct.items():
        byte_score = pct / 100
        repo_score = len(lang_repos[lang]) / max_repo_count if max_repo_count > 0 else 0
        recency_score = _recency(lang_last_push[lang], now)
        score = byte_score * 0.4 + repo_score * 0.3 + recency_score * 0.3
        all_candidates.append((lang, score, "language"))

    max_detected = max(all_detected.values()) if all_detected else 1
    for tech, count in all_detected.items():
        score = (count / max_detected) * 0.8 + 0.2
        all_candidates.append((tech, score, "detected"))

    all_candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = all_candidates[:6]

    technologies = []
    for name, score, source in top_candidates:
        if source == "detected":
            pct = round((all_detected.get(name, 0) / total_weight) * 100, 0) if total_weight > 0 else 0
        else:
            pct = lang_pct.get(name, 0)
        technologies.append({
            "name": name,
            "percentage": pct,
            "score": round(score, 3),
            "level": _level(pct, score),
            "level_color": LEVEL_COLORS[_level(pct, score)],
        })

    all_commit_dates = []
    for dates in (fetched_commit_dates or {}).values():
        all_commit_dates.extend(dates)

    profile = _profile_metrics(all_commit_dates, fetched_commit_stats, lang_pct, now)
    profile["languages_count"] = len(lang_pct)
    profile["repos_count"] = total_repos

    monthly = defaultdict(int)
    for ts in all_commit_dates:
        dt = _parse_ts(ts) + IST_OFFSET
        monthly[(dt.year, dt.month)] += 1

    activity_out = []
    anchor = now + IST_OFFSET
    for i in range(11, -1, -1):
        idx = anchor.month - i
        year = anchor.year + ((idx - 1) // 12)
        month = ((idx - 1) % 12) + 1
        activity_out.append({
            "month": datetime(year, month, 1).strftime("%b"),
            "commit": monthly.get((year, month), 0),
        })
    max_act = max([a["commit"] for a in activity_out], default=1)
    for a in activity_out:
        a["pct"] = round((a["commit"] / max_act) * 100) if max_act else 0

    return {
        "generated": now.strftime("%b %Y"),
        "generated_iso": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "languages": languages[:6],
        "technologies": technologies,
        "complexity": complexity,
        "profile": profile,
        "activity": activity_out,
    }