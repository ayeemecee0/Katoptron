import importlib.util
from pathlib import Path
import unittest
SFILE=Path(__file__).with_name("watch_sacramento_county_original_sources.py")
spec=importlib.util.spec_from_file_location("sac_official",SFILE)
M=importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

class SacramentoOfficialWatch(unittest.TestCase):
    def test_pinned_sources_are_official_and_bounded(self):
        self.assertEqual(len(M.PAGES),3)
        self.assertTrue(all(M.approved(p) for p in M.PAGES))
        for bad in (
          "http://sccob.saccounty.gov/us/en/board-of-supervisors-public-meetings.html",
          "https://sccob.saccounty.gov.evil.test/a",
          "https://sccob.saccounty.gov/../other",
          "https://agendanet.saccounty.gov/?token=password",
          "https://evil.test/ALPR"
        ):
            if "token=" in bad:
                self.assertFalse(M.find_links(M.PAGES[0],
                     '<a href="'+bad+'">Flock Safety</a>'))
            else:self.assertFalse(M.approved(bad))
    def test_explicit_visible_label_and_exact_government_link_only(self):
        html=('''<html><a href="/records?id=44">Flock Safety agreement</a>
            <a href="/another">Meeting agenda</a>
            <a href="https://evil.test/contract">Flock Safety</a>
            <a href="/alpr.pdf">ALPR retention policy</a>
            <a href="/private?session=secret">Flock camera list</a></html>''')
        links=M.find_links(M.PAGES[0],html)
        self.assertEqual(len(links),2)
        self.assertTrue(all(x["status"]=="unreviewed" and x["state_hint"]=="CA"
                            for x in links))
        self.assertTrue(all("NOT" not in x["headline"] for x in links))
    def test_generic_agenda_label_with_explicit_named_document_path_is_private_lead(self):
        page=M.PAGES[0]
        html=('''<a href="/records/Flock_Safety_2026_Contract.pdf">Download agenda packet</a>
                   <a href="/records/general-budget.pdf">Download agenda packet</a>
                   <a href="/private/vehicle-search-logs">Search logs</a>
                   <a href="https://evil.example/Flock_Safety_2026.pdf">Download</a>''')
        rows=M.find_links(page,html)
        self.assertEqual(len(rows),1)
        self.assertIn("Flock_Safety_2026",rows[0]["url"])
        self.assertEqual(rows[0]["status"],"unreviewed")
        self.assertIn("UNREVIEWED",rows[0]["snippet"])

    def test_no_alert_generation_for_new_official_document_links(self):
        html='<a href="/Flock-contract.pdf">Flock contract</a>'
        report=M.discover(fetch=lambda _:html)
        self.assertEqual(report["source_pages_held"],0)
        self.assertEqual(report["unreviewed_explicit_source_links"],2)  # same relative path on two distinct official publisher hosts
        self.assertEqual(report["public_alert_events_created"],0)
        self.assertEqual(report["new_contracts_verified"],0)
        self.assertEqual(report["camera_locations_published"],0)
        self.assertEqual(report["sources"][0]["status"],"scanned")
        self.assertEqual(len(report["sources"][0]["source_sha256"]),64)
    def test_partial_fetch_failures_are_reported_not_hidden(self):
        def fetch(page):
            if page==M.PAGES[0]:raise ValueError("Unavailable")
            return '<a href="/ALPR">License plate reader policy</a>'
        report=M.discover(fetch=fetch)
        self.assertEqual(report["source_pages_held"],1)
        self.assertEqual(report["public_alert_events_created"],0)

if __name__=="__main__":unittest.main()
