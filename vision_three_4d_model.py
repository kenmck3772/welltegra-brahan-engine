#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              VISION THREE 4D WELBORE MODEL                                   ║
║                                                                               ║
║  Purpose: Complete 4D wellbore model for Vision Three integration            ║
║  Export: JSON format ready for 3D visualization                             ║
║                                                                               ║
║  John's Requirements:                                                         ║
║  - Virtual LEGO (WellboreObject with OD, ID, Length, Top MD)                 ║
║  - Parents and Children (component relationships)                            ║
║  - Key dates recorded (lifecycle states)                                      ║
║  - Spine (well trajectory/profile)                                           ║
║  - Time slider (4D state changes)                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# ==============================================================================
# ENUMS
# ==============================================================================

class LifecycleState(Enum):
    DESIGNED = "as designed"
    BUILT = "as built"
    INTERVENED = "as intervened"
    P_AND_A = "as to be P&A"
    PLUGGED = "as plugged"
    ABANDONED = "as abandoned"
    DECAYED = "as decayed"

class ComponentType(Enum):
    CASING = "CASING"
    TUBING = "TUBING"
    PACKER = "PACKER"
    PLUG = "PLUG"
    NIPPLE = "NIPPLE"
    SLEEVE = "SLEEVE"
    DHSV = "DHSV"
    SCSSV = "SCSSV"
    GLV = "GLV"
    CEMENT = "CEMENT"
    PERFORATION = "PERFORATION"
    BRIDGE_PLUG = "BRIDGE_PLUG"
    SSSV = "SSSV"
    TUBING_HANGER = "TUBING_HANGER"
    WELLHEAD = "WELLHEAD"
    INTERVENTION_STRING = "INTERVENTION_STRING"

# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class TrajectoryPoint:
    """Single point on the well spine (trajectory)"""
    md: float          # Measured Depth (ft)
    tvd: float         # True Vertical Depth (ft)
    inclination: float # Degrees from vertical
    azimuth: float     # Degrees from North
    x_offset: float = 0.0  # X offset from surface location (ft)
    y_offset: float = 0.0  # Y offset from surface location (ft)
    
    def to_3d_coords(self, surface_x: float = 0, surface_y: float = 0) -> Tuple[float, float, float]:
        """Convert to 3D coordinates (X, Y, Z)"""
        # Z = -TVD (depth below surface)
        z = -self.tvd
        
        # X, Y based on horizontal displacement
        horiz_disp = self.md * math.sin(math.radians(self.inclination))
        x = surface_x + horiz_disp * math.sin(math.radians(self.azimuth))
        y = surface_y + horiz_disp * math.cos(math.radians(self.azimuth))
        
        return (x, y, z)

@dataclass
class LifecycleEvent:
    """A state change in the component's life"""
    timestamp: str
    state: str
    operation: str
    source_document: str
    notes: str = ""

@dataclass
class WellboreObject4D:
    """
    Virtual LEGO piece - John's specification
    
    "Objects need a spine (well profile) and attributes of 
    Max OD, Min ID, Make-up length, Top MD … think virtual LEGO"
    """
    # Identity
    object_id: str
    component_type: str
    serial_number: str = ""
    
    # Geometry (John's "Virtual LEGO" requirements)
    max_od: float = 0.0      # Outer diameter (inches)
    min_id: float = 0.0      # Inner diameter (inches)
    makeup_length: float = 0.0  # Length (ft)
    top_md: float = 0.0      # Top measured depth (ft)
    bottom_md: float = 0.0   # Bottom measured depth (ft)
    
    # Position in 3D space (calculated from spine)
    top_x: float = 0.0
    top_y: float = 0.0
    top_z: float = 0.0
    bottom_x: float = 0.0
    bottom_y: float = 0.0
    bottom_z: float = 0.0
    
    # Relationships (John's "parents and children")
    parent_id: str = ""
    children_ids: List[str] = field(default_factory=list)
    
    # Lifecycle (John's "key dates recorded")
    lifecycle: List[LifecycleEvent] = field(default_factory=list)
    current_state: str = "DESIGNED"
    
    # Material properties
    material: str = "STEEL"
    weight_ppf: float = 0.0
    grade: str = ""
    
    # 3D visualization
    color: str = "#4A90D9"
    opacity: float = 1.0
    visible: bool = True
    
    def add_lifecycle_event(self, 
                            timestamp: str, 
                            state: str, 
                            operation: str,
                            source: str = "",
                            notes: str = ""):
        """Add a lifecycle event (for time slider)"""
        event = LifecycleEvent(
            timestamp=timestamp,
            state=state,
            operation=operation,
            source_document=source,
            notes=notes
        )
        self.lifecycle.append(event)
        self.current_state = state
    
    def get_state_at_time(self, timestamp: str) -> str:
        """Get the state of this object at a specific time (time slider)"""
        state = "DESIGNED"
        for event in self.lifecycle:
            if event.timestamp <= timestamp:
                state = event.state
        return state
    
    def to_vision_three_dict(self) -> Dict:
        """Export in Vision Three format"""
        return {
            "objectId": self.object_id,
            "type": self.component_type,
            "serialNumber": self.serial_number,
            "geometry": {
                "maxOD": self.max_od,
                "minID": self.min_id,
                "length": self.makeup_length,
                "topMD": self.top_md,
                "bottomMD": self.bottom_md
            },
            "position3D": {
                "top": {"x": self.top_x, "y": self.top_y, "z": self.top_z},
                "bottom": {"x": self.bottom_x, "y": self.bottom_y, "z": self.bottom_z}
            },
            "relationships": {
                "parentId": self.parent_id,
                "childrenIds": self.children_ids
            },
            "lifecycle": [
                {
                    "timestamp": e.timestamp,
                    "state": e.state,
                    "operation": e.operation,
                    "source": e.source_document
                } for e in sorted(self.lifecycle, key=lambda x: x.timestamp)
            ],
            "currentState": self.current_state,
            "material": {
                "type": self.material,
                "weightPPF": self.weight_ppf,
                "grade": self.grade
            },
            "visualization": {
                "color": self.color,
                "opacity": self.opacity,
                "visible": self.visible
            }
        }

@dataclass
class InterventionString:
    """
    Intervention string (DP, CT, Wireline) for virtual subsurface operations
    """
    string_id: str
    string_type: str  # "DRILL_PIPE", "COILED_TUBING", "WIRELINE"
    diameter: float
    length: float
    top_md: float
    components: List[Dict] = field(default_factory=list)
    
    def to_vision_three_dict(self) -> Dict:
        return {
            "stringId": self.string_id,
            "type": self.string_type,
            "diameter": self.diameter,
            "length": self.length,
            "topMD": self.top_md,
            "components": self.components
        }

# ==============================================================================
# WELL SPINE (TRAJECTORY)
# ==============================================================================

class WellSpine:
    """
    The spine of the well - trajectory/profile
    John's requirement: "objects need a spine (well profile)"
    """
    
    def __init__(self, well_id: str):
        self.well_id = well_id
        self.trajectory: List[TrajectoryPoint] = []
        self.surface_x = 0.0
        self.surface_y = 0.0
        self.kickoff_md = 0.0
        self.max_inclination = 0.0
        self.total_depth = 0.0
    
    def add_trajectory_point(self, 
                             md: float, 
                             tvd: float, 
                             inclination: float, 
                             azimuth: float):
        """Add a trajectory point"""
        point = TrajectoryPoint(
            md=md,
            tvd=tvd,
            inclination=inclination,
            azimuth=azimuth
        )
        self.trajectory.append(point)
        
        # Update max values
        if inclination > self.max_inclination:
            self.max_inclination = inclination
        if md > self.total_depth:
            self.total_depth = md
    
    def get_point_at_md(self, target_md: float) -> Optional[TrajectoryPoint]:
        """Interpolate trajectory at specific MD"""
        if not self.trajectory:
            return None
        
        # Find bracketing points
        for i in range(len(self.trajectory) - 1):
            p1 = self.trajectory[i]
            p2 = self.trajectory[i + 1]
            
            if p1.md <= target_md <= p2.md:
                # Linear interpolation
                ratio = (target_md - p1.md) / (p2.md - p1.md) if p2.md != p1.md else 0
                
                return TrajectoryPoint(
                    md=target_md,
                    tvd=p1.tvd + ratio * (p2.tvd - p1.tvd),
                    inclination=p1.inclination + ratio * (p2.inclination - p1.inclination),
                    azimuth=p1.azimuth + ratio * (p2.azimuth - p1.azimuth)
                )
        
        # Return last point if beyond trajectory
        if target_md > self.trajectory[-1].md:
            return self.trajectory[-1]
        
        return self.trajectory[0] if self.trajectory else None
    
    def generate_simple_trajectory(self, 
                                    total_depth: float, 
                                    kickoff_depth: float,
                                    max_inclination: float,
                                    azimuth: float = 0.0):
        """Generate a simple trajectory for wells without survey data"""
        
        self.kickoff_md = kickoff_depth
        self.max_inclination = max_inclination
        
        # Build from surface
        self.add_trajectory_point(0, 0, 0, azimuth)
        
        # To kickoff
        if kickoff_depth > 0:
            self.add_trajectory_point(kickoff_depth, kickoff_depth, 0, azimuth)
        
        # Build angle section
        if max_inclination > 0:
            # Build angle over ~1000 ft
            build_rate = max_inclination / 1000
            current_md = kickoff_depth
            current_inc = 0
            build_length = 1000
            
            for i in range(10):
                current_md += build_length / 10
                current_inc = min(max_inclination, current_inc + max_inclination / 10)
                current_tv = kickoff_depth + (current_md - kickoff_depth) * math.cos(math.radians(current_inc))
                
                self.add_trajectory_point(current_md, current_tv, current_inc, azimuth)
        
        # To TD
        self.add_trajectory_point(total_depth, 
                                   kickoff_depth + (total_depth - kickoff_depth - 1000) * math.cos(math.radians(max_inclination)),
                                   max_inclination, azimuth)
    
    def to_vision_three_dict(self) -> Dict:
        """Export spine for Vision Three"""
        return {
            "wellId": self.well_id,
            "surfaceLocation": {
                "x": self.surface_x,
                "y": self.surface_y
            },
            "trajectory": [
                {
                    "md": p.md,
                    "tvd": p.tvd,
                    "inclination": p.inclination,
                    "azimuth": p.azimuth,
                    "coords3D": {
                        "x": p.to_3d_coords(self.surface_x, self.surface_y)[0],
                        "y": p.to_3d_coords(self.surface_x, self.surface_y)[1],
                        "z": p.to_3d_coords(self.surface_x, self.surface_y)[2]
                    }
                } for p in self.trajectory
            ],
            "maxInclination": self.max_inclination,
            "totalDepth": self.total_depth
        }

# ==============================================================================
# 4D WELLBORE MODEL
# ==============================================================================

class WellboreModel4D:
    """
    Complete 4D wellbore model
    Integrates spine, objects, and time slider
    """
    
    def __init__(self, well_id: str):
        self.well_id = well_id
        self.spine = WellSpine(well_id)
        self.objects: Dict[str, WellboreObject4D] = {}
        self.intervention_strings: List[InterventionString] = []
        self.created_at = datetime.now().isoformat()
    
    def add_object(self, obj: WellboreObject4D):
        """Add a wellbore object (virtual LEGO piece)"""
        # Calculate 3D position from spine
        top_point = self.spine.get_point_at_md(obj.top_md)
        bottom_point = self.spine.get_point_at_md(obj.bottom_md)
        
        if top_point:
            coords = top_point.to_3d_coords()
            obj.top_x, obj.top_y, obj.top_z = coords
        
        if bottom_point:
            coords = bottom_point.to_3d_coords()
            obj.bottom_x, obj.bottom_y, obj.bottom_z = coords
        
        self.objects[obj.object_id] = obj
    
    def set_parent_child(self, child_id: str, parent_id: str):
        """Set parent-child relationship"""
        if child_id in self.objects and parent_id in self.objects:
            self.objects[child_id].parent_id = parent_id
            if child_id not in self.objects[parent_id].children_ids:
                self.objects[parent_id].children_ids.append(child_id)
    
    def get_model_at_time(self, timestamp: str) -> Dict:
        """Get complete model state at specific time (time slider)"""
        return {
            "wellId": self.well_id,
            "timestamp": timestamp,
            "spine": self.spine.to_vision_three_dict(),
            "objects": [
                {
                    **obj.to_vision_three_dict(),
                    "stateAtTime": obj.get_state_at_time(timestamp)
                } for obj in self.objects.values()
            ]
        }
    
    def to_vision_three_export(self) -> Dict:
        """Full export for Vision Three integration"""
        return {
            "format": "WELLTEGRA_4D_V1",
            "version": "3.0",
            "exportedAt": datetime.now().isoformat(),
            "well": {
                "wellId": self.well_id,
                "spine": self.spine.to_vision_three_dict()
            },
            "objects": [obj.to_vision_three_dict() for obj in self.objects.values()],
            "interventionStrings": [s.to_vision_three_dict() for s in self.intervention_strings],
            "timeSlider": {
                "minTime": min(
                    (e.timestamp for obj in self.objects.values() for e in obj.lifecycle),
                    default="1900-01-01"
                ),
                "maxTime": max(
                    (e.timestamp for obj in self.objects.values() for e in obj.lifecycle),
                    default=datetime.now().isoformat()
                ),
                "states": [s.value for s in LifecycleState]
            }
        }

# ==============================================================================
# DATA LOADER FROM LAS FILES
# ==============================================================================

class LasDataLoader:
    """Load actual data from LAS files into 4D model"""
    
    def __init__(self, las_dir: str):
        self.las_dir = las_dir
    
    def load_well_data(self, well_id: str) -> Dict:
        """Load all available data for a well"""
        # This would parse actual LAS files
        # For now, return structure
        return {
            "well_id": well_id,
            "trajectory": [],
            "components": [],
            "interventions": []
        }

# ==============================================================================
# DEMO / TEST
# ==============================================================================

def create_demo_model() -> WellboreModel4D:
    """Create a demo 4D model with all John's requirements"""
    
    # Create model
    model = WellboreModel4D(well_id="9/13a-B56Z")
    
    # Create spine (trajectory)
    model.spine.generate_simple_trajectory(
        total_depth=12000,
        kickoff_depth=5000,
        max_inclination=45,
        azimuth=135
    )
    
    # Create objects (Virtual LEGO)
    
    # 1. Surface Casing
    surface_casing = WellboreObject4D(
        object_id="CSG-SURFACE",
        component_type=ComponentType.CASING.value,
        max_od=20.0,
        min_id=18.5,
        makeup_length=1000,
        top_md=0,
        bottom_md=2000,
        material="STEEL",
        grade="K-55",
        weight_ppf=94.0,
        color="#8B4513"
    )
    surface_casing.add_lifecycle_event(
        "1990-05-15T10:00:00Z",
        LifecycleState.BUILT.value,
        "Run and cemented surface casing",
        "Drilling Report 1990-05-15"
    )
    model.add_object(surface_casing)
    
    # 2. Production Casing
    prod_casing = WellboreObject4D(
        object_id="CSG-PROD",
        component_type=ComponentType.CASING.value,
        max_od=9.625,
        min_id=8.68,
        makeup_length=12000,
        top_md=0,
        bottom_md=12000,
        material="STEEL",
        grade="L-80",
        weight_ppf=47.0,
        color="#CD853F"
    )
    prod_casing.add_lifecycle_event(
        "1990-06-01T08:00:00Z",
        LifecycleState.BUILT.value,
        "Run and cemented production casing",
        "Drilling Report 1990-06-01"
    )
    prod_casing.add_lifecycle_event(
        "1990-06-15T12:00:00Z",
        LifecycleState.INTERVENED.value,
        "Perforations at 10500-10600 ft",
        "Completion Report 1990-06-15"
    )
    prod_casing.add_lifecycle_event(
        "2024-01-10T14:00:00Z",
        LifecycleState.P_AND_A.value,
        "P&A program initiated",
        "P&A Program 2024"
    )
    model.add_object(prod_casing)
    
    # Set parent-child
    model.set_parent_child("CSG-PROD", "CSG-SURFACE")
    
    # 3. Tubing
    tubing = WellboreObject4D(
        object_id="TUB-001",
        component_type=ComponentType.TUBING.value,
        max_od=3.5,
        min_id=2.992,
        makeup_length=10500,
        top_md=500,
        bottom_md=11000,
        material="STEEL",
        grade="L-80",
        weight_ppf=9.2,
        color="#4169E1"
    )
    tubing.add_lifecycle_event(
        "1990-06-20T10:00:00Z",
        LifecycleState.BUILT.value,
        "Run tubing string",
        "Completion Report 1990-06-20"
    )
    tubing.add_lifecycle_event(
        "2010-08-05T15:00:00Z",
        LifecycleState.INTERVENED.value,
        "Workover - tubing replaced",
        "Workover Report 2010-08-05"
    )
    model.add_object(tubing)
    model.set_parent_child("TUB-001", "CSG-PROD")
    
    # 4. Packer
    packer = WellboreObject4D(
        object_id="PKR-001",
        component_type=ComponentType.PACKER.value,
        serial_number="PKR-90-12345",
        max_od=4.5,
        min_id=2.5,
        makeup_length=10,
        top_md=10800,
        bottom_md=10810,
        material="STEEL",
        grade="L-80",
        color="#2E8B57"
    )
    packer.add_lifecycle_event(
        "1990-06-20T14:00:00Z",
        LifecycleState.BUILT.value,
        "Set production packer",
        "Completion Report 1990-06-20"
    )
    model.add_object(packer)
    model.set_parent_child("PKR-001", "TUB-001")
    
    # 5. DHSV
    dhsv = WellboreObject4D(
        object_id="DHSV-001",
        component_type=ComponentType.DHSV.value,
        serial_number="DHSV-90-67890",
        max_od=3.5,
        min_id=2.75,
        makeup_length=8,
        top_md=10500,
        bottom_md=10508,
        material="STEEL",
        grade="INCONEL",
        color="#DC143C"
    )
    dhsv.add_lifecycle_event(
        "1990-06-20T15:00:00Z",
        LifecycleState.BUILT.value,
        "Installed DHSV",
        "Completion Report 1990-06-20"
    )
    dhsv.add_lifecycle_event(
        "2010-08-06T10:00:00Z",
        LifecycleState.INTERVENED.value,
        "DHSV replaced during workover",
        "Workover Report 2010-08-06"
    )
    model.add_object(dhsv)
    model.set_parent_child("DHSV-001", "TUB-001")
    
    # 6. Cement Plug (for P&A)
    cement_plug = WellboreObject4D(
        object_id="PLUG-001",
        component_type=ComponentType.PLUG.value,
        max_od=8.68,  # Same as casing ID
        min_id=0,
        makeup_length=500,
        top_md=8000,
        bottom_md=8500,
        material="CEMENT",
        grade="Class G",
        color="#808080",
        opacity=0.7
    )
    cement_plug.add_lifecycle_event(
        "2024-01-15T12:00:00Z",
        LifecycleState.PLUGGED.value,
        "Set primary cement plug",
        "P&A Report 2024-01-15"
    )
    model.add_object(cement_plug)
    model.set_parent_child("PLUG-001", "CSG-PROD")
    
    # Add intervention string (wireline)
    wireline = InterventionString(
        string_id="INT-WL-2024-001",
        string_type="WIRELINE",
        diameter=0.125,
        length=11000,
        top_md=0,
        components=[
            {"type": "SINKER_BAR", "length": 10},
            {"type": "CCL", "length": 5},
            {"type": "GR", "length": 8},
            {"type": "PRESSURE_GAUGE", "length": 6}
        ]
    )
    model.intervention_strings.append(wireline)
    
    return model

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("VISION THREE 4D WELBORE MODEL")
    print("=" * 70)
    print()
    
    print("John's Requirements Check:")
    print("   ✅ Virtual LEGO (OD, ID, Length, Top MD)")
    print("   ✅ Parents and Children relationships")
    print("   ✅ Key dates recorded (lifecycle)")
    print("   ✅ Spine (well trajectory)")
    print("   ✅ Time slider (get_state_at_time)")
    print("   ✅ Intervention strings")
    print()
    
    # Create demo model
    print("Building demo model...")
    model = create_demo_model()
    
    print(f"\n   Well: {model.well_id}")
    print(f"   Spine points: {len(model.spine.trajectory)}")
    print(f"   Objects: {len(model.objects)}")
    print(f"   Intervention strings: {len(model.intervention_strings)}")
    
    # Show objects
    print("\n" + "=" * 70)
    print("WELBORE OBJECTS (Virtual LEGO)")
    print("=" * 70)
    
    for obj_id, obj in model.objects.items():
        print(f"\n   📦 {obj_id}")
        print(f"      Type: {obj.component_type}")
        print(f"      Geometry: OD={obj.max_od}\", ID={obj.min_id}\", Length={obj.makeup_length}ft")
        print(f"      Position: Top MD={obj.top_md}ft, Bottom MD={obj.bottom_md}ft")
        print(f"      Parent: {obj.parent_id or 'None'}")
        print(f"      Children: {obj.children_ids or 'None'}")
        print(f"      Lifecycle events: {len(obj.lifecycle)}")
        
        for event in obj.lifecycle:
            print(f"         {event.timestamp[:10]}: {event.state}")
    
    # Show relationships
    print("\n" + "=" * 70)
    print("PARENT-CHILD RELATIONSHIPS")
    print("=" * 70)
    
    for obj_id, obj in model.objects.items():
        if obj.children_ids:
            print(f"   {obj_id} → PARENT OF → {obj.children_ids}")
    
    # Show spine
    print("\n" + "=" * 70)
    print("WEL SPINE (TRAJECTORY)")
    print("=" * 70)
    
    print(f"\n   Total Depth: {model.spine.total_depth} ft MD")
    print(f"   Max Inclination: {model.spine.max_inclination}°")
    print(f"   Trajectory points: {len(model.spine.trajectory)}")
    
    print("\n   First 5 points:")
    for p in model.spine.trajectory[:5]:
        print(f"      MD={p.md:.0f}ft, TVD={p.tvd:.0f}ft, Inc={p.inclination:.1f}°")
    
    # Time slider demo
    print("\n" + "=" * 70)
    print("TIME SLIDER DEMO")
    print("=" * 70)
    
    test_times = [
        "1990-01-01",  # Before built
        "1990-06-20",  # During completion
        "2010-08-05",  # During workover
        "2024-01-15",  # During P&A
    ]
    
    for t in test_times:
        state = model.objects["TUB-001"].get_state_at_time(t)
        print(f"   {t}: Tubing state = {state}")
    
    # Export for Vision Three
    export = model.to_vision_three_export()
    
    with open("vision_three_4d_export.json", "w") as f:
        json.dump(export, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("📁 EXPORTED: vision_three_4d_export.json")
    print("=" * 70)
    
    print("\n   Format: WELLTEGRA_4D_V1")
    print("   Ready for: Vision Three integration")
    print()
