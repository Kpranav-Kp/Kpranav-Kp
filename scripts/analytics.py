from datetime import datetime, timezone
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

TECH_COLORS = {
    "Python": "#3776AB", "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6", "Java": "#ED8B00",
    "C++": "#00599C", "Go": "#00ADD8",
    "Rust": "#000000", "C#": "#239120",
    "Ruby": "#CC342D", "PHP": "#777BB4",
    "Swift": "#FA7343", "Kotlin": "#7F52FF",
    "Dart": "#0175C2", "C": "#A8B9CC", "R": "#276DC3",
    "FastAPI": "#059669",     "Django": "#0C4B33",
    "Flask": "#000000", "React": "#61DAFB",
    "Node.js": "#339933", "Express": "#000000",
    "Next.js": "#000000", "Vue": "#4FC08D",
    "TensorFlow": "#FF6F00", "PyTorch": "#EE4C2C",
    "Spring": "#6DB33F",
    "PostgreSQL": "#336791", "MongoDB": "#47A248",
    "MySQL": "#4479A1", "Redis": "#DC382D", "SQLite": "#003B57",
    "Docker": "#2496ED", "Kubernetes": "#326CE5",
    "Vercel": "#000000", "GitHub Actions": "#2088FF",
    "AWS": "#FF9900", "GCP": "#4285F4", "Azure": "#0078D4",
    "Nginx": "#009639", "Celery": "#37814A", "Supabase": "#3ECF8E",
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
    "Advanced": "#10B981", "Intermediate": "#3B82F6",
    "Beginner": "#6B7280",
}


def _grade(score):
    if score >= 85: return ("S", "#FFD700")
    if score >= 70: return ("A+", "#10B981")
    if score >= 55: return ("A", "#3B82F6")
    if score >= 40: return ("B+", "#8B5CF6")
    if score >= 25: return ("B", "#F59E0B")
    if score >= 15: return ("C+", "#EC4899")
    return ("C", "#6B7280")


def compute(repos, fetched_topics, fetched_langs, fetched_contents, fetched_releases, fetched_commits=None, old_data=None):
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

        commit_count = (fetched_commits or {}).get(repo_key, 1)
        repo_weight = max(0.1, 1 - (now - pushed_at).days / 730)
        repo_details.append({
            "name": repo_name,
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
    for lang, pct in lang_sorted:
        trend = None
        if lang in old_lang_map:
            diff = round(pct - old_lang_map[lang], 1)
            trend = diff
        languages.append({
            "name": lang,
            "percentage": pct,
            "repos": len(lang_repos[lang]),
            "color": TECH_COLORS.get(lang, "#3B82F6"),
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

    comp_colors = {"Small": "#10B981", "Medium": "#F59E0B", "Large": "#EF4444"}
    complexity = []
    for label in ["Small", "Medium", "Large"]:
        count = complexity_buckets[label]
        pct = round((count / total_repos) * 100, 0) if total_repos > 0 else 0
        complexity.append({
            "label": label, "percentage": pct, "count": count, "color": comp_colors[label],
        })

    lang_framework = defaultdict(lambda: defaultdict(int))
    lang_infra = defaultdict(lambda: defaultdict(int))
    lang_db = defaultdict(lambda: defaultdict(int))
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
                lang_framework[primary][FRAMEWORK_MAP[t]] += 1
                detected_this.add(FRAMEWORK_MAP[t])
            if t in INFRA_MAP:
                lang_infra[primary][INFRA_MAP[t]] += 1
                detected_this.add(INFRA_MAP[t])
            if t in DATABASE_MAP:
                lang_db[primary][DATABASE_MAP[t]] += 1
                detected_this.add(DATABASE_MAP[t])

        for fn, tech in CONTENTS_FRAMEWORK.items():
            if fn in cn:
                lang_framework[primary][tech] += 1
                detected_this.add(tech)

        for fn, tech in CONTENTS_INFRA.items():
            if fn == ".github":
                if any(c == ".github" for c in cn):
                    lang_infra[primary][tech] += 1
                    detected_this.add(tech)
            elif fn in cn:
                lang_infra[primary][tech] += 1
                detected_this.add(tech)

        if "package.json" in cn and primary in ("JavaScript", "TypeScript"):
            lang_framework[primary]["Node.js"] += 1
            detected_this.add("Node.js")
        for fn in cn:
            fnl = fn.lower()
            if (fnl.endswith(".jsx") or fnl.endswith(".tsx")) and primary in ("JavaScript", "TypeScript"):
                lang_framework[primary]["React"] += 1
                detected_this.add("React")
                break

        for fn in cn:
            fnl = fn.lower()
            if "postgres" in fnl or "psql" in fnl:
                lang_db[primary]["PostgreSQL"] += 1
                detected_this.add("PostgreSQL")
                break
        for fn in cn:
            fnl = fn.lower()
            if "mongo" in fnl:
                lang_db[primary]["MongoDB"] += 1
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
            "color": TECH_COLORS.get(name, "#3B82F6"),
        })

    repo_activities = [rd["weight"] * 0.5 + min(rd["commit_count"] / 30, 1) * 0.5 for rd in repo_details]
    active_pct = round((sum(repo_activities) / len(repo_activities)) * 100, 0) if repo_activities else 0
    languages_count = len(lang_pct)
    max_years = round((max(all_ages_days) / 365.25), 1) if all_ages_days else 0

    depth_score = sum(1 for t in technologies if t["level"] == "Advanced") * 1.0 + sum(1 for t in technologies if t["level"] == "Intermediate") * 0.5
    depth_pct = min(round((depth_score / len(technologies)) * 100, 0), 100) if technologies else 0
    breadth_score = min(len(cat_counts) * 14 + len(lang_pct) * 6, 100)
    maturity_pct = min(round(max_years / 5 * 100, 0), 100)

    grades = [
        ("Overall", round((active_pct + depth_pct + breadth_score + maturity_pct) / 4, 0)),
        ("Activity", active_pct),
        ("Depth", depth_pct),
        ("Breadth", breadth_score),
    ]
    grades_data = []
    for label, score in grades:
        letter, color = _grade(score)
        grades_data.append({
            "label": label,
            "grade": letter,
            "score": int(score),
            "color": color,
        })

    profile = {
        "active_pct": int(active_pct),
        "languages_count": languages_count,
        "maturity": max_years,
        "grades": grades_data,
    }

    chain_counter = defaultdict(int)
    for rd in repo_details:
        if not rd["langs"]:
            continue
        lang = rd["langs"][0]
        topics_lower = [t.lower() for t in rd["topics"]]
        cn = rd["content_names"]

        fws = set()
        for t in topics_lower:
            if t in FRAMEWORK_MAP:
                fws.add(FRAMEWORK_MAP[t])
        for fn, tech in CONTENTS_FRAMEWORK.items():
            if fn in cn:
                fws.add(tech)
        if not fws and "package.json" in cn and lang in ("JavaScript", "TypeScript"):
            fws.add("Node.js")
        if lang in ("JavaScript", "TypeScript") and any(fn.lower().endswith(".jsx") or fn.lower().endswith(".tsx") for fn in cn):
            fws.add("React")

        infras = set()
        for t in topics_lower:
            if t in INFRA_MAP:
                infras.add(INFRA_MAP[t])
        for fn, tech in CONTENTS_INFRA.items():
            if fn in cn:
                infras.add(tech)

        dbs = set()
        for t in topics_lower:
            if t in DATABASE_MAP:
                dbs.add(DATABASE_MAP[t])
        for fn in cn:
            fnl = fn.lower()
            if "postgres" in fnl or "psql" in fnl:
                dbs.add("PostgreSQL")
            if "mongo" in fnl:
                dbs.add("MongoDB")
            if "redis" in fnl:
                dbs.add("Redis")

        chain = [lang] + sorted(fws) + sorted(infras) + sorted(dbs)

        if len(chain) > 1:
            chain_counter[tuple(chain)] += 1

    all_tech_set = set(FRAMEWORK_MAP.values()) | set(INFRA_MAP.values()) | set(DATABASE_MAP.values())
    network_chains = []
    for chain_tuple, _ in sorted(chain_counter.items(), key=lambda x: (x[1], len(x[0])), reverse=True)[:2]:
        cd = []
        for entry in chain_tuple:
            if entry in all_tech_set:
                tc = sum(rd_["weight"] for rd_ in repo_details if any(
                    (FRAMEWORK_MAP.get(t.lower()) == entry or
                     INFRA_MAP.get(t.lower()) == entry or
                     DATABASE_MAP.get(t.lower()) == entry) for t in rd_["topics"])
                    or (entry == "Docker" and "Dockerfile" in rd_["content_names"])
                    or (entry == "GitHub Actions" and ".github" in rd_["content_names"])
                    or (entry == "Node.js" and "package.json" in rd_["content_names"] and rd_["langs"] and rd_["langs"][0] in ("JavaScript", "TypeScript"))
                    or (entry == "PostgreSQL" and any("postgres" in f.lower() for f in rd_["content_names"]))
                    or (entry == "MongoDB" and any("mongo" in f.lower() for f in rd_["content_names"]))
                    or (entry == "Django" and "manage.py" in rd_["content_names"])
                    or (entry == "Next.js" and "next.config.js" in rd_["content_names"]))
                pct = round((tc / total_weight) * 100, 0) if total_weight > 0 else 0
            else:
                pct = lang_pct.get(entry, 0)
            cd.append({"name": entry, "pct": int(pct) if pct == int(pct) else pct, "color": TECH_COLORS.get(entry, "#3B82F6")})
        network_chains.append(cd)

    network = network_chains[:2]

    return {
        "generated": now.strftime("%b %Y"),
        "generated_iso": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "languages": languages[:5],
        "technologies": technologies,
        "complexity": complexity,
        "profile": profile,
        "network": network,
    }
