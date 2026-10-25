"""Bounded read-only audit of public OSM-derived U.S. ALPR GeoJSON.

No coordinates printed, no Supabase connection, no persistent copy.
"""
import gzip,json,io,urllib.request
URL='https://data.dontgetflocked.com/cameras.geojson.gz'
MAX_BYTES=50_000_000
req=urllib.request.Request(URL,headers={'User-Agent':'Katoptron-civic-open-data-audit/1.0','Accept':'application/geo+json, application/json'})
with urllib.request.urlopen(req,timeout=90) as response:
    data=response.read(MAX_BYTES+1)
    print('ALPR FEED http_status',response.status)
    print('ALPR FEED compressed_or_raw_bytes',len(data))
if not 100_000<len(data)<=MAX_BYTES:raise SystemExit('Feed exceeded bounds or empty')
if data[:2]==b'\x1f\x8b':
    data=gzip.decompress(data)
if len(data)>140_000_000:raise SystemExit('Decoded feed unexpectedly large')
fc=json.loads(data)
features=fc.get('features') if isinstance(fc,dict) else None
if not isinstance(features,list) or not 50_000<len(features)<400_000:
    raise SystemExit('Unexpected ALPR feature count')
p=features[0].get('properties',{}) if isinstance(features[0],dict) else {}
print('ALPR FEED feature_count',len(features))
print('ALPR FEED sample_field_names',sorted(p))
flock=0;identifiable=0;point=0
for row in features:
    p=row.get('properties') if isinstance(row,dict) else None
    g=row.get('geometry') if isinstance(row,dict) else None
    if isinstance(g,dict) and g.get('type')=='Point':point+=1
    if isinstance(p,dict):
        b=str(p.get('brand') or p.get('manufacturer') or '').strip().lower()
        if b:identifiable+=1
        if b.startswith(('flock','floc')):flock+=1
print('ALPR FEED point_features',point)
print('ALPR FEED explicitly_Flock_labeled',flock)
print('ALPR FEED source_brand_identified',identifiable)
print('ALPR FEED no camera locations or identities printed')
