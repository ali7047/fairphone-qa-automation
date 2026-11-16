#!/usr/bin/env bash
# Publish an Allure report to the gh-pages branch, which GitHub Pages serves as a website.
#
#   publish_report.sh <report-dir> <workflow-key> <run-number>
#
# Result: <PAGES_URL>/<workflow-key>/<run-number>/  (one folder per run, so every
# run's link keeps showing that run's report), plus <workflow-key>/latest/ and an
# index page listing all runs.
#
# Environment:
#   REMOTE_URL  git address to push to, with credentials (the workflow's token)
#   PAGES_URL   base address of the GitHub Pages site
#   KEEP_RUNS   reports kept per workflow (default 20); older ones are removed
#
# The branch is replaced by a single new commit each time: old reports are not kept
# in git history, so the repository does not grow with every run.
set -euo pipefail

report_dir=$1
key=$2
run=$3
keep=${KEEP_RUNS:-20}
here=$(cd "$(dirname "$0")" && pwd)
site=$(mktemp -d)

# 1. Start from what is published now (if anything).
if git ls-remote --exit-code --heads "$REMOTE_URL" gh-pages >/dev/null 2>&1; then
  git clone --quiet --depth 1 --branch gh-pages "$REMOTE_URL" "$site"
  rm -rf "$site/.git"
fi

# 2. Add this run's report.
rm -rf "${site:?}/$key/$run"
mkdir -p "$site/$key/$run"
cp -R "$report_dir"/. "$site/$key/$run"/

# 3. Keep only the newest runs.
find "$site/$key" -mindepth 1 -maxdepth 1 -type d -regex '.*/[0-9]+' -printf '%f\n' \
  | sort -n | head -n -"$keep" \
  | while read -r old; do rm -rf "${site:?}/$key/$old"; done

# 4. "latest" points to this run and keeps its history (for trend charts in the
#    next run); the index lists every run.
rm -rf "$site/$key/latest"
mkdir -p "$site/$key/latest"
cp -R "$report_dir/history" "$site/$key/latest/history" 2>/dev/null || true
cat > "$site/$key/latest/index.html" <<EOF
<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../$run/">
<title>Latest report</title><a href="../$run/">Latest report: run $run</a>
EOF
python3 "$here/report_site.py" index "$site"
touch "$site/.nojekyll"   # serve files as they are (no Jekyll processing)

# 5. Publish as one fresh commit.
git -C "$site" init --quiet -b gh-pages
git -C "$site" add -A
git -C "$site" \
  -c user.name="github-actions[bot]" \
  -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
  commit --quiet -m "Test reports: $key #$run"
git -C "$site" push --quiet --force "$REMOTE_URL" gh-pages

url="${PAGES_URL%/}/$key/$run/"
echo "Published: $url"
if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "url=$url" >> "$GITHUB_OUTPUT"
fi
