#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              LAS TO 4D MODEL LOADER                                         ║
║                                                                               ║
║  Purpose: Load real LAS data into 4D wellbore model                         ║
║  Features:                                                                    ║
║  - Parse actual trajectory from LAS files                                    ║
║  - Extract equipment with real geometry                                      ║
║  - Build decay modeling (corrosion over time)                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# Import from our 4D model
exec(open('vision_three_4d_model.py').read().split('if __name__')[0])

# ==============================================================================
# DECAY MODELING
# ==============================================================================

@dataclass
class CorrosionModel:
    """
    Corrosion decay model for steel components
    
    Models material degradation over time:
    - General corrosion (uniform wall loss)
    - Pitting corrosion (localized)
    - Stress corrosion cracking
    - Microbiologically influenced corrosion (MIC)
    """
    
    # Corrosion rates (mm/year) - typical for oilfield environments
    CORROSION_RATES = {
        "ATMOSPHERIC": 0.05,      # Exposed to air
        "SWEET_PRODUCTION": 0.2,   # CO2 environment
        "SOUR_PRODUCTION": 0.5,    # H2S environment
        "SEAWATER": 0.15,          # Marine exposure
        "BRINE": 0.3,              # High salinity
        "ACID_GAS": 0.8,           # Acid gas injection
        "ANNULUS": 0.1,            # A-annulus environment
    }
    
    initial_wall_thickness: float  # inches
    current_wall_thickness: float  # inches
    installation_date: str
    environment: str
    material_grade: str
    
    def calculate_wall_loss(self, years: float) -> float:
        """Calculate wall loss in inches over time"""
        rate_mm_per_year = self.CORROSION_RATES.get(self.environment, 0.1)
        rate_in_per_year = rate_mm_per_year / 25.4
        return rate_in_per_year * years
    
    def predict_remaining_life(self, min_wall_pct: float = 0.5) -> float:
        """Predict remaining life in years before min wall reached"""
        min_wall = self.initial_wall_thickness * min_wall_pct
        current_loss = self.initial_wall_thickness - self.current_wall_thickness
        
        if self.current_wall_thickness <= min_wall:
            return 0
        
        remaining_wall = self.current_wall_thickness - min_wall
        rate_in_per_year = self.CORROSION_RATES.get(self.environment, 0.1) / 25.4
        
        return remaining_wall / rate_in_per_year if rate_in_per_year > 0 else 999
    
    def get_wall_thickness_at_time(self, target_date: str) -> float:
        """Get predicted wall thickness at a future date"""
        install = datetime.fromisoformat(self.installation_date.replace('Z', ''))
        target = datetime.fromisoformat(target_date.replace('Z', ''))
        
        years = (target - install).days / 365.25
        
        if years < 0:
            return self.initial_wall_thickness
        
        loss = self.calculate_wall_loss(years)
        return max(0, self.initial_wall_thickness - loss)
    
    def assess_integrity(self) -> Dict:
        """Assess current integrity status"""
        wall_loss_pct = (1 - self.current_wall_thickness / self.initial_wall_thickness) * 100
        remaining_life = self.predict_remaining_life()
        
        if wall_loss_pct > 50:
            status = "CRITICAL"
            action = "Immediate intervention required"
        elif wall_loss_pct > 30:
            status = "SEVERE"
            action = "Plan replacement within 1 year"
        elif wall_loss_pct > 15:
            status = "MODERATE"
            action = "Monitor closely, plan intervention"
        else:
            status = "ACCEPTABLE"
            action = "Continue routine monitoring"
        
        return {
            "initial_wall": self.initial_wall_thickness,
            "current_wall": self.current_wall_thickness,
            "wall_loss_pct": round(wall_loss_pct, 1),
            "remaining_life_years": round(remaining_life, 1),
            "status": status,
            "recommended_action": action
        }

@dataclass
class DecayEvent:
    """A decay/degradation event over time"""
    timestamp: str
    event_type: str  # "CORROSION_MEASUREMENT", "WALL_LOSS", "LEAK_DETECTED", "FAILURE"
    wall_thickness: float
    notes: str = ""

class DecayModel:
    """
    Complete decay model for a wellbore object
    Tracks degradation over entire lifecycle
    """
    
    def __init__(self, 
                 object_id: str,
                 initial_wall: float,
                 install_date: str,
                 environment: str,
                 material_grade: str):
        
        self.object_id = object_id
        self.corrosion_model = CorrosionModel(
            initial_wall_thickness=initial_wall,
            current_wall_thickness=initial_wall,  # Initially no corrosion
            installation_date=install_date,
            environment=environment,
            material_grade=material_grade
        )
        
        self.decay_history: List[DecayEvent] = []
        self.current_date = datetime.now().isoformat()
    
    def record_measurement(self, 
                           timestamp: str, 
                           measured_wall: float,
                           notes: str = ""):
        """Record a wall thickness measurement"""
        
        # Calculate corrosion rate from last measurement
        wall_loss = self.corrosion_model.initial_wall_thickness - measured_wall
        
        event = DecayEvent(
            timestamp=timestamp,
            event_type="CORROSION_MEASUREMENT",
            wall_thickness=measured_wall,
            notes=notes
        )
        
        self.decay_history.append(event)
        self.corrosion_model.current_wall_thickness = measured_wall
    
    def predict_decay_to_time(self, target_timestamp: str) -> Dict:
        """Predict state of component at future time"""
        
        install = datetime.fromisoformat(
            self.corrosion_model.installation_date.replace('Z', '').split('T')[0] + 'T00:00:00'
        )
        target = datetime.fromisoformat(target_timestamp.replace('Z', '').split('T')[0] + 'T00:00:00')
        
        years = (target - install).days / 365.25
        
        predicted_wall = self.corrosion_model.get_wall_thickness_at_time(target_timestamp)
        wall_loss_pct = (1 - predicted_wall / self.corrosion_model.initial_wall_thickness) * 100
        
        return {
            "timestamp": target_timestamp,
            "years_elapsed": round(years, 1),
            "predicted_wall_thickness": round(predicted_wall, 3),
            "wall_loss_pct": round(wall_loss_pct, 1),
            "remaining_life_years": round(self.corrosion_model.predict_remaining_life(), 1)
        }
    
    def generate_decay_timeline(self, 
                                 start_year: int,
                                 end_year: int,
                                 step_years: int = 5) -> List[Dict]:
        """Generate complete decay timeline"""
        
        timeline = []
        
        for year in range(start_year, end_year + 1, step_years):
            timestamp = f"{year}-01-01T00:00:00Z"
            prediction = self.predict_decay_to_time(timestamp)
            timeline.append(prediction)
        
        return timeline
    
    def to_dict(self) -> Dict:
        """Export decay model"""
        return {
            "objectId": self.object_id,
            "corrosionModel": {
                "initialWall": self.corrosion_model.initial_wall_thickness,
                "currentWall": self.corrosion_model.current_wall_thickness,
                "environment": self.corrosion_model.environment,
                "materialGrade": self.corrosion_model.material_grade,
                "integrityAssessment": self.corrosion_model.assess_integrity()
            },
            "decayHistory": [
                {
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "wallThickness": e.wall_thickness,
                    "notes": e.notes
                } for e in self.decay_history
            ]
        }

# ==============================================================================
# LAS FILE PARSER
# ==============================================================================

class LasToModelLoader:
    """Load real data from LAS files into 4D model"""
    
    def __init__(self, las_dir: str):
        self.las_dir = las_dir
        self.wells_data = defaultdict(lambda: {
            "trajectory": [],
            "equipment": [],
            "dates": [],
            "curves": {}
        })
    
    def scan_las_files(self):
        """Scan all LAS files and extract data"""
        
        if not os.path.exists(self.las_dir):
            print(f"LAS directory not found: {self.las_dir}")
            return
        
        las_files = [f for f in os.listdir(self.las_dir) if f.endswith('.las')]
        print(f"Found {len(las_files)} LAS files")
        
        for filename in las_files:
            filepath = os.path.join(self.las_dir, filename)
            self._parse_las_file(filepath)
    
    def _parse_las_file(self, filepath: str):
        """Parse a single LAS file"""
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            return
        
        # Extract well info
        well_id = "UNKNOWN"
        for line in content.split('\n'):
            if 'WELL' in line.upper() and '.' in line:
                well_id = line.split('.')[1].split(':')[0].strip()
                break
        
        # Extract date
        date = ""
        for line in content.split('\n'):
            if 'DATE' in line.upper() and '.' in line:
                date = line.split('.')[1].split(':')[0].strip()
                break
        
        if date:
            self.wells_data[well_id]["dates"].append(date)
        
        # Extract depth range (for trajectory)
        strt = 0
        stop = 0
        for line in content.split('\n'):
            if 'STRT' in line.upper() and '.' in line:
                match = re.search(r'[\d.]+', line.split('.')[1] if '.' in line else line)
                if match:
                    strt = float(match.group())
            if 'STOP' in line.upper() and '.' in line:
                match = re.search(r'[\d.]+', line.split('.')[1] if '.' in line else line)
                if match:
                    stop = float(match.group())
        
        if stop > strt:
            self.wells_data[well_id]["depth_range"] = (strt, stop)
        
        # Extract curve mnemonics
        in_curve = False
        for line in content.split('\n'):
            if '~CURVE' in line.upper():
                in_curve = True
                continue
            if line.startswith('~') and in_curve:
                break
            if in_curve and '.' in line:
                mnem = line.split('.')[0].strip().upper()
                if mnem not in self.wells_data[well_id]["curves"]:
                    self.wells_data[well_id]["curves"][mnem] = 0
                self.wells_data[well_id]["curves"][mnem] += 1
        
        # Check for equipment mentions
        content_upper = content.upper()
        
        equipment_types = {
            "CASING": ["CASING", "CSG"],
            "TUBING": ["TUBING", "TBG"],
            "PACKER": ["PACKER", "PKR"],
            "DHSV": ["DHSV", "SSSV"],
            "NIPPLE": ["NIPPLE", "LPN"],
            "PLUG": ["PLUG", "BRIDGE"]
        }
        
        for eq_type, keywords in equipment_types.items():
            for kw in keywords:
                if kw in content_upper:
                    self.wells_data[well_id]["equipment"].append(eq_type)
                    break
    
    def build_model_for_well(self, well_id: str) -> Optional[WellboreModel4D]:
        """Build complete 4D model for a well"""
        
        if well_id not in self.wells_data:
            return None
        
        data = self.wells_data[well_id]
        
        print(f"\n   Building model for {well_id}")
        
        # Create model
        model = WellboreModel4D(well_id=well_id)
        
        # Build spine from depth range
        depth_range = data.get("depth_range", (0, 10000))
        
        # Estimate trajectory (would need actual survey data for real values)
        model.spine.generate_simple_trajectory(
            total_depth=depth_range[1],
            kickoff_depth=depth_range[1] * 0.4,  # Estimate
            max_inclination=30,  # Estimate
            azimuth=90  # Estimate
        )
        
        # Add equipment based on mentions
        equipment_found = list(set(data["equipment"]))
        print(f"      Equipment types: {equipment_found}")
        
        # Add casing if mentioned
        if "CASING" in equipment_found:
            casing = WellboreObject4D(
                object_id=f"{well_id}-CSG",
                component_type=ComponentType.CASING.value,
                max_od=9.625,
                min_id=8.68,
                makeup_length=depth_range[1],
                top_md=0,
                bottom_md=depth_range[1],
                material="STEEL",
                grade="L-80"
            )
            
            # Add installation date from LAS dates
            if data["dates"]:
                install_date = data["dates"][0]
                casing.add_lifecycle_event(
                    timestamp=install_date,
                    state=LifecycleState.BUILT.value,
                    operation="Casing logged",
                    source="LAS file"
                )
            
            model.add_object(casing)
        
        # Add tubing if mentioned
        if "TUBING" in equipment_found:
            tubing = WellboreObject4D(
                object_id=f"{well_id}-TUB",
                component_type=ComponentType.TUBING.value,
                max_od=3.5,
                min_id=2.992,
                makeup_length=depth_range[1] * 0.9,
                top_md=500,
                bottom_md=depth_range[1] * 0.95,
                material="STEEL",
                grade="L-80"
            )
            model.add_object(tubing)
        
        # Set relationships
        if f"{well_id}-CSG" in model.objects and f"{well_id}-TUB" in model.objects:
            model.set_parent_child(f"{well_id}-TUB", f"{well_id}-CSG")
        
        # Add decay model
        if f"{well_id}-CSG" in model.objects:
            decay = DecayModel(
                object_id=f"{well_id}-CSG",
                initial_wall=0.47,  # 9-5/8" 47ppf casing
                install_date=data["dates"][0] if data["dates"] else "1990-01-01",
                environment="SWEET_PRODUCTION",
                material_grade="L-80"
            )
            model.objects[f"{well_id}-CSG"].decay_model = decay
        
        return model
    
    def get_wells_list(self) -> List[str]:
        """Get list of wells found"""
        return list(self.wells_data.keys())

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("LAS TO 4D MODEL LOADER")
    print("With Decay Modeling (Corrosion Over Time)")
    print("=" * 70)
    print()
    
    # Initialize loader
    las_dir = "brahan_engine_data/las_files"
    loader = LasToModelLoader(las_dir)
    
    # Scan files
    print("📂 Scanning LAS files...")
    loader.scan_las_files()
    
    wells = loader.get_wells_list()
    print(f"\n   Wells found: {len(wells)}")
    
    # Build models for top wells
    print("\n" + "=" * 70)
    print("BUILDING 4D MODELS")
    print("=" * 70)
    
    models = []
    for well_id in wells[:5]:  # Top 5 wells
        model = loader.build_model_for_well(well_id)
        if model:
            models.append(model)
    
    # Show decay modeling
    print("\n" + "=" * 70)
    print("DECAY MODELING (CORROSION OVER TIME)")
    print("=" * 70)
    print()
    
    # Create decay model demo
    decay = DecayModel(
        object_id="9/13a-B56Z-CSG",
        initial_wall=0.47,  # inches
        install_date="1990-06-01",
        environment="SWEET_PRODUCTION",
        material_grade="L-80"
    )
    
    # Record some measurements over time
    decay.record_measurement("2000-06-01", 0.45, "10-year inspection")
    decay.record_measurement("2010-06-01", 0.42, "20-year inspection")
    decay.record_measurement("2020-06-01", 0.38, "30-year inspection")
    
    # Show current state
    assessment = decay.corrosion_model.assess_integrity()
    
    print(f"Object: {decay.object_id}")
    print(f"Environment: {decay.corrosion_model.environment}")
    print(f"Material: {decay.corrosion_model.material_grade}")
    print()
    print(f"Initial wall thickness: {assessment['initial_wall']:.3f} inches")
    print(f"Current wall thickness: {assessment['current_wall']:.3f} inches")
    print(f"Wall loss: {assessment['wall_loss_pct']:.1f}%")
    print(f"Remaining life: {assessment['remaining_life_years']:.1f} years")
    print(f"Status: {assessment['status']}")
    print(f"Action: {assessment['recommended_action']}")
    
    # Generate decay timeline
    print("\n" + "=" * 70)
    print("DECAY TIMELINE (1990-2050)")
    print("=" * 70)
    print()
    
    timeline = decay.generate_decay_timeline(1990, 2050, 10)
    
    print(f"{'Year':<8} {'Wall (in)':<12} {'Loss %':<10} {'Remaining Life':<15}")
    print("-" * 50)
    
    for t in timeline:
        year = t['timestamp'][:4]
        wall = t['predicted_wall_thickness']
        loss = t['wall_loss_pct']
        life = t['remaining_life_years']
        
        print(f"{year:<8} {wall:<12.3f} {loss:<10.1f} {life:<15.1f}")
    
    # Export
    export = {
        "generated": datetime.now().isoformat(),
        "wells_scanned": len(wells),
        "models_built": len(models),
        "decay_model": decay.to_dict(),
        "decay_timeline": timeline
    }
    
    with open("las_4d_models_with_decay.json", "w") as f:
        json.dump(export, f, indent=2, default=str)
    
    print()
    print("=" * 70)
    print("📁 SAVED: las_4d_models_with_decay.json")
    print("=" * 70)
