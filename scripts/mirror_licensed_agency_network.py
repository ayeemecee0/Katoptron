#!/usr/bin/env python3
"""Mirror fully source-validated EyesOnFlock CC BY-SA agency network for GitHub Pages.

Fetch happens server-side in GitHub Actions, resolving third-party browser CORS.
Generated files contain names, dated portal metadata and directional IDs;
they deliberately strip ALL agency center coordinates to prevent any mixing
with camera position layers. No service-role key or plate data is used.
"""
import json
import sys
from pathlib import Path
from import_licensed_agency_network import KEYS, download, validate

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"data"/"agency-intelligence"

def build(meta,network,edges):
    agencies=validate(meta,network,edges)
    normalized=[]
    for feature in network["features"]:
        p=feature["properties"]
        normalized.append({"properties":{
         "id":p["id"],"name":p["name"],"city":p.get("city") or "",
         "state":p.get("state") or "","type":p.get("type") or "other",
         "isPortal":p.get("isPortal") is True,
         "portalSlug":p.get("portalSlug"),
         "isJunk":p.get("isJunk") is True,
         "isInactive":p.get("isInactive") is True,
         "aliases":p.get("aliases") or [],
         "connectionCount":p.get("connectionCount",0),
         "cameras":p.get("cameras"),
         "hotlistHits":p.get("hotlistHits"),
        }})
    # Preserve data use/attribution. DO NOT copy vendor geocoded lat/lon.
    provenance=dict(
     updated=meta["generatedAt"],generatedAt=meta["generatedAt"],
     source="EyesOnFlock via deflock-data R2",
     source_url="https://deflockdata.dontgetflocked.com/sharing-network-meta.json",
     license="CC BY-SA 4.0",
     license_url="https://creativecommons.org/licenses/by-sa/4.0/",
     transformation="Coordinates omitted; names/IDs preserved, directions kept outbound-only",
     featureCount=len(normalized),portalCount=meta["portalCount"],
     directedEdges=meta["directedEdges"]
    )
    return {"type":"FeatureCollection","features":normalized},edges,provenance


def main():
    meta,geojson,edges=(download(name) for name in KEYS)
    nodes,adj,manifest=build(meta,geojson,edges)
    DEST.mkdir(parents=True,exist_ok=True)
    for name,obj in (("nodes.json",nodes),("adjacency.json",adj),("manifest.json",manifest)):
        data=json.dumps(obj,ensure_ascii=False,separators=(",",":"))+"\n"
        if len(data.encode("utf8"))>35_000_000:
            raise ValueError("Mirrored network file would exceed public artifact safety bound")
        target=DEST/name
        temp=target.with_suffix(".pending")
        temp.write_text(data,encoding="utf8")
        temp.replace(target)
    print("Mirrored source network:",manifest["featureCount"],"identities,",
          manifest["portalCount"],"portals,",
          manifest["directedEdges"],"directional source edges.")
    print("Coordinate-bearing data written to public artifact: ZERO.")


if __name__=="__main__":
    try:main()
    except Exception as exc:
        raise SystemExit("Agency mirror HELD: "+type(exc).__name__+
                         ": "+str(exc)[:140]) from None
