"""Syntax and critical-control smoke checks for static community intake pages."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

class ScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.active = not dict(attrs).get("src")
            if self.active:
                self.scripts.append("")
    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False
    def handle_data(self, data):
        if self.active:
            self.scripts[-1] += data

for filename, required in {
    "community-map.html": ["osm-point-canvas.js","loadExactPoints",
      "flock_public_osm_exact_render_snapshot", "flock_osm_community_points",
      "Each pink dot is an actual OpenStreetMap-reported coordinate",
      "officialCount"],
    "submit.html": ["withdraw_own_community_report", "sanitizePhoto", "flock_community_submissions"],
    "community-review.html": ["list_community_review_queue", "set_community_review_status", "community_report_attachment_paths"],
    "accountability.html": ["flock_accountability_directory", "flock_accountability_roles", "safeCsvValue"],
    "analytics.html": ["flock_analytics_overview", "flock_analytics_states", "flock_analytics_monthly_evidence"],
}.items():
    doc = (ROOT / filename).read_text(encoding="utf-8")
    for marker in required:
        assert marker in doc, (filename, "missing", marker)
    if filename == "accountability.html":
        # A previous truncated inline edit silently appended an entire second
        # page after </html>. JS parsing alone did not catch the resulting
        # anonymous text node and 1466px horizontal mobile overflow.
        assert doc.rstrip().endswith("</body></html>"), (
            filename, "unexpected trailing content after final document")
        assert doc.count("</body></html>") == 1, (
            filename, "duplicate document footer / stray raw text")
    parser = ScriptParser()
    parser.feed(doc)
    assert parser.scripts, filename
    for script in parser.scripts:
        check = subprocess.run(["node", "--check"], input=script, text=True, capture_output=True)
        assert check.returncode == 0, (filename, check.stderr)
    print("Community page JavaScript parsed:", filename)
