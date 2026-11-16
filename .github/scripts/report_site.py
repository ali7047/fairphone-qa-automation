"""Helpers for the Allure report job in GitHub Actions. Standard library only.

    python report_site.py metadata <allure-results>  executor and environment shown in the report
    python report_site.py summary  <allure-results>  results table for the run page (Markdown on stdout)
    python report_site.py index    <site-dir>        index.html listing every published report

Values come from environment variables set by the workflow (see smoke.yml).
"""

from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# --- metadata: shown on the report's Overview page ---------------------------------


def write_metadata(results: Path) -> None:
    results.mkdir(parents=True, exist_ok=True)
    executor = {
        "name": "GitHub Actions",
        "type": "github",
        "url": env("RUN_URL").rsplit("/runs/", 1)[0],
        "buildOrder": int(env("RUN_NUMBER", "0")),
        "buildName": f"{env('WORKFLOW_NAME')} #{env('RUN_NUMBER')} ({env('BRANCH')})",
        "buildUrl": env("RUN_URL"),
        "reportUrl": env("REPORT_URL"),
        "reportName": "Fairphone shop tests",
    }
    (results / "executor.json").write_text(json.dumps(executor, indent=2), encoding="utf-8")

    environment = {
        "Shop": env("REGION", "eu").upper(),
        "Language": env("SHOP_LANGUAGE", "en"),
        "Address": env("BASE_URL") or "live shop of the region",
        "Browser": env("BROWSER", "chromium"),
        "Branch": env("BRANCH"),
        "Commit": env("COMMIT_SHA")[:7],
    }
    lines = [f"{key}={value}" for key, value in environment.items()]
    (results / "environment.properties").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- summary: the table at the top of the workflow run page ------------------------

ICONS = {"passed": "✅", "failed": "❌", "broken": "⚠️", "skipped": "⏭️"}


def print_summary(results: Path) -> None:
    if env("PUBLISHED") == "true":
        print(f"## 📊 [Open the Allure report]({env('REPORT_URL')})\n")
        if env("REPORT_LIVE") != "true":
            print(
                "> [!NOTE]\n> GitHub Pages was still building when this job ended: if the link shows 404,"
                " wait a minute and try again.\n"
            )
    else:
        print(
            "> [!WARNING]\n> The report could not be published to GitHub Pages (see the *Publish* step)."
            " Download the **allure-report** artifact below instead.\n"
        )

    print(
        f"**{env('WORKFLOW_NAME')} #{env('RUN_NUMBER')}** · branch `{env('BRANCH')}`"
        f" · shop {env('REGION', 'eu').upper()} · language {env('SHOP_LANGUAGE', 'en')}"
        f" · {env('BROWSER', 'chromium')}\n"
    )
    rows = []
    for file in sorted(results.glob("*-result.json")):
        result = json.loads(file.read_text(encoding="utf-8"))
        labels = {label["name"]: label["value"] for label in result.get("labels", [])}
        message = ((result.get("statusDetails") or {}).get("message") or "").strip().splitlines()
        rows.append((labels.get("feature", ""), result["name"], result["status"], message[0][:140] if message else ""))
    print("| Suite | Test | Result | Why it failed |")
    print("|---|---|---|---|")
    for suite, name, status, why in sorted(rows):
        print(f"| {suite} | `{name}` | {ICONS.get(status, '')} {status} | {why.replace('|', '/')} |")
    print(
        "\n*Known issues* are expected to fail until the shop fixes them; they never block a pull request."
        "\nThe same report is also attached to this run as the **allure-report** artifact."
    )


# --- index: the page at the root of the GitHub Pages site --------------------------


def write_index(site: Path) -> None:
    runs = []
    for executors_file in site.glob("*/*/widgets/executors.json"):
        report_dir = executors_file.parent.parent
        if not report_dir.name.isdigit():
            continue
        executor = (json.loads(executors_file.read_text(encoding="utf-8")) or [{}])[0]
        summary_file = report_dir / "widgets" / "summary.json"
        summary = json.loads(summary_file.read_text(encoding="utf-8")) if summary_file.exists() else {}
        runs.append(
            {
                "workflow": report_dir.parent.name,
                "number": int(report_dir.name),
                "name": executor.get("buildName", ""),
                "run_url": executor.get("buildUrl", ""),
                "report": f"{report_dir.parent.name}/{report_dir.name}/",
                "stats": summary.get("statistic", {}),
            }
        )
    runs.sort(key=lambda run: (run["workflow"], -run["number"]))

    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(run['workflow'])}</td>"
        f'<td><a href="{html.escape(run["report"])}">{html.escape(run["name"] or str(run["number"]))}</a></td>'
        f"<td>✅ {run['stats'].get('passed', 0)} &nbsp; ❌ {run['stats'].get('failed', 0)}"
        f" &nbsp; ⚠️ {run['stats'].get('broken', 0)}</td>"
        f'<td><a href="{html.escape(run["run_url"])}">workflow run</a></td>'
        "</tr>"
        for run in runs
    )
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Fairphone shop test reports</title>
<style>body{{font-family:system-ui,sans-serif;margin:2rem;color:#1d3b2f}}table{{border-collapse:collapse}}
td,th{{padding:.4rem .8rem;border-bottom:1px solid #ddd;text-align:left}}</style></head>
<body><h1>Fairphone shop test reports</h1>
<p>One Allure report per workflow run (newest first). Older runs are removed automatically.</p>
<table><tr><th>Workflow</th><th>Report</th><th>Results</th><th>Run</th></tr>
{rows or '<tr><td colspan="4">No reports yet.</td></tr>'}
</table></body></html>
"""
    (site / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # the summary uses emoji; Windows consoles default to cp1252
    command, folder = sys.argv[1], Path(sys.argv[2])
    {"metadata": write_metadata, "summary": print_summary, "index": write_index}[command](folder)
