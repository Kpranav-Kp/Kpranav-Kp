def render_svg(data):
    techs = data.get("technologies", [])
    complexity = data.get("complexity", [])
    activity = data.get("activity", [])
    profile = data.get("profile", {})
    generated = data.get("generated", "")

    def fmt(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    def big_num(v):
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 1_000:
            return f"{v / 1_000:.1f}k"
        return f"{v:,}"

    tech_cards = []
    for i, t in enumerate(techs):
        d = round(0.1 + i * 0.08, 2)
        tech_cards.append(f"""
    <div class="tc" style="animation: fadeIn 0.5s ease-out {d}s both;">
      <div class="tca" style="background:{t['level_color']}"></div>
      <span class="tcn">{t['name']}</span>
      <span class="tcl" style="color:{t['level_color']}">{t['level']}</span>
      <div class="tcb"><div class="bar" style="width:{t['percentage']}%;background:{t['level_color']};animation-delay:{fmt(d + 0.3)}s"></div></div>
    </div>""")

    comp_rows = []
    for i, c in enumerate(complexity):
        d = round(0.15 + i * 0.15, 2)
        comp_rows.append(f"""
    <div class="row" style="animation: slideRow 0.5s ease-out {d}s both;">
      <span class="rl">{c['label']}</span>
      <div class="bt"><div class="bar" style="width:{c['percentage']}%;background:{c['color']};animation-delay:{fmt(d + 0.35)}s"></div></div>
      <span class="rv">{c['percentage']:.0f}%</span>
      <span class="rm">{c['count']} repo{"s" if c['count'] != 1 else ""}</span>
    </div>""")

    repos_count = max(profile.get("repos_count", 1), 1)
    added_total = profile.get("lines_added", 0)
    deleted_total = profile.get("lines_deleted", 0)

    stat_cards = ""
    cards = [
        ("Current streak", f"{profile.get('current_streak', 0)}", "days", "#34D399", ""),
        ("Longest streak", f"{profile.get('longest_streak', 0)}", "days", "#6366F1", profile.get("longest_range", "")),
        ("Lines added", big_num(added_total), "", "#34D399", f"~{big_num(round(added_total / repos_count))}/repo"),
        ("Lines deleted", big_num(deleted_total), "", "#F43F5E", f"~{big_num(round(deleted_total / repos_count))}/repo"),
        ("Commits / week", fmt(profile.get("commit_frequency", 0)), "", "#6366F1", f"{profile.get('total_commits')} lifetime"),
        ("Peak hours", profile.get("peak_hour", "-"), "", "#0EA5E9", profile.get("peak_day", "")),
    ]
    for i, (label, value, unit, color, sub) in enumerate(cards):
        d = round(0.15 + i * 0.06, 2)
        unit_html = f'<span class="su">{unit}</span>' if unit else ""
        sub_html = f'<span class="sd">{sub}</span>' if sub else ""
        stat_cards += f"""
    <div class="ss" style="animation: slideUp 0.5s ease-out {d}s both">
      <span class="sl">{label}</span>
      <span class="sv" style="color:{color}">{value}{unit_html}</span>
      {sub_html}
    </div>"""

    habits = profile.get("habits", [])
    habits_html = ""
    if habits:
        chip = ""
        for h in habits:
            chip += f'<span class="hb" style="color:{h["color"]};border-color:{h["color"]}55;background:{h["color"]}11">{h["label"]}</span>'
        habits_html = f'<div class="habits">{"".join(chip)}</div>'

    contrib_rows = ""
    if activity:
        for i, r in enumerate(activity):
            d = round(0.15 + i * 0.05, 2)
            is_max = r["pct"] >= 100
            glow = "box-shadow:0 0 12px rgba(14,165,233,0.55);" if is_max else ""
            contrib_rows += f"""
    <div class="ab" style="animation: slideUp 0.5s ease-out {d}s both">
      <span class="ac">{r['commit'] if r['commit'] else ""}</span>
      <div class="abar" style="height:{max(r['pct'], 2)}%">
        <div class="afill" style="animation-delay:{fmt(d + 0.25)}s;{glow}"></div>
      </div>
      <span class="am">{r['month']}</span>
    </div>"""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 940" width="100%" height="100%">
  <foreignObject width="100%" height="100%">
    <div xmlns="http://www.w3.org/1999/xhtml" class="card">
      <style>
        :root {{
          --bg1: #0B1220; --bg2: #0F1B2D;
          --surface: rgba(255,255,255,0.03);
          --border: rgba(255,255,255,0.07);
          --bl: rgba(255,255,255,0.05);
          --text: #F1F5F9; --muted: #7485A0;
          --bar-bg: rgba(255,255,255,0.06);
          --accent: #6366F1;
          --green: #34D399; --rose: #F43F5E; --sky: #0EA5E9;
          --shadow: 0 0 0 1px rgba(255,255,255,0.02), 0 8px 32px rgba(0,0,0,0.55);
        }}
        @media (prefers-color-scheme: light) {{
          :root {{
            --bg1: #FFFFFF; --bg2: #F3F5F9;
            --surface: rgba(17,24,39,0.02);
            --border: rgba(17,24,39,0.07);
            --bl: rgba(17,24,39,0.05);
            --text: #0F172A; --muted: #64748B;
            --bar-bg: rgba(17,24,39,0.05);
            --shadow: 0 0 0 1px rgba(17,24,39,0.03), 0 8px 32px rgba(15,23,42,0.08);
          }}
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        .card {{
          font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
          background: linear-gradient(160deg, var(--bg1), var(--bg2));
          border: 1px solid var(--border);
          border-radius: 20px; padding: 28px;
          box-shadow: var(--shadow);
          width: 100%; min-height: 100%; color: var(--text);
        }}
        h1 {{
          font-size: 20px; font-weight: 700; text-align: center; letter-spacing: -0.3px;
          margin-bottom: 24px;
          background: linear-gradient(90deg, var(--text), var(--accent), var(--sky), var(--text));
          background-size: 300% 100%;
          -webkit-background-clip: text; background-clip: text;
          -webkit-text-fill-color: transparent; color: transparent;
          animation: sheenTitle 8s ease-in-out infinite;
        }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
        .sc {{
          background: var(--surface); border: 1px solid var(--bl); border-radius: 14px; padding: 18px;
          animation: slideUp 0.5s ease-out both;
        }}
        .sc:nth-child(1) {{ animation-delay: 0.05s; }}
        .sc:nth-child(2) {{ animation-delay: 0.1s; }}
        .sc:nth-child(3) {{ animation-delay: 0.15s; }}
        .sf {{ grid-column: span 2; }}
        h2 {{ font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--muted); margin-bottom: 12px; }}
        .row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; min-height: 28px; }}
        .rl {{ width: 72px; font-size: 12px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 0; }}
        .bt {{ flex: 1; height: 6px; background: var(--bar-bg); border-radius: 3px; overflow: hidden; }}
        .bar {{ height: 100%; border-radius: 3px; animation: grow 0.9s cubic-bezier(0.16, 1, 0.3, 1) both; }}
        .rv {{ width: 34px; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; flex-shrink: 0; text-align: right; }}
        .rm {{ font-size: 10px; color: var(--muted); flex-shrink: 0; width: 48px; text-align: right; }}
        .tg {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .tc {{
          background: var(--bar-bg); border: 1px solid var(--bl); border-radius: 10px; padding: 14px 8px 10px;
          display: flex; flex-direction: column; align-items: center; gap: 3px; position: relative; overflow: hidden;
        }}
        .tca {{ position: absolute; top: 0; left: 0; right: 0; height: 2px; }}
        .tcn {{ font-size: 12px; font-weight: 600; margin-top: 2px; }}
        .tcl {{ font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; }}
        .tcb {{ width: 100%; height: 3px; background: var(--bar-bg); border-radius: 2px; overflow: hidden; margin-top: 3px; }}
        .grid2 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }}
        .ss {{
          display: flex; flex-direction: column; gap: 2px; padding: 10px 12px;
          border: 1px solid var(--bl); border-radius: 10px; background: var(--bar-bg);
        }}
        .sl {{ font-size: 8px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); }}
        .sv {{ font-size: 20px; font-weight: 800; letter-spacing: -0.6px; line-height: 1.15; }}
        .su {{ font-size: 9px; font-weight: 600; color: var(--muted); margin-left: 2px; }}
        .sd {{ font-size: 9px; font-weight: 500; color: var(--muted); margin-top: 1px; }}
        .habits {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }}
        .hb {{ font-size: 9px; font-weight: 600; padding: 3px 10px; border: 1px solid; border-radius: 999px; }}
        .act {{ display: grid; grid-template-columns: repeat(12, 1fr); gap: 6px; align-items: end; }}
        .ab {{ display: flex; flex-direction: column; align-items: center; gap: 3px; height: 92px; }}
        .ac {{ font-size: 9px; font-weight: 600; font-variant-numeric: tabular-nums; color: var(--muted); line-height: 1; }}
        .abar {{
          width: 60%; flex: 1; min-height: 2px; border-radius: 3px;
          background: var(--bar-bg); display: flex; align-items: flex-end;
          overflow: hidden; justify-content: center;
        }}
        .afill {{ width: 100%; height: 100%; border-radius: 3px; background: linear-gradient(180deg, var(--accent), var(--sky)); animation: fillBar 1s cubic-bezier(0.16, 1, 0.3, 1) both, slowPulse 3.4s ease-in-out 1.1s infinite; }}
        .am {{ font-size: 9px; font-weight: 600; color: var(--muted); }}
        .footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 18px; padding-top: 12px; border-top: 1px solid var(--bl); font-size: 10px; color: var(--muted); animation: fadeIn 0.6s ease-out 0.6s both; }}
        @keyframes grow {{ from {{ width: 0%; }} }}
        @keyframes fillBar {{ 0% {{ height: 0%; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideRow {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: translateX(0); }} }}
        @keyframes sheenTitle {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .sv {{ animation: slowPulse 2.6s ease-in-out infinite; }}
        @keyframes slowPulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.62; }} }}
        @media (max-width: 500px) {{
          .grid {{ grid-template-columns: 1fr; }}
          .sf {{ grid-column: span 1; }}
          .tg {{ grid-template-columns: repeat(2, 1fr); }}
          .grid2 {{ grid-template-columns: repeat(2, 1fr); }}
          .abar {{ width: 70%; }}
        }}
        @media (prefers-reduced-motion: reduce) {{
          * {{ animation: none !important; box-shadow: none !important; }}
        }}
      </style>
      <h1>Profile Analytics</h1>
      <div class="grid">
        <div class="sc sf">
          <h2>Core Technologies</h2>
          <div class="tg">{"".join(tech_cards)}</div>
        </div>
        <div class="sc">
          <h2>Project Complexity</h2>
          {"".join(comp_rows)}
        </div>
        <div class="sc">
          <h2>Profile</h2>
          <div class="grid2">{stat_cards}</div>
          {habits_html}
        </div>
        <div class="sc sf">
          <h2>Commit Activity \u00b7 Last 12 Months</h2>
          <div class="act">{contrib_rows}</div>
        </div>
      </div>
      <div style="height:20px"></div>
      <div class="footer">
        <span>Updated {generated}</span>
        <span>GitHub Actions \u00b7 profile-analytics</span>
      </div>
    </div>
  </foreignObject>
</svg>'''