#!/usr/bin/env python3
"""
Wellabuild Integration Module
Bridges the forensic engine with wellabuild capabilities
"""

import os
import sys
import json
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class WellabuildBridge:
    """Integration bridge between Brahan Forensic Engine and Wellabuild SDK"""
    
    def __init__(self):
        self.wellabuild_available = False
        self.check_wellabuild()
    
    def check_wellabuild(self):
        """Check if wellabuild modules are available"""
        try:
            sys.path.insert(0, os.path.expanduser("~/wellabuild"))
            from wellabuild import wellabuild_sdk
            from wellabuild import gr_cement_analyzer
            from wellabuild import wellbore_objects
            from wellabuild import environmental_predicates
            
            self.wellabuild_available = True
            print("✅ Wellabuild modules loaded")
        except ImportError as e:
            print(f"⚠️ Wellabuild not available: {e}")
            self.wellabuild_available = False
    
    def check_environmental_compliance(self, well_id):
        """Check environmental compliance for a well"""
        try:
            with open(os.path.join(BASE_DIR, "risk_scores.json")) as f:
                risk_data = json.load(f)
            
            well_risk = risk_data.get(well_id, {})
            
            return {
                "well_id": well_id,
                "environmental_score": 100 - well_risk.get("score", 0),
                "compliance_status": "PASS" if well_risk.get("score", 0) < 30 else "FAIL"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_full_integration(self):
        """Run full integration with all wellabuild capabilities"""
        return {
            "status": "ok" if self.wellabuild_available else "limited",
            "modules": ["wellabuild_sdk", "gr_cement_analyzer", "wellbore_objects", "environmental_predicates"] if self.wellabuild_available else []
        }

if __name__ == "__main__":
    print("=" * 60)
    print("Wellabuild Integration Module")
    print("=" * 60)
    
    bridge = WellabuildBridge()
    result = bridge.run_full_integration()
    print(f"Status: {result['status']}")
    print(f"Modules: {result['modules']}")
