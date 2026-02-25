#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              DOWNTIME & RELIABILITY SCORECARD ENGINE                         ║
║                        WellTegra v3.0                                        ║
║                                                                               ║
║  Purpose: Track and score service companies, equipment, and human factors     ║
║  Mission: Find recurring mistakes and weak links quickly                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import uuid

# ==============================================================================
# ENUMS
# ==============================================================================

class OperationType(Enum):
    WIRELINE = "WIRELINE"
    SLICKLINE = "SLICKLINE"
    ELINE = "E-LINE"
    COILED_TUBING = "COILED_TUBING"
    DRILLING = "DRILLING"
    WORKOVER = "WORKOVER"
    ABANDONMENT = "ABANDONMENT"
    WELL_TEST = "WELL_TEST"
    CEMENTING = "CEMENTING"

class FailureCause(Enum):
    HUMAN_ERROR = "HUMAN_ERROR"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"
    LOGISTICS = "LOGISTICS"
    NON_COMPLIANT_ON_ARRIVAL = "NON_COMPLIANT_ON_ARRIVAL"
    PLANNING_OR_PROCEDURE = "PLANNING_OR_PROCEDURE"
    WEATHER = "WEATHER"
    PLATFORM_ISSUE = "PLATFORM_ISSUE"

class BarrierType(Enum):
    SINGLE_BLOCK = "SINGLE_BLOCK"
    DOUBLE_BLOCK = "DOUBLE_BLOCK"
    DOUBLE_BLOCK_AND_BLEED = "DOUBLE_BLOCK_AND_BLEED"
    CONSTANT_BLEED = "CONSTANT_BLEED"

class EngagementType(Enum):
    OPERATOR_CONTRACT = "OPERATOR_CONTRACT"
    MULTI_SKILLED_CONTRACT = "MULTI_SKILLED_CONTRACT"
    AD_HOC = "AD_HOC"
    AGENCY = "AGENCY"

class Severity(Enum):
    MINOR = "MINOR"
    SERIOUS = "SERIOUS"
    MAJOR = "MAJOR"

# ==============================================================================
# DATA CLASSES - Intervention Run Record
# ==============================================================================

@dataclass
class DowntimeEvent:
    """A single downtime event during intervention"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp_start: str = ""
    timestamp_end: str = ""
    duration_minutes: float = 0.0
    linked_equipment_id: str = ""
    linked_company: str = ""
    failure_cause: str = ""
    description: str = ""
    equipment_serial: str = ""
    vessel_manifest_ref: str = ""
    
@dataclass
class BarrierTest:
    """Barrier test between runs"""
    barrier_id: str = ""
    test_type: str = ""
    test_duration_min: float = 0.0
    result: str = ""
    comments: str = ""

@dataclass
class EquipmentCertification:
    """Equipment certification status"""
    equipment_id: str = ""
    equipment_type: str = ""
    cert_status: str = ""
    cert_ref: str = ""
    last_inspection_date: str = ""
    non_conformances: List[str] = field(default_factory=list)

@dataclass
class PersonnelRole:
    """Personnel competence record"""
    name: str = ""
    company: str = ""
    role: str = ""
    competence_verified: bool = False
    competence_ref: str = ""
    expiry_date: str = ""
    notes: str = ""

@dataclass
class SIMOPSConflict:
    """SIMOPS conflict record"""
    conflict_id: str = ""
    operations_in_conflict: List[str] = field(default_factory=list)
    conflict_type: str = ""
    description: str = ""
    mitigations: List[str] = field(default_factory=list)

@dataclass
class InterventionRunRecord:
    """
    Complete Intervention Run Record
    Encodes all data for a single intervention operation
    """
    # Run Identity
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    well_id: str = ""
    uwi: str = ""
    operation_type: str = ""
    date_start: str = ""
    date_end: str = ""
    
    # People & Companies
    service_companies: List[Dict] = field(default_factory=list)
    contractors: List[Dict] = field(default_factory=list)
    operator_team: Dict = field(default_factory=dict)
    
    # Equipment
    wireline_units: List[Dict] = field(default_factory=list)
    pressure_control_equipment: List[Dict] = field(default_factory=list)
    powerpacks_panels: List[Dict] = field(default_factory=list)
    lifting_equipment: List[Dict] = field(default_factory=list)
    
    # Rig-up Constraints
    space_constraints: str = ""
    access_constraints: str = ""
    layout_notes: str = ""
    
    # Barriers
    barriers_prior_to_rigup: List[Dict] = field(default_factory=list)
    barrier_tests: List[BarrierTest] = field(default_factory=list)
    double_block_type: str = ""
    double_block_in_use: bool = False
    
    # Downtime Events
    downtime_events: List[DowntimeEvent] = field(default_factory=list)
    
    # Safety & Compliance
    arrival_safety_checks: Dict = field(default_factory=dict)
    documentation_compliance: Dict = field(default_factory=dict)
    equipment_certification: Dict = field(default_factory=dict)
    personnel_competence: Dict = field(default_factory=dict)
    safety_communications: Dict = field(default_factory=dict)
    pressure_testing_rigup: Dict = field(default_factory=dict)
    bop_testing: Dict = field(default_factory=dict)
    
    # SIMOPS
    simops_active: bool = False
    simops_operations: List[Dict] = field(default_factory=list)
    simops_conflicts: List[SIMOPSConflict] = field(default_factory=list)
    
    # Emergency & Incidents
    incidents: List[Dict] = field(default_factory=list)
    waiting_events: List[Dict] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

# ==============================================================================
# SCORECARD CALCULATOR
# ==============================================================================

class DowntimeScorecardEngine:
    """
    Calculates per-company and per-equipment reliability scores
    from Intervention Run Records
    """
    
    def __init__(self):
        self.runs: List[InterventionRunRecord] = []
        self.company_stats = defaultdict(lambda: {
            "total_runs": 0,
            "downtime_events_count": 0,
            "downtime_minutes_total": 0,
            "events_by_cause": defaultdict(int),
            "non_compliant_on_arrival_count": 0,
            "equipment_failures": 0,
            "human_errors": 0,
            "incidents_count": 0,
            "barrier_test_failures": 0,
            "simops_conflicts": 0
        })
        
        self.equipment_stats = defaultdict(lambda: {
            "times_used": 0,
            "failures": 0,
            "downtime_caused_minutes": 0,
            "non_conformances": 0,
            "companies_involved": set()
        })
    
    def add_run(self, run: InterventionRunRecord):
        """Add a run record to the engine"""
        self.runs.append(run)
        self._process_run(run)
    
    def _process_run(self, run: InterventionRunRecord):
        """Process a run and update statistics"""
        
        # Process companies
        companies_involved = set()
        
        for company in run.service_companies:
            name = company.get("name", "UNKNOWN")
            companies_involved.add(name)
            self.company_stats[name]["total_runs"] += 1
        
        for contractor in run.contractors:
            name = contractor.get("name", "UNKNOWN")
            companies_involved.add(name)
        
        # Process downtime events
        for event in run.downtime_events:
            company = event.linked_company
            self.company_stats[company]["downtime_events_count"] += 1
            self.company_stats[company]["downtime_minutes_total"] += event.duration_minutes
            self.company_stats[company]["events_by_cause"][event.failure_cause] += 1
            
            if event.failure_cause == "NON_COMPLIANT_ON_ARRIVAL":
                self.company_stats[company]["non_compliant_on_arrival_count"] += 1
            elif event.failure_cause == "EQUIPMENT_FAILURE":
                self.company_stats[company]["equipment_failures"] += 1
            elif event.failure_cause == "HUMAN_ERROR":
                self.company_stats[company]["human_errors"] += 1
            
            # Track equipment
            if event.linked_equipment_id:
                self.equipment_stats[event.linked_equipment_id]["times_used"] += 1
                self.equipment_stats[event.linked_equipment_id]["failures"] += 1
                self.equipment_stats[event.linked_equipment_id]["downtime_caused_minutes"] += event.duration_minutes
                self.equipment_stats[event.linked_equipment_id]["companies_involved"].add(company)
        
        # Process barrier tests
        for test in run.barrier_tests:
            if test.result == "FAIL":
                for company in companies_involved:
                    self.company_stats[company]["barrier_test_failures"] += 1
        
        # Process SIMOPS conflicts
        for conflict in run.simops_conflicts:
            for company in companies_involved:
                self.company_stats[company]["simops_conflicts"] += 1
        
        # Process incidents
        for incident in run.incidents:
            for company in companies_involved:
                self.company_stats[company]["incidents_count"] += 1
    
    def calculate_company_score(self, company_name: str) -> Dict:
        """Calculate reliability score for a company"""
        stats = self.company_stats[company_name]
        
        if stats["total_runs"] == 0:
            return {"company": company_name, "score": None, "status": "NO_DATA"}
        
        # Calculate scores
        downtime_score = self._calculate_downtime_score(stats)
        safety_score = self._calculate_safety_score(stats)
        reliability_score = (downtime_score + safety_score) / 2
        
        # Determine trend (simplified - would need historical data)
        trend = "STABLE"
        if stats["incidents_count"] > 0 or stats["human_errors"] > 2:
            trend = "DEGRADING"
        elif stats["non_compliant_on_arrival_count"] == 0 and stats["incidents_count"] == 0:
            trend = "IMPROVING"
        
        return {
            "company": company_name,
            "total_runs": stats["total_runs"],
            "downtime_events": stats["downtime_events_count"],
            "downtime_minutes": stats["downtime_minutes_total"],
            "downtime_score": round(downtime_score, 1),
            "safety_score": round(safety_score, 1),
            "reliability_score": round(reliability_score, 1),
            "reliability_trend": trend,
            "events_by_cause": dict(stats["events_by_cause"]),
            "non_compliant_arrivals": stats["non_compliant_on_arrival_count"],
            "human_errors": stats["human_errors"],
            "equipment_failures": stats["equipment_failures"],
            "incidents": stats["incidents_count"],
            "barrier_test_failures": stats["barrier_test_failures"],
            "simops_conflicts": stats["simops_conflicts"],
            "barrier_discipline_flag": stats["barrier_test_failures"] > 2 or stats["simops_conflicts"] > 1
        }
    
    def _calculate_downtime_score(self, stats: Dict) -> float:
        """Calculate downtime score (0-100, higher is better)"""
        if stats["total_runs"] == 0:
            return 0.0
        
        # Average downtime per run
        avg_downtime = stats["downtime_minutes_total"] / stats["total_runs"]
        
        # Score calculation (less downtime = higher score)
        # 0 min avg = 100, 120 min avg = 50, 240+ min avg = 0
        if avg_downtime == 0:
            return 100.0
        elif avg_downtime >= 240:
            return 0.0
        else:
            return max(0, 100 - (avg_downtime / 2.4))
    
    def _calculate_safety_score(self, stats: Dict) -> float:
        """Calculate safety compliance score (0-100, higher is better)"""
        score = 100.0
        
        # Deduct for issues
        score -= stats["non_compliant_on_arrival_count"] * 15
        score -= stats["human_errors"] * 10
        score -= stats["incidents_count"] * 25
        score -= stats["barrier_test_failures"] * 10
        score -= stats["simops_conflicts"] * 5
        
        return max(0, min(100, score))
    
    def calculate_equipment_score(self, equipment_id: str) -> Dict:
        """Calculate reliability score for specific equipment"""
        stats = self.equipment_stats[equipment_id]
        
        if stats["times_used"] == 0:
            return {"equipment_id": equipment_id, "score": None, "status": "NO_DATA"}
        
        # Failure rate
        failure_rate = stats["failures"] / stats["times_used"]
        
        # Score (higher = more reliable)
        reliability_score = max(0, 100 * (1 - failure_rate))
        
        # Flag for review
        review_flag = False
        review_reasons = []
        
        if stats["failures"] >= 3:
            review_flag = True
            review_reasons.append("Multiple failures")
        
        if stats["non_conformances"] >= 2:
            review_flag = True
            review_reasons.append("Multiple non-conformances")
        
        if failure_rate > 0.5:
            review_flag = True
            review_reasons.append("High failure rate")
        
        return {
            "equipment_id": equipment_id,
            "times_used": stats["times_used"],
            "failures": stats["failures"],
            "downtime_caused_minutes": stats["downtime_caused_minutes"],
            "failure_rate": round(failure_rate * 100, 1),
            "reliability_score": round(reliability_score, 1),
            "companies_involved": list(stats["companies_involved"]),
            "retire_repair_review_flag": review_flag,
            "review_reasons": review_reasons
        }
    
    def generate_full_scorecard(self) -> Dict:
        """Generate complete scorecard report"""
        
        company_scorecards = []
        for company in self.company_stats.keys():
            company_scorecards.append(self.calculate_company_score(company))
        
        equipment_scorecards = []
        for equipment in self.equipment_stats.keys():
            equipment_scorecards.append(self.calculate_equipment_score(equipment))
        
        # Sort by reliability score
        company_scorecards.sort(key=lambda x: x.get("reliability_score") or 0, reverse=True)
        equipment_scorecards.sort(key=lambda x: x.get("reliability_score") or 0, reverse=True)
        
        # Summary stats
        total_downtime = sum(s["downtime_minutes_total"] for s in self.company_stats.values())
        total_incidents = sum(s["incidents_count"] for s in self.company_stats.values())
        
        return {
            "generated_at": datetime.now().isoformat(),
            "total_runs_analyzed": len(self.runs),
            "total_companies": len(self.company_stats),
            "total_equipment": len(self.equipment_stats),
            "total_downtime_minutes": total_downtime,
            "total_incidents": total_incidents,
            "company_scorecards": company_scorecards,
            "equipment_scorecards": equipment_scorecards,
            "worst_performers": {
                "companies": [c for c in company_scorecards if c.get("reliability_score", 0) < 50][:5],
                "equipment": [e for e in equipment_scorecards if e.get("reliability_score", 0) < 50][:5]
            },
            "best_performers": {
                "companies": [c for c in company_scorecards if c.get("reliability_score", 0) >= 80][:5],
                "equipment": [e for e in equipment_scorecards if e.get("reliability_score", 0) >= 80][:5]
            }
        }

# ==============================================================================
# DEMO / TEST
# ==============================================================================

def create_demo_run() -> InterventionRunRecord:
    """Create a demo intervention run for testing"""
    
    run = InterventionRunRecord(
        run_id="DEMO-001",
        well_id="Stella_3_30",
        uwi="UKCS-03-30-STELLA-001",
        operation_type="WIRELINE",
        date_start="2026-03-01T06:00:00Z",
        date_end="2026-03-01T20:00:00Z",
        
        service_companies=[
            {"name": "WirelineCo A", "role": "WIRELINE_SERVICE"},
            {"name": "LiftingCo B", "role": "LIFTING"}
        ],
        
        contractors=[
            {"name": "Contractor X", "role": "PCE_MAINTENANCE"}
        ],
        
        downtime_events=[
            DowntimeEvent(
                timestamp_start="2026-03-01T11:30:00Z",
                timestamp_end="2026-03-01T12:00:00Z",
                duration_minutes=30,
                linked_equipment_id="CRANE-01",
                linked_company="LiftingCo B",
                failure_cause="LOGISTICS",
                description="Waiting on crane availability due to overlapping CT lift"
            ),
            DowntimeEvent(
                timestamp_start="2026-03-01T16:00:00Z",
                timestamp_end="2026-03-01T18:00:00Z",
                duration_minutes=120,
                linked_equipment_id="PCE-STACK-01",
                linked_company="WirelineCo A",
                failure_cause="EQUIPMENT_FAILURE",
                description="PCE leak on first test; required re-greasing and retest"
            )
        ],
        
        double_block_type="DOUBLE_BLOCK_AND_BLEED",
        double_block_in_use=True,
        
        incidents=[
            {
                "incident_id": "INC-001",
                "datetime": "2026-03-01T16:10:00Z",
                "severity": "MINOR",
                "description": "PCE leak discovered during test",
                "job_stopped": True
            }
        ]
    )
    
    return run

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("DOWNTIME & RELIABILITY SCORECARD ENGINE")
    print("=" * 60)
    print()
    
    # Create engine
    engine = DowntimeScorecardEngine()
    
    # Add demo runs
    print("Adding demo intervention runs...")
    
    run1 = create_demo_run()
    engine.add_run(run1)
    
    # Add more demo runs with different scenarios
    run2 = InterventionRunRecord(
        run_id="DEMO-002",
        well_id="Stella_3_30",
        operation_type="WIRELINE",
        service_companies=[{"name": "WirelineCo A", "role": "WIRELINE_SERVICE"}],
        downtime_events=[
            DowntimeEvent(
                duration_minutes=45,
                linked_company="WirelineCo A",
                failure_cause="HUMAN_ERROR",
                description="Incorrect tool string assembled"
            )
        ]
    )
    engine.add_run(run2)
    
    run3 = InterventionRunRecord(
        run_id="DEMO-003",
        well_id="Other_Well",
        operation_type="COILED_TUBING",
        service_companies=[{"name": "CT_Services", "role": "CT_SERVICE"}],
        downtime_events=[
            DowntimeEvent(
                duration_minutes=180,
                linked_company="CT_Services",
                linked_equipment_id="CT-UNIT-05",
                failure_cause="NON_COMPLIANT_ON_ARRIVAL",
                description="CT unit arrived with leaking swivel"
            )
        ],
        incidents=[
            {"severity": "SERIOUS", "description": "Well control event"}
        ]
    )
    engine.add_run(run3)
    
    print(f"   {len(engine.runs)} runs added")
    print()
    
    # Generate scorecard
    print("Generating scorecard...")
    print()
    
    scorecard = engine.generate_full_scorecard()
    
    # Display results
    print("=" * 60)
    print("COMPANY SCORECARDS")
    print("=" * 60)
    print()
    
    for company in scorecard["company_scorecards"]:
        print(f"🏢 {company['company']}")
        print(f"   Runs: {company['total_runs']}")
        print(f"   Reliability Score: {company['reliability_score']}/100")
        print(f"   Downtime: {company['downtime_minutes']} min")
        print(f"   Trend: {company['reliability_trend']}")
        if company['barrier_discipline_flag']:
            print(f"   ⚠️  BARRIER DISCIPLINE FLAG")
        print()
    
    print("=" * 60)
    print("EQUIPMENT SCORECARDS")
    print("=" * 60)
    print()
    
    for equip in scorecard["equipment_scorecards"][:5]:
        print(f"🔧 {equip['equipment_id']}")
        print(f"   Times Used: {equip['times_used']}")
        print(f"   Failures: {equip['failures']}")
        print(f"   Reliability: {equip['reliability_score']}/100")
        if equip['retire_repair_review_flag']:
            print(f"   🚨 REVIEW REQUIRED: {equip['review_reasons']}")
        print()
    
    # Save
    with open("downtime_scorecard.json", "w") as f:
        json.dump(scorecard, f, indent=2, default=str)
    
    print("=" * 60)
    print("📁 SAVED: downtime_scorecard.json")
    print("=" * 60)
