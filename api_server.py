#!/usr/bin/env python3
"""
WellTegra Brahan Forensic Engine - REST API
All-in-one API server with real-time updates
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# ======================================================================
# LOAD DATA
# ======================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename):
    try:
        with open(os.path.join(BASE_DIR, filename)) as f:
            return json.load(f)
    except:
        return {}

# Load all data files
data_files = {
    "risk_scores": "risk_scores.json",
    "fraud": "fraud_detection_report.json",
    "ghost_fish": "complete_jewellery_inventory.json",
    "compliance": "regulatory_compliance.json",
    "integrity": "integrity_scorecard.json",
    "wells": "well_inventory_corrected.json",
    "predictions": "failure_predictions.json",
    "audit": "audit_trail.json"
}

data = {}
for key, filename in data_files.items():
    data[key] = load_json(filename)

# ======================================================================
# API ENDPOINTS
# ======================================================================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "WellTegra Brahan Forensic API",
        "version": "3.0",
        "endpoints": [
            "GET /api/summary",
            "GET /api/wells",
            "GET /api/wells/<well_id>",
            "GET /api/fraud",
            "GET /api/ghost-fish",
            "GET /api/risk-scores",
            "GET /api/compliance",
            "GET /api/predictions",
            "GET /api/audit",
            "POST /api/scan"
        ]
    })

@app.route('/api/summary', methods=['GET'])
def get_summary():
    risk = data.get("risk_scores", {})
    
    return jsonify({
        "total_wells": len(risk),
        "critical": sum(1 for v in risk.values() if v.get("level") == "CRITICAL"),
        "high_risk": sum(1 for v in risk.values() if v.get("level") == "HIGH"),
        "medium_risk": sum(1 for v in risk.values() if v.get("level") == "MEDIUM"),
        "low_risk": sum(1 for v in risk.values() if v.get("level") == "LOW"),
        "compliance_score": data.get("compliance", {}).get("score", 0),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/wells', methods=['GET'])
def get_wells():
    wells = data.get("wells", {}).get("wells", {})
    risk = data.get("risk_scores", {})
    
    result = []
    for well_name, well_data in wells.items():
        well_risk = risk.get(well_name, {})
        result.append({
            "name": well_name,
            "field": well_data.get("field"),
            "files": well_data.get("files"),
            "risk_score": well_risk.get("score", 0),
            "risk_level": well_risk.get("level", "LOW"),
            "factors": well_risk.get("factors", [])
        })
    
    return jsonify(result)

@app.route('/api/wells/<well_id>', methods=['GET'])
def get_well(well_id):
    wells = data.get("wells", {}).get("wells", {})
    risk = data.get("risk_scores", {})
    fraud = data.get("fraud", {}).get("details", [])
    
    well_data = wells.get(well_id, {})
    well_risk = risk.get(well_id, {})
    well_fraud = [f for f in fraud if f.get("well") == well_id]
    
    return jsonify({
        "well_id": well_id,
        "details": well_data,
        "risk": well_risk,
        "fraud_flags": well_fraud
    })

@app.route('/api/fraud', methods=['GET'])
def get_fraud():
    fraud = data.get("fraud", {})
    return jsonify({
        "total": fraud.get("files_flagged", 0),
        "critical": fraud.get("critical", 0),
        "high": fraud.get("high", 0),
        "details": fraud.get("details", [])[:50]
    })

@app.route('/api/ghost-fish', methods=['GET'])
def get_ghost_fish():
    gf = data.get("ghost_fish", {})
    return jsonify(gf.get("ghost_fish", []))

@app.route('/api/risk-scores', methods=['GET'])
def get_risk_scores():
    return jsonify(data.get("risk_scores", {}))

@app.route('/api/compliance', methods=['GET'])
def get_compliance():
    return jsonify(data.get("compliance", {}))

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    return jsonify(data.get("predictions", {}))

@app.route('/api/audit', methods=['GET'])
def get_audit():
    return jsonify(data.get("audit", {}))

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    # In production, this would trigger a new scan
    return jsonify({
        "status": "started",
        "scan_id": f"SCAN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "message": "Scan initiated"
    })

# ======================================================================
# RUN SERVER
# ======================================================================

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("WellTegra Brahan Forensic API v3.0")
    print("=" * 60)
    print()
    print("Running at: http://localhost:5000")
    print()
    print("Endpoints:")
    print("  GET /api/summary")
    print("  GET /api/wells")
    print("  GET /api/fraud")
    print("  GET /api/risk-scores")
    print("  GET /api/compliance")
    print()
    app.run(host='0.0.0.0', port=5000, debug=True)
