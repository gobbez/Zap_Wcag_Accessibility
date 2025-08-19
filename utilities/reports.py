from datetime import datetime
from typing import List, Dict, Any, Tuple
import webbrowser

# Weights for impact
IMPACT_WEIGHTS = {
    "minor": 1,
    "moderate": 2,
    "serious": 4,
    "critical": 8,
}

# Maximum penalty per page (to prevent a single page from skewing results too much)
MAX_PENALTY_PER_PAGE = 100


def page_penalty_from_violations(violations: List[Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
    """Returns (capped_penalty, breakdown)"""
    penalty = 0
    breakdown = {
        "by_impact": {k: 0 for k in IMPACT_WEIGHTS.keys()},
        "violations": [],
    }
    for v in violations:
        impact = (v.get("impact") or "minor").lower()
        weight = IMPACT_WEIGHTS.get(impact, 1)
        nodes = v.get("nodes", [])
        count = max(1, len(nodes))
        penalty += weight * count
        breakdown["by_impact"][impact] = breakdown["by_impact"].get(impact, 0) + count
        breakdown["violations"].append({
            "id": v.get("id"),
            "impact": impact,
            "description": v.get("description"),
            "help": v.get("help"),
            "helpUrl": v.get("helpUrl"),
            "nodes_count": count,
            "tags": v.get("tags", []),
        })
    penalty_capped = min(MAX_PENALTY_PER_PAGE, penalty)
    return penalty_capped, breakdown


def make_reports(pages_results: List[Dict[str, Any]], out_prefix: str = "accessibility_report") -> str:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = f"{out_prefix}_{now}.html"

    # Score calculation
    per_page = []
    for r in pages_results:
        if not r.get("ok"):
            per_page.append({
                "url": r["url"],
                "ok": False,
                "error": r.get("error")
            })
        else:
            violations = r["results"].get("violations", [])
            penalty, breakdown = page_penalty_from_violations(violations)
            score = max(0, 100 - penalty)
            per_page.append({
                "url": r["url"],
                "ok": True,
                "score": score,
                "penalty": penalty,
                "violations_total": len(violations),
                "breakdown": breakdown,
            })

    valid_scores = [p["score"] for p in per_page if p.get("ok")]
    overall_score = int(round(sum(valid_scores) / len(valid_scores))) if valid_scores else 0

    # Build HTML
    html_lines = []
    html_lines.append("<!DOCTYPE html>")
    html_lines.append("<html lang='en'>")
    html_lines.append("<head>")
    html_lines.append("<meta charset='UTF-8'>")
    html_lines.append("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html_lines.append("<title>Accessibility Report</title>")
    html_lines.append("<style>")
    html_lines.append("body { font-family: Arial, sans-serif; margin: 20px; }")
    html_lines.append("h1, h2, h3 { color: #2c3e50; }")
    html_lines.append(".score { font-weight: bold; }")
    html_lines.append(".critical { color: red; } .serious { color: darkorange; } .moderate { color: goldenrod; } .minor { color: gray; }")
    html_lines.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
    html_lines.append("th, td { border: 1px solid #ccc; padding: 6px 10px; }")
    html_lines.append("th { background: #f5f5f5; }")
    html_lines.append("</style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    html_lines.append(f"<h1>Accessibility Report (axe + Selenium)</h1>")
    html_lines.append(f"<p><b>Generated:</b> {datetime.now().isoformat(timespec='seconds')}</p>")
    html_lines.append(f"<p><b>Overall score (0-100):</b> <span class='score'>{overall_score}</span></p>")

    for p in per_page:
        html_lines.append(f"<h2>{p['url']}</h2>")
        if not p.get("ok"):
            html_lines.append(f"<p><b>Status:</b> ERROR</p>")
            html_lines.append(f"<p><b>Details:</b> {p.get('error')}</p>")
            continue

        html_lines.append(f"<p><b>Page score:</b> <span class='score'>{p['score']}</span> (penalty: {p['penalty']}, violations: {p['violations_total']})</p>")

        bi = p["breakdown"]["by_impact"]
        html_lines.append("<p><b>Violations by impact:</b> " + ", ".join(f"{k}: {v}" for k, v in bi.items()) + "</p>")

        html_lines.append("<h3>Key Violations</h3>")
        html_lines.append("<table>")
        html_lines.append("<tr><th>ID</th><th>Impact</th><th>Description</th><th>Guide</th><th>Occurrences</th></tr>")

        for v in sorted(
            p["breakdown"]["violations"],
            key=lambda x: (IMPACT_WEIGHTS.get(x["impact"], 1) * -1, x["nodes_count"] * -1)
        )[:10]:
            html_lines.append("<tr>")
            html_lines.append(f"<td>{v['id']}</td>")
            html_lines.append(f"<td class='{v['impact']}'>{v['impact']}</td>")
            html_lines.append(f"<td>{v.get('help') or v.get('description')}</td>")
            if v.get("helpUrl"):
                html_lines.append(f"<td><a href='{v['helpUrl']}' target='_blank'>Guide</a></td>")
            else:
                html_lines.append("<td>-</td>")
            html_lines.append(f"<td>{v['nodes_count']}</td>")
            html_lines.append("</tr>")

        html_lines.append("</table>")

    html_lines.append("</body></html>")

    # Save HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))

    # Open in default browser
    webbrowser.open_new_tab(html_path)

    return html_path
