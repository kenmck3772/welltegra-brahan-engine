#!/usr/bin/env python3
"""
WELLTEGRA MASTER SCANNER
One Command - Complete Forensic Analysis
"""

import os
import re
import json
import hashlib
from datetime import datetime
from collections import defaultdict

# ======================================================================
# CONFIGURATION
# ======================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAS_DIR = os.path.join(BASE_DIR, "brahan_engine_data/las_files")
PDF_DIR = os.path.join(BASE_DIR, "brahan_engine_data/pdf_files")
TIFF_DIR = os.path.join(BASE_DIR, "brahan_engine_data/tiff_files")
OUTPUT_DIR = os.path.join(BASE_DIR, "scan_results")

SCAN_ID = f"SCAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ======================================================================
# MAIN SCANNER CLASS
# ======================================================================

class WellTegraScanner:
    def __init__(self):
        self.results = {
            "scan_id": SCAN_ID,
            "timestamp": datetime.now().isoformat(),
            "inventory": {},
            "wells": {},
            "fraud": {},
            "ghost_fish": [],
            "green_cement": {},
            "cement_jobs": {},
            "locations": {},
            "caliper": {},
            "summary": {}
        }
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # ----- PHASE 1: FILE INVENTORY -----
    def scan_inventory(self):
        print("📂 PHASE 1: File Inventory")
        print("-" * 40)
        
        las = [f for f in os.listdir(LAS_DIR) if f.endswith('.las')] if os.path.exists(LAS_DIR) else []
        pdf = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')] if os.path.exists(PDF_DIR) else []
        
        tiff = 0
        if os.path.exists(TIFF_DIR):
            for f in os.listdir(TIFF_DIR):
                if f.lower().endswith(('.tiff', '.tif')):
                    tiff += 1
        
        self.results["inventory"] = {
            "las": len(las),
            "pdf": len(pdf),
            "tiff": tiff,
            "total": len(las) + len(pdf) + tiff
        }
        
        print(f"   LAS: {len(las)}")
        print(f"   PDF: {len(pdf)}")
        print(f"   TIFF: {tiff}")
        print(f"   Total: {self.results['inventory']['total']}")
        print()
        
        return las
    
    # ----- PHASE 2: WELL EXTRACTION -----
    def scan_wells(self, las_files):
        print("🔍 PHASE 2: Well Extraction")
        print("-" * 40)
        
        wells = defaultdict(lambda: {"files": [], "field": "", "company": ""})
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            well_name = "UNKNOWN"
            field = ""
            company = ""
            
            for line in content.split('\n'):
                if 'WELL' in line.upper() and '.' in line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        well_name = parts[1].split(':')[0].strip()
                if 'FLD' in line.upper() and '.' in line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        field = parts[1].split(':')[0].strip()
                if 'COMP' in line.upper() and '.' in line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        company = parts[1].split(':')[0].strip()
            
            wells[well_name]["files"].append(filename)
            if field:
                wells[well_name]["field"] = field
            if company:
                wells[well_name]["company"] = company
        
        self.results["wells"] = {k: {"files": len(v["files"]), "field": v["field"], "company": v["company"]} for k, v in wells.items()}
        
        print(f"   Unique wells: {len(wells)}")
        top = sorted(wells.items(), key=lambda x: -len(x[1]["files"]))[:5]
        for name, data in top:
            print(f"      {name}: {len(data['files'])} files")
        print()
        
        return wells
    
    # ----- PHASE 3: FRAUD DETECTION -----
    def scan_fraud(self, las_files):
        print("🚨 PHASE 3: Fraud Detection")
        print("-" * 40)
        
        fraud_flags = []
        critical = 0
        high = 0
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            well_info = {}
            for line in content.split('\n'):
                if '.' in line:
                    parts = line.split('.')
                    if len(parts) >= 2:
                        mnem = parts[0].strip().upper()
                        data = parts[1].split(':')[0].strip()
                        well_info[mnem] = data
            
            flags = []
            
            # Check UWI
            uwi = well_info.get('UWI', '')
            if uwi in ['', '1', '-999', '-9999', '0']:
                flags.append({"code": "F001", "type": "INVALID_UWI", "severity": "HIGH"})
                high += 1
            
            # Check coords
            lat = well_info.get('LATI', '')
            lon = well_info.get('LONG', '')
            if lat in ['', '0', '-999'] or lon in ['', '0', '-999']:
                flags.append({"code": "F002", "type": "MISSING_COORDS", "severity": "MEDIUM"})
            
            # Check depths
            try:
                strt = float(well_info.get('STRT', 0))
                stop = float(well_info.get('STOP', 0))
                if stop <= strt:
                    flags.append({"code": "F004", "type": "INVALID_DEPTH", "severity": "CRITICAL"})
                    critical += 1
            except:
                pass
            
            if flags:
                fraud_flags.append({"file": filename, "well": well_info.get('WELL', 'UNKNOWN'), "flags": flags})
        
        self.results["fraud"] = {
            "files_flagged": len(fraud_flags),
            "critical": critical,
            "high": high,
            "details": fraud_flags[:50]
        }
        
        print(f"   Files flagged: {len(fraud_flags)}")
        print(f"   CRITICAL: {critical}")
        print(f"   HIGH: {high}")
        print()
    
    # ----- PHASE 4: GHOST FISH -----
    def scan_ghost_fish(self, las_files):
        print("🐟 PHASE 4: Ghost Fish Detection")
        print("-" * 40)
        
        ghost_fish = []
        patterns = ["STUCK", "LOST", "FISH", "JUNK", "WIRE FAILURE", "LEFT IN HOLE"]
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            well = "UNKNOWN"
            for line in content.split('\n'):
                if 'WELL' in line.upper() and '.' in line:
                    well = line.split('.')[1].split(':')[0].strip()
                    break
            
            content_upper = content.upper()
            
            for pattern in patterns:
                if pattern in content_upper:
                    ghost_fish.append({
                        "file": filename,
                        "well": well,
                        "type": pattern
                    })
                    break
        
        self.results["ghost_fish"] = ghost_fish
        
        # Count by well
        by_well = defaultdict(int)
        for gf in ghost_fish:
            by_well[gf["well"]] += 1
        
        print(f"   Ghost fish found: {len(ghost_fish)}")
        for well, count in sorted(by_well.items(), key=lambda x: -x[1])[:5]:
            print(f"      {well}: {count}")
        print()
    
    # ----- PHASE 5: GREEN CEMENT -----
    def scan_green_cement(self, las_files):
        print("🟢 PHASE 5: Green Cement Analysis")
        print("-" * 40)
        
        gr_files = []
        GR_MNEMS = ["GR", "GAMMA", "GAMMA_RAY"]
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            content_upper = content.upper()
            
            for mnem in GR_MNEMS:
                if mnem in content_upper:
                    well = "UNKNOWN"
                    date = ""
                    for line in content.split('\n'):
                        if 'WELL' in line.upper() and '.' in line:
                            well = line.split('.')[1].split(':')[0].strip()
                        if 'DATE' in line.upper() and '.' in line:
                            date = line.split('.')[1].split(':')[0].strip()
                    
                    gr_files.append({"well": well, "date": date})
                    break
        
        # Group by well
        wells_with_gr = defaultdict(list)
        for gf in gr_files:
            wells_with_gr[gf["well"]].append(gf)
        
        # Find time-lapse candidates
        timelapse = {k: len(v) for k, v in wells_with_gr.items() if len(v) >= 2}
        
        self.results["green_cement"] = {
            "gr_files": len(gr_files),
            "wells_with_gr": len(wells_with_gr),
            "timelapse_candidates": timelapse
        }
        
        print(f"   GR files: {len(gr_files)}")
        print(f"   Time-lapse candidates: {len(timelapse)}")
        print()
    
    # ----- PHASE 6: CEMENT JOBS -----
    def scan_cement_jobs(self, las_files):
        print("📦 PHASE 6: Cement Job Data")
        print("-" * 40)
        
        cement_data = []
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            content_upper = content.upper()
            
            if "CEMENT" in content_upper or "WOC" in content_upper or "SQUEEZE" in content_upper:
                well = "UNKNOWN"
                for line in content.split('\n'):
                    if 'WELL' in line.upper() and '.' in line:
                        well = line.split('.')[1].split(':')[0].strip()
                        break
                
                cement_data.append({"well": well, "file": filename})
        
        self.results["cement_jobs"] = {
            "files_with_cement_data": len(cement_data),
            "details": cement_data[:20]
        }
        
        print(f"   Cement data files: {len(cement_data)}")
        print()
    
    # ----- PHASE 7: CALIPER -----
    def scan_caliper(self, las_files):
        print("📏 PHASE 7: Caliper/Corrosion")
        print("-" * 40)
        
        caliper_files = []
        CAL_MNEMS = ["CAL", "CALI", "CCL", "DCAL", "IDQC", "USIT"]
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            content_upper = content.upper()
            found = []
            
            for mnem in CAL_MNEMS:
                if mnem in content_upper:
                    found.append(mnem)
            
            if found:
                caliper_files.append({"file": filename, "curves": found})
        
        self.results["caliper"] = {
            "files_with_caliper": len(caliper_files),
            "details": caliper_files[:20]
        }
        
        print(f"   Caliper files: {len(caliper_files)}")
        print()
    
    # ----- PHASE 8: LOCATIONS -----
    def scan_locations(self, las_files):
        print("📍 PHASE 8: Location Verification")
        print("-" * 40)
        
        valid = 0
        missing = 0
        
        for filename in las_files:
            filepath = os.path.join(LAS_DIR, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            except:
                continue
            
            lat = ""
            lon = ""
            
            for line in content.split('\n'):
                if 'LATI' in line.upper() and '.' in line:
                    lat = line.split('.')[1].split(':')[0].strip()
                if 'LONG' in line.upper() and '.' in line:
                    lon = line.split('.')[1].split(':')[0].strip()
            
            if lat in ['', '0', '-999'] or lon in ['', '0', '-999']:
                missing += 1
            else:
                valid += 1
        
        self.results["locations"] = {
            "valid": valid,
            "missing": missing
        }
        
        print(f"   Valid: {valid}")
        print(f"   Missing: {missing}")
        print()
    
    # ----- GENERATE REPORTS -----
    def generate_reports(self):
        print("📊 Generating Reports...")
        print("-" * 40)
        
        # Summary
        self.results["summary"] = {
            "total_files": self.results["inventory"]["total"],
            "wells_found": len(self.results["wells"]),
            "fraud_flags": self.results["fraud"]["files_flagged"],
            "critical_issues": self.results["fraud"]["critical"],
            "ghost_fish": len(self.results["ghost_fish"]),
            "missing_coordinates": self.results["locations"]["missing"]
        }
        
        # Save JSON
        json_path = os.path.join(OUTPUT_DIR, f"{SCAN_ID}_complete.json")
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Generate HTML
        html = self.generate_html()
        html_path = os.path.join(OUTPUT_DIR, f"{SCAN_ID}_dashboard.html")
        with open(html_path, 'w') as f:
            f.write(html)
        
        print(f"   {SCAN_ID}_complete.json")
        print(f"   {SCAN_ID}_dashboard.html")
        print()
    
    def generate_html(self):
        s = self.results["summary"]
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>WellTegra Complete Scan Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial; background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); color: #e0e0e0; padding: 20px; }}
        .header {{ text-align: center; padding: 30px; background: rgba(22, 33, 62, 0.8); border-radius: 15px; margin-bottom: 20px; }}
        h1 {{ color: #00d4ff; font-size: 2em; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #16213e; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
        .stat-label {{ color: #888; margin-top: 5px; }}
        .critical {{ color: #ff6b6b; }}
        .warning {{ color: #ffd93d; }}
        .good {{ color: #4ecca3; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #0f3460; color: #00d4ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 WellTegra Complete Scan</h1>
        <p>{SCAN_ID}</p>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-value">{s["total_files"]}</div><div class="stat-label">Files</div></div>
        <div class="stat"><div class="stat-value">{s["wells_found"]}</div><div class="stat-label">Wells</div></div>
        <div class="stat"><div class="stat-value critical">{s["critical_issues"]}</div><div class="stat-label">Critical</div></div>
        <div class="stat"><div class="stat-value warning">{s["ghost_fish"]}</div><div class="stat-label">Ghost Fish</div></div>
        <div class="stat"><div class="stat-value warning">{s["missing_coordinates"]}</div><div class="stat-label">Missing Coords</div></div>
    </div>
    
    <div class="card">
        <h2>Inventory</h2>
        <table>
            <tr><th>Type</th><th>Count</th></tr>
            <tr><td>LAS Files</td><td>{self.results["inventory"]["las"]}</td></tr>
            <tr><td>PDF Documents</td><td>{self.results["inventory"]["pdf"]}</td></tr>
            <tr><td>TIFF Images</td><td>{self.results["inventory"]["tiff"]}</td></tr>
        </table>
    </div>
    
    <div class="card">
        <h2>Top Wells by File Count</h2>
        <table>
            <tr><th>Well</th><th>Files</th><th>Field</th></tr>
'''
        
        for well, data in sorted(self.results["wells"].items(), key=lambda x: -x[1]["files"])[:15]:
            html += f'        <tr><td>{well}</td><td>{data["files"]}</td><td>{data["field"] or "UNKNOWN"}</td></tr>\n'
        
        html += f'''        </table>
    </div>
    
    <div class="card">
        <h2>Fraud Detection</h2>
        <p>Files Flagged: {self.results["fraud"]["files_flagged"]}</p>
        <p class="critical">Critical Issues: {self.results["fraud"]["critical"]}</p>
        <p class="warning">High Risk: {self.results["fraud"]["high"]}</p>
    </div>
    
    <div class="card">
        <h2>Ghost Fish</h2>
        <p>Items stuck/lost: {len(self.results["ghost_fish"])}</p>
    </div>
    
    <div class="card">
        <h2>Green Cement Analysis</h2>
        <p>GR Files: {self.results["green_cement"]["gr_files"]}</p>
        <p>Time-lapse Candidates: {len(self.results["green_cement"]["timelapse_candidates"])}</p>
    </div>
    
    <div class="card">
        <h2>Location Status</h2>
        <p class="good">Valid Coordinates: {self.results["locations"]["valid"]}</p>
        <p class="warning">Missing Coordinates: {self.results["locations"]["missing"]}</p>
    </div>
    
    <p style="text-align: center; color: #666; padding: 20px;">WellTegra Forensic Engine v3.0 | Complete Scan</p>
</body>
</html>'''
        
        return html
    
    # ----- RUN ALL -----
    def run_all(self):
        print()
        print("=" * 70)
        print("WELLTEGRA MASTER SCANNER")
        print(f"Scan ID: {SCAN_ID}")
        print("=" * 70)
        print()
        
        # Phase 1
        las_files = self.scan_inventory()
        
        # Phase 2
        self.scan_wells(las_files)
        
        # Phase 3
        self.scan_fraud(las_files)
        
        # Phase 4
        self.scan_ghost_fish(las_files)
        
        # Phase 5
        self.scan_green_cement(las_files)
        
        # Phase 6
        self.scan_cement_jobs(las_files)
        
        # Phase 7
        self.scan_caliper(las_files)
        
        # Phase 8
        self.scan_locations(las_files)
        
        # Reports
        self.generate_reports()
        
        # Final Summary
        print("=" * 70)
        print("✅ SCAN COMPLETE")
        print("=" * 70)
        print()
        
        s = self.results["summary"]
        
        print("SUMMARY")
        print("-" * 40)
        print(f"  Files scanned:   {s['total_files']}")
        print(f"  Wells found:     {s['wells_found']}")
        print(f"  Fraud flags:     {s['fraud_flags']}")
        print(f"  Critical:        {s['critical_issues']}")
        print(f"  Ghost fish:      {s['ghost_fish']}")
        print()
        print(f"📁 Output: {OUTPUT_DIR}")
        print()
        print("=" * 70)

# ======================================================================
# MAIN
# ======================================================================

if __name__ == "__main__":
    scanner = WellTegraScanner()
    scanner.run_all()
