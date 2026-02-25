#!/usr/bin/env python3
"""
WELLTEGRA - BRAHAN FORENSIC SCANNER
================================
Scans ALL file types: LAS + PDF + TIFF
One command - Complete analysis
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else os.getcwd()
LAS_DIR = os.path.join(BASE_DIR, "brahan_engine_data/las_files")
PDF_DIR = os.path.join(BASE_DIR, "brahan_engine_data/pdf_files")
TIFF_DIR = os.path.join(BASE_DIR, "brahan_engine_data/tiff_files")
OUTPUT_DIR = os.path.join(BASE_DIR, "unified_scan_results")

SCAN_ID = f"UNIFIED-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ======================================================================
# MASTER SCANNER CLASS
# ======================================================================

class UnifiedMasterScanner:
    def __init__(self):
        self.results = {
            "scan_id": SCAN_ID,
            "timestamp": datetime.now().isoformat(),
            "inventory": {},
            "wells": {},
            "fraud": {},
            "ghost_fish": [],
            "perforations": {},
            "barriers": {},
            "equipment": {},
            "tiff_analysis": {},
            "summary": {}
        }
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # ----- PHASE 1: INVENTORY ALL FILES -----
    def scan_inventory(self):
        print("📂 PHASE 1: Inventory (LAS + PDF + TIFF)")
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
        
        print(f"   LAS:  {len(las)}")
        print(f"   PDF:  {len(pdf)}")
        print(f"   TIFF: {tiff}")
        print(f"   Total: {self.results['inventory']['total']}")
        print()
        
        return las, pdf
    
    # ----- PHASE 2: LAS ANALYSIS -----
    def scan_las(self, las_files):
        print("📄 PHASE 2: LAS File Analysis")
        print("-" * 40)
        
        wells = defaultdict(lambda: {"files": [], "field": "", "company": ""})
        fraud_flags = []
        ghost_fish = []
        perforations = []
        barriers = []
        equipment = []
        
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
            
            well = well_info.get('WELL', 'UNKNOWN')
            field = well_info.get('FLD', '')
            company = well_info.get('COMP', '')
            
            wells[well]["files"].append(filename)
            if field:
                wells[well]["field"] = field
            if company:
                wells[well]["company"] = company
            
            content_upper = content.upper()
            
            # Fraud detection
            flags = []
            uwi = well_info.get('UWI', '')
            if uwi in ['', '1', '-999', '-9999', '0']:
                flags.append({"code": "F001", "type": "INVALID_UWI"})
            
            try:
                strt = float(well_info.get('STRT', 0))
                stop = float(well_info.get('STOP', 0))
                if stop <= strt:
                    flags.append({"code": "F004", "type": "INVALID_DEPTH"})
            except:
                pass
            
            if flags:
                fraud_flags.append({"file": filename, "well": well, "flags": flags})
            
            # Ghost fish
            for pattern in ["STUCK", "LOST", "FISH", "JUNK"]:
                if pattern in content_upper:
                    ghost_fish.append({"file": filename, "well": well, "type": pattern})
                    break
            
            # Perforations
            if 'PERF' in content_upper:
                perforations.append({"file": filename, "well": well})
            
            # Barriers
            for btype in ["CEMENT", "PACKER", "PLUG", "BRIDGE"]:
                if btype in content_upper:
                    barriers.append({"file": filename, "well": well, "type": btype})
            
            # Equipment
            for equip in ["SSSV", "NIPPLE", "GLV", "MANDREL"]:
                if equip in content_upper:
                    equipment.append({"file": filename, "well": well, "type": equip})
        
        self.results["wells"] = {k: {"files": len(v["files"]), "field": v["field"], "company": v["company"]} for k, v in wells.items()}
        self.results["fraud"] = {"count": len(fraud_flags), "details": fraud_flags[:50]}
        self.results["ghost_fish"] = ghost_fish
        self.results["perforations"] = {"las_count": len(perforations), "files": perforations}
        self.results["barriers"] = {"las_count": len(barriers), "files": barriers}
        self.results["equipment"] = {"las_count": len(equipment), "files": equipment}
        
        print(f"   Wells found: {len(wells)}")
        print(f"   Fraud flags: {len(fraud_flags)}")
        print(f"   Ghost fish: {len(ghost_fish)}")
        print(f"   Perforation files: {len(perforations)}")
        print(f"   Barrier files: {len(barriers)}")
        print()
    
    # ----- PHASE 3: PDF ANALYSIS -----
    def scan_pdf(self, pdf_files):
        print("📄 PHASE 3: PDF File Analysis")
        print("-" * 40)
        
        # PDF categories
        CATEGORIES = {
            "CEMENT": ["CEMENT", "CBL", "BOND", "SQUEEZE"],
            "COMPLETION": ["COMPLETION", "TUBING", "TALLY"],
            "PERFORATION": ["PERF", "GUN", "TCP"],
            "EOWR": ["EOWR", "END OF WELL", "ABANDONMENT"],
            "DRILLING": ["DRILL", "EOWR", "REPORT"],
            "TEST": ["TEST", "PRESSURE", "DST"],
            "CORE": ["CORE", "SAMPLE"],
            "LOG": ["LOG", "LITH", "WIRE"]
        }
        
        by_category = defaultdict(list)
        by_well = defaultdict(list)
        
        for pdf in pdf_files:
            pdf_upper = pdf.upper()
            
            # Extract well from filename
            well = "UNKNOWN"
            parts = pdf.split('_')
            if len(parts) >= 2:
                well = parts[0]
            
            by_well[well].append(pdf)
            
            # Categorize
            for cat, keywords in CATEGORIES.items():
                for kw in keywords:
                    if kw in pdf_upper:
                        by_category[cat].append(pdf)
                        break
        
        self.results["pdf_analysis"] = {
            "total": len(pdf_files),
            "by_category": {k: len(v) for k, v in by_category.items()},
            "by_well": {k: len(v) for k, v in by_well.items()}
        }
        
        print(f"   Total PDFs: {len(pdf_files)}")
        for cat, files in sorted(by_category.items(), key=lambda x: -len(x[1]))[:8]:
            print(f"      {cat}: {len(files)}")
        print()
    
    # ----- PHASE 4: TIFF ANALYSIS -----
    def scan_tiff(self):
        print("🖼️ PHASE 4: TIFF File Analysis")
        print("-" * 40)
        
        if not os.path.exists(TIFF_DIR):
            print("   TIFF directory not found")
            return
        
        tiff_files = [f for f in os.listdir(TIFF_DIR) if f.lower().endswith(('.tiff', '.tif'))]
        
        # Categories
        LOG_TYPES = {
            "PERFORATION": ["PERF", "CCL", "GUN"],
            "CEMENT": ["CEMENT", "CBL", "BOND"],
            "GAMMA": ["GR", "GAMMA"],
            "CALIPER": ["CAL", "CALI"],
            "COMPLETION": ["COMP", "SCHEMATIC"],
            "LOG": ["LOG", "LITH", "WIRE"]
        }
        
        by_type = defaultdict(list)
        by_well = defaultdict(list)
        
        for tiff in tiff_files:
            tiff_upper = tiff.upper()
            
            # Extract well
            well = tiff.split('_')[0] if '_' in tiff else "UNKNOWN"
            by_well[well].append(tiff)
            
            # Categorize
            for log_type, keywords in LOG_TYPES.items():
                for kw in keywords:
                    if kw in tiff_upper:
                        by_type[log_type].append(tiff)
                        break
        
        self.results["tiff_analysis"] = {
            "total": len(tiff_files),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_well": {k: len(v) for k, v in by_well.items()},
            "perforation_tiffs": by_type.get("PERFORATION", [])
        }
        
        print(f"   Total TIFFs: {len(tiff_files)}")
        for log_type, files in sorted(by_type.items(), key=lambda x: -len(x[1]))[:8]:
            print(f"      {log_type}: {len(files)}")
        print()
    
    # ----- PHASE 5: CROSS-REFERENCE -----
    def cross_reference(self):
        print("🔗 PHASE 5: Cross-Reference")
        print("-" * 40)
        
        # Find wells with data in all formats
        wells_with_las = set(self.results["wells"].keys())
        wells_with_pdf = set(self.results["pdf_analysis"]["by_well"].keys())
        wells_with_tiff = set(self.results["tiff_analysis"]["by_well"].keys())
        
        all_wells = wells_with_las | wells_with_pdf | wells_with_tiff
        complete_wells = wells_with_las & wells_with_pdf & wells_with_tiff
        
        self.results["cross_reference"] = {
            "total_unique_wells": len(all_wells),
            "wells_with_las": len(wells_with_las),
            "wells_with_pdf": len(wells_with_pdf),
            "wells_with_tiff": len(wells_with_tiff),
            "complete_coverage": len(complete_wells),
            "complete_wells": list(complete_wells)
        }
        
        print(f"   Total unique wells: {len(all_wells)}")
        print(f"   With LAS data: {len(wells_with_las)}")
        print(f"   With PDF data: {len(wells_with_pdf)}")
        print(f"   With TIFF data: {len(wells_with_tiff)}")
        print(f"   Complete coverage: {len(complete_wells)}")
        print()
    
    # ----- PHASE 6: SUMMARY -----
    def generate_summary(self):
        self.results["summary"] = {
            "total_files": self.results["inventory"]["total"],
            "unique_wells": len(self.results["wells"]),
            "fraud_flags": self.results["fraud"]["count"],
            "ghost_fish": len(self.results["ghost_fish"]),
            "perforation_files": self.results["perforations"]["las_count"],
            "barrier_files": self.results["barriers"]["las_count"]
        }
    
    # ----- GENERATE REPORTS -----
    def generate_reports(self):
        print("📊 Generating Reports...")
        print("-" * 40)
        
        # JSON
        json_path = os.path.join(OUTPUT_DIR, f"{SCAN_ID}.json")
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # HTML
        html = self.generate_html()
        html_path = os.path.join(OUTPUT_DIR, f"{SCAN_ID}.html")
        with open(html_path, 'w') as f:
            f.write(html)
        
        print(f"   {SCAN_ID}.json")
        print(f"   {SCAN_ID}.html")
        print()
    
    def generate_html(self):
        s = self.results["summary"]
        inv = self.results["inventory"]
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>WellTegra Unified Scan</title>
    <style>
        body {{ font-family: Arial; background: #1a1a2e; color: #e0e0e0; padding: 20px; }}
        .header {{ text-align: center; padding: 30px; background: #16213e; border-radius: 10px; margin-bottom: 20px; }}
        h1 {{ color: #00d4ff; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #16213e; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
        .stat-label {{ color: #888; margin-top: 5px; }}
        .card {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 15px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #0f3460; color: #00d4ff; }}
        .critical {{ color: #ff6b6b; }}
        .warning {{ color: #ffd93d; }}
        .good {{ color: #4ecca3; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WellTegra - Brahan Forensic Scanner</h1>
        <p>{SCAN_ID}</p>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-value">{inv['total']}</div><div class="stat-label">Total Files</div></div>
        <div class="stat"><div class="stat-value">{inv['las']}</div><div class="stat-label">LAS</div></div>
        <div class="stat"><div class="stat-value">{inv['pdf']}</div><div class="stat-label">PDF</div></div>
        <div class="stat"><div class="stat-value">{inv['tiff']}</div><div class="stat-label">TIFF</div></div>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-value">{s['unique_wells']}</div><div class="stat-label">Wells</div></div>
        <div class="stat"><div class="stat-value critical">{s['fraud_flags']}</div><div class="stat-label">Fraud Flags</div></div>
        <div class="stat"><div class="stat-value warning">{s['ghost_fish']}</div><div class="stat-label">Ghost Fish</div></div>
        <div class="stat"><div class="stat-value good">{s['perforation_files']}</div><div class="stat-label">Perf Files</div></div>
    </div>
    
    <div class="card">
        <h2>File Coverage</h2>
        <table>
            <tr><th>Well</th><th>LAS</th><th>PDF</th><th>TIFF</th></tr>
'''
        
        for well in list(self.results["wells"].keys())[:15]:
            las_count = self.results["wells"][well]["files"]
            pdf_count = self.results["pdf_analysis"]["by_well"].get(well, 0)
            tiff_count = self.results["tiff_analysis"]["by_well"].get(well, 0)
            html += f'<tr><td>{well}</td><td>{las_count}</td><td>{pdf_count}</td><td>{tiff_count}</td></tr>\n'
        
        html += '''        </table>
    </div>
    
    <p style="text-align: center; color: #666; padding: 20px;">WellTegra Brahan Scanner v3.0</p>
</body>
</html>'''
    
    # ----- RUN ALL -----
    def run(self):
        print()
        print("=" * 70)
        print("WELLTEGRA - BRAHAN FORENSIC SCANNER")
        print(f"Scan ID: {SCAN_ID}")
        print("=" * 70)
        print()
        
        las_files, pdf_files = self.scan_inventory()
        self.scan_las(las_files)
        self.scan_pdf(pdf_files)
        self.scan_tiff()
        self.cross_reference()
        self.generate_summary()
        self.generate_reports()
        
        print("=" * 70)
        print("✅ BRAHAN FORENSIC SCAN COMPLETE")
        print("=" * 70)
        print()
        
        s = self.results["summary"]
        print("SUMMARY")
        print("-" * 40)
        print(f"  Files:     {s['total_files']}")
        print(f"  Wells:     {s['unique_wells']}")
        print(f"  Fraud:     {s['fraud_flags']}")
        print(f"  Ghost:     {s['ghost_fish']}")
        print(f"  Perf:      {s['perforation_files']}")
        print()
        print(f"📁 Output: {OUTPUT_DIR}")
        print()
        print("=" * 70)

# ======================================================================
# MAIN
# ======================================================================

if __name__ == "__main__":
    scanner = UnifiedMasterScanner()
    scanner.run()
