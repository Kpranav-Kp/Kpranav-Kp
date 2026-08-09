def _shade(hex_c, f):
    r = int(hex_c[1:3], 16)
    g = int(hex_c[3:5], 16)
    b = int(hex_c[5:7], 16)
    r = max(0, min(255, round(r * f)))
    g = max(0, min(255, round(g * f)))
    b = max(0, min(255, round(b * f)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _city_geometry(activity):
    A, S = 0.866, 0.5
    u = 1.3
    spacing = 2.05
    n = len(activity)
    RAMP = ["#3F4D6B", "#5B6C99", "#6F83C8", "#6366F1", "#38BDF8", "#34D399"]

    towers = []
    start = -(n - 1) * spacing / 2
    for i, r in enumerate(activity):
        pct = r.get("pct") or 0
        level = max(1, round((max(pct, 1) / 100) * 5))
        towers.append({
            "cx": start + i * spacing,
            "level": level,
            "commit": r.get("commit", 0),
        })

    scaler = 60

    def P(cx, cy, cz):
        return (cx - cz) * A * scaler, (cx + cz) * S * scaler - cy * scaler

    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    for tw in towers:
        cx = tw["cx"]
        top = tw["level"] * u
        for p in P(cx, top, 0.0), P(cx + u, top, 0.0), P(cx + u, top, u), P(cx, top, u):
            minx, maxx = min(minx, p[0]), max(maxx, p[0])
            miny, maxy = min(miny, p[1]), max(maxy, p[1])
        for dz in (0.0, u):
            for p in P(cx, 0, dz), P(cx + u, 0, dz), P(cx + u, top, dz), P(cx, top, dz):
                minx, maxx = min(minx, p[0]), max(maxx, p[0])
                miny, maxy = min(miny, p[1]), max(maxy, p[1])

    pad = 26
    W = maxx - minx + 2 * pad
    H = maxy - miny + 2 * pad
    ox = -minx + pad
    oy = -miny + pad

    def v(pt):
        return f"{pt[0] + ox:.1f},{pt[1] + oy:.1f}"

    towers_out = []
    for idx, tw in enumerate(towers):
        cx = tw["cx"]
        top = tw["level"] * u
        mcx, mcy = P(cx + u / 2, top, u / 2)
        tower_polys = []
        for k in range(tw["level"]):
            y0 = k * u
            y1 = y0 + u
            front = RAMP[min(k, len(RAMP) - 1)]
            tower_polys.append(f'<polygon class="cube" points="{v(P(cx, y1, 0.0))} {v(P(cx + u, y1, 0.0))} {v(P(cx + u, y1, u))} {v(P(cx, y1, u))}" fill="{_shade(front, 1.0)}"/>')
            tower_polys.append(f'<polygon class="cube" points="{v(P(cx + u, y0, 0.0))} {v(P(cx + u, y1, 0.0))} {v(P(cx + u, y1, u))} {v(P(cx + u, y0, u))}" fill="{_shade(front, 0.82)}"/>')
            tower_polys.append(f'<polygon class="cube" points="{v(P(cx, y0, u))} {v(P(cx, y1, u))} {v(P(cx + u, y1, u))} {v(P(cx + u, y0, u))}" fill="{_shade(front, 0.62)}"/>')
        towers[idx]["polys"] = "".join(tower_polys)
        towers[idx]["tx"] = mcx + ox
        towers[idx]["ty"] = mcy + oy

    return towers, W, H


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

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 620" width="100%" height="100%">
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
          border-radius: 20px 20px 0 0; padding: 24px;
          box-shadow: var(--shadow);
          width: 100%; min-height: 100%; color: var(--text);
          position: relative;
          display: flex; flex-direction: column;
          animation: cardGlow 5s ease-in-out infinite;
        }}
        .card::after {{
          content: "";
          position: absolute; inset: -2px; border-radius: 22px;
          background: conic-gradient(from 0deg, var(--accent), var(--sky), var(--green), var(--rose), var(--accent));
          z-index: -1;
          opacity: 0.18;
          animation: ringPulse 5s ease-in-out infinite;
        }}
        h1 {{
          font-size: 20px; font-weight: 700; text-align: center; letter-spacing: -0.3px;
          margin-bottom: 16px; color: var(--text);
        }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
        .sc {{
          background: var(--surface); border: 1px solid var(--bl); border-radius: 14px; padding: 16px;
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
        .ml {{ display: flex; justify-content: space-between; margin-top: 4px; }}
        .am {{ font-size: 9px; font-weight: 600; color: var(--muted); width: 8.33%; text-align: center; }}
        .footer {{
          display: flex; justify-content: space-between; align-items: center; margin-top: 18px; padding-top: 12px;
          border-top: 1px solid var(--bl); font-size: 10px; color: var(--muted);
          margin-top: auto;
        }}
        @keyframes grow {{ from {{ width: 0%; }} }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideRow {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: translateX(0); }} }}
        @keyframes ringPulse {{ 0%, 100% {{ opacity: 0.12; }} 50% {{ opacity: 0.28; }} }}
        @keyframes cardGlow {{
          0%, 100% {{ box-shadow: 0 0 18px 0 rgba(99,102,241,0.10), var(--shadow); }}
          50% {{ box-shadow: 0 0 30px 2px rgba(14,165,233,0.18), var(--shadow); }}
        }}
        .sv {{ color: var(--text); }}
        @media (max-width: 500px) {{
          .grid {{ grid-template-columns: 1fr; }}
          .sf {{ grid-column: span 1; }}
          .tg {{ grid-template-columns: repeat(2, 1fr); }}
          .grid2 {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        @media (prefers-reduced-motion: reduce) {{
          * {{ animation: none !important; box-shadow: none !important; }}
          .card::after {{ opacity: 0.15; }}
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
      </div>
      <div class="footer">
        <span>Updated {generated}</span>
        <span>GitHub Actions \u00b7 profile-analytics</span>
      </div>
    </div>
  </foreignObject>
</svg>'''


def render_city(activity):
    if not activity:
        return ""
    towers, w, ch = _city_geometry(activity)

    n = len(activity)
    R = 20
    header = 78
    H = header + ch + 40

    path = (
        f"M0,0 L{w:.1f},0 L{w:.1f},{H - R:.1f} Q{w:.1f},{H:.1f} {w - R:.1f},{H:.1f} "
        f"L{R:.1f},{H:.1f} Q0,{H:.1f} 0,{H - R:.1f} Z"
    )

    tower_html = []
    for i, tw in enumerate(towers):
        delay = round(i * 0.18, 2)
        tx = tw["tx"]
        ty = tw["ty"]
        commit = tw.get("commit", 0)
        tower_html.append(
            f'<g class="tw" style="animation-delay:{delay}s" transform="translate(0 {header})">'
            f'{tw["polys"]}'
            f'<text class="lbl" x="{tx:.1f}" y="{ty - 20:.1f}" text-anchor="middle">{commit}</text>'
            f'</g>'
        )

    labels = ""
    for i, r in enumerate(activity):
        cx = (i + 0.5) * (w / n)
        labels += (
            f'<text x="{cx:.1f}" y="{header + ch + 20:.1f}" font-size="13" fill="#7485A0" '
            f'text-anchor="middle" font-family="Inter, Arial, sans-serif">{r["month"]}</text>'
        )

    defs = (
        f'<linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#0B1220"/><stop offset="1" stop-color="#0F1B2D"/>'
        f'</linearGradient>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {H:.1f}" width="100%" height="auto" preserveAspectRatio="xMidYMin meet">
  <defs>
    {defs}
  </defs>
  <style>
    .cube {{ opacity: 1; }}
    .tw {{ transform-box: fill-box; transform-origin: 50% 100%; }}
    .tw .cube {{ animation: cubeFloat 3.2s ease-in-out infinite; animation-delay: inherit; }}
    .tw .lbl {{ font-size: 15px; font-weight: 700; fill: #E2E8F0; font-family: Inter, Arial, sans-serif; opacity: 0; animation: lblIn 0.6s ease-out forwards; }}
    @keyframes cubeFloat {{
      0%, 100% {{ transform: translateY(0); filter: drop-shadow(0 0 6px rgba(99,102,241,0.55)); }}
      50% {{ transform: translateY(-7px); filter: drop-shadow(0 0 18px rgba(56,189,248,0.9)); }}
    }}
    @keyframes lblIn {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .cube {{ animation: none !important; filter: none !important; }} .lbl {{ animation: none !important; opacity: 1; }} }}
  </style>
  <path d="{path}" fill="url(#cbg)" stroke="rgba(255,255,255,0.07)" stroke-width="1.5"/>
  <text x="{w / 2:.1f}" y="{30}" text-anchor="middle" font-size="24" font-weight="700" fill="#F1F5F9" font-family="Inter, Arial, sans-serif">Monthly Commit Activity</text>
  <g>
    {"".join(tower_html)}
  </g>
  {labels}
</svg>'''