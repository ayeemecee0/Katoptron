"""Bounded negative test of current browser-visible Geoapify key restrictions.

Uses ONE fixed public US geocoding request and an intentionally foreign
Origin/Referer. Does not print provider key, URL, response body, or query.
An expected 403 is evidence of a rejection, not proof of billing quotas.
"""
from pathlib import Path
import re
import urllib.parse
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
KEY=re.compile(r"geoapifyPublicKey:\s*'([A-Za-z0-9_-]{20,160})'")
ORIGIN='https://not-katoptron.example.invalid'

def verify():
    config=(ROOT/'config.js').read_text(encoding='utf8')
    match=KEY.search(config)
    if not match:
        raise ValueError('Public Geoapify key not configured')
    url='https://api.geoapify.com/v1/geocode/search?'+urllib.parse.urlencode({
      'text':'Sacramento California','format':'json','limit':'1',
      'filter':'countrycode:us','apiKey':match.group(1)
    })
    request=urllib.request.Request(url,headers={
      'Origin':ORIGIN,'Referer':ORIGIN+'/',
      'User-Agent':'Mozilla/5.0 Katoptron-foreign-origin-negative-test',
      'Accept':'application/json'
    })
    try:
        with urllib.request.urlopen(request,timeout=15) as response:
            status=response.status
    except urllib.error.HTTPError as exc:
        status=exc.code
    except urllib.error.URLError:
        raise RuntimeError('Geoapify foreign-origin test unavailable')
    if status in (401,403):
        # Both 401 and 403 are provider authorization rejections. This
        # negative result must be paired with successful real hosted-origin
        # requests; it is NOT proof of dashboard quota/spending limits.
        print('GEOAPIFY FOREIGN-ORIGIN REQUEST REJECTED: HTTP '+str(status))
        return
    if status==200:
        raise RuntimeError('Geoapify public key accepted an unapproved browser origin; protect key in MyProjects.')
    raise RuntimeError('Geoapify foreign-origin test inconclusive: HTTP '+str(status))

if __name__=='__main__':
    verify()
