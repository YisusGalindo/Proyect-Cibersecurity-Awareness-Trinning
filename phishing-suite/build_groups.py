#!/usr/bin/env python3
import csv, json, sys
path = sys.argv[1]
by_region_dept = {}
agg = {"MX": [], "US": []}
with open(path, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        region = r['region'].strip().upper()
        dept = r['department'].strip()
        email = r['email'].strip()
        first = r['first_name'].strip()
        last = r['last_name'].strip()
        key = (region, dept)
        by_region_dept.setdefault(key, []).append({
            "first_name": first,
            "last_name": last,
            "email": email
        })
        agg.setdefault(region, []).append({
            "first_name": first,
            "last_name": last,
            "email": email
        })
out = []
for (region, dept), members in by_region_dept.items():
    out.append({"name": f"{region}_{dept}", "targets": members})
for region, members in agg.items():
    out.append({"name": f"{region}_All", "targets": members})
print(json.dumps(out))
