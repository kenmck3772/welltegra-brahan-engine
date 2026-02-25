#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              WEATHER & KICK TRACKER                                          ║
║                        WellTegra v3.0                                        ║
║                                                                               ║
║  Features:                                                                    ║
║  - Weather conditions at tubing hanger landing                               ║
║  - Unrecorded kicks detection from pressure signatures                       ║
║  - Environmental correlation with operations                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import random

# ==============================================================================
# ENUMS
# ==============================================================================

class WeatherSeverity(Enum):
    CALM = "CALM"           # < 10 knots wind, no swell
    MODERATE = "MODERATE"   # 10-25 knots, moderate swell
    ROUGH = "ROUGH"         # 25-40 knots, heavy swell
    SEVERE = "SEVERE"       # > 40 knots, storm conditions

class KickType(Enum):
    SWAB = "SWAB"           # Swab kick during POOH
    SURGE = "SURGE"         # Surge kick during RIH
    INFLUX = "INFLUX"       # Formation influx
    LOST_RETURNS = "LOST_RETURNS"
    GAS_BUBBLE = "GAS_BUBBLE"
    WATER_FLOW = "WATER_FLOW"

class KickSeverity(Enum):
    MINOR = "MINOR"         # < 5 bbl gain
    MODERATE = "MODERATE"   # 5-20 bbl gain
    MAJOR = "MAJOR"         # 20-50 bbl gain
    CRITICAL = "CRITICAL"   # > 50 bbl gain

# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class WeatherCondition:
    """Weather conditions at a specific operation time"""
    timestamp: str
    wind_speed_knots: float
    wind_direction: str
    wave_height_m: float
    swell_direction: str
    visibility_km: float
    temperature_c: float
    barometric_pressure_mb: float
    severity: str
    impact_on_operation: str = ""

@dataclass
class KickEvent:
    """A kick or well control event"""
    event_id: str
    timestamp: str
    kick_type: str
    severity: str
    pit_gain_bbl: float
    flowline_out_bbl: float
    shut_in_pressure_psi: float
    formation_pressure_psi: float
    mud_weight_ppg: float
    kill_mud_weight_ppg: float
    detection_method: str
    recorded_in_log: bool
    time_to_detect_min: float
    time_to_control_min: float
    root_cause: str
    notes: str = ""

@dataclass
class TubingHangerLanding:
    """Record of tubing hanger landing operation"""
    landing_id: str
    well_id: str
    timestamp: str
    depth_msl: float
    weather: WeatherCondition
    rig_motion: str
    landing_successful: bool
    retries_required: int
    downtime_minutes: float
    notes: str = ""

# ==============================================================================
# WEATHER TRACKER
# ==============================================================================

class WeatherTracker:
    """
    Tracks weather conditions during critical operations
    """
    
    def __init__(self):
        self.weather_records = []
    
    def record_weather(self, 
                       timestamp: str,
                       wind_speed: float,
                       wind_dir: str,
                       wave_height: float,
                       swell_dir: str,
                       visibility: float,
                       temperature: float,
                       pressure: float) -> WeatherCondition:
        """Record weather conditions"""
        
        # Calculate severity
        if wind_speed < 10 and wave_height < 1:
            severity = WeatherSeverity.CALM
        elif wind_speed < 25 and wave_height < 3:
            severity = WeatherSeverity.MODERATE
        elif wind_speed < 40 and wave_height < 5:
            severity = WeatherSeverity.ROUGH
        else:
            severity = WeatherSeverity.SEVERE
        
        # Impact assessment
        if severity == WeatherSeverity.CALM:
            impact = "No impact on operations"
        elif severity == WeatherSeverity.MODERATE:
            impact = "Minor delays possible, normal operations"
        elif severity == WeatherSeverity.ROUGH:
            impact = "Significant delays, restricted lifts"
        else:
            impact = "Operations suspended"
        
        condition = WeatherCondition(
            timestamp=timestamp,
            wind_speed_knots=wind_speed,
            wind_direction=wind_dir,
            wave_height_m=wave_height,
            swell_direction=swell_dir,
            visibility_km=visibility,
            temperature_c=temperature,
            barometric_pressure_mb=pressure,
            severity=severity.value,
            impact_on_operation=impact
        )
        
        self.weather_records.append(condition)
        return condition
    
    def get_weather_at_time(self, target_time: str) -> Optional[WeatherCondition]:
        """Get weather closest to target time"""
        # In production, this would query a weather database
        for record in self.weather_records:
            if record.timestamp == target_time:
                return record
        return None
    
    def analyze_weather_impact(self, 
                               operation: str,
                               weather: WeatherCondition) -> Dict:
        """Analyze weather impact on operation"""
        
        impact_score = 0
        
        if weather.severity == WeatherSeverity.MODERATE.value:
            impact_score = 20
        elif weather.severity == WeatherSeverity.ROUGH.value:
            impact_score = 50
        elif weather.severity == WeatherSeverity.SEVERE.value:
            impact_score = 100
        
        return {
            "operation": operation,
            "weather_severity": weather.severity,
            "impact_score": impact_score,
            "risks": self._identify_risks(weather, operation),
            "mitigations": self._suggest_mitigations(weather, operation)
        }
    
    def _identify_risks(self, weather: WeatherCondition, operation: str) -> List[str]:
        risks = []
        
        if weather.wind_speed_knots > 25:
            risks.append("High wind - crane operations restricted")
        
        if weather.wave_height_m > 2:
            risks.append("Heavy swell - rig motion affecting pipe handling")
        
        if weather.visibility_km < 5:
            risks.append("Low visibility - helicopter ops affected")
        
        if "tubing hanger" in operation.lower() and weather.wave_height_m > 1.5:
            risks.append("Rig motion may affect tubing hanger landing")
        
        return risks
    
    def _suggest_mitigations(self, 
                             weather: WeatherCondition, 
                             operation: str) -> List[str]:
        mitigations = []
        
        if weather.severity in [WeatherSeverity.ROUGH.value, WeatherSeverity.SEVERE.value]:
            mitigations.append("Consider postponing non-critical operations")
            mitigations.append("Increase safety stand-downs")
        
        if "tubing hanger" in operation.lower():
            mitigations.append("Use motion compensation")
            mitigations("Monitor rig heave during landing")
        
        return mitigations

# ==============================================================================
# KICK DETECTOR
# ==============================================================================

class KickDetector:
    """
    Detects unrecorded kicks from pressure and flow data
    """
    
    def __init__(self):
        self.detected_kicks = []
        self.pressure_history = []
        self.flow_history = []
        
        # Detection thresholds
        self.pit_gain_threshold_bbl = 2.0
        self.pressure_spike_threshold_psi = 50
        self.flow_increase_threshold_pct = 10
    
    def analyze_pressure(self, 
                         timestamp: str,
                         pressure_psi: float,
                         pit_volume_bbl: float,
                         flow_in_bpm: float,
                         flow_out_bpm: float,
                         depth_md: float,
                         mud_weight_ppg: float) -> Optional[KickEvent]:
        """Analyze for kick indicators"""
        
        self.pressure_history.append({
            "time": timestamp,
            "pressure": pressure_psi,
            "pit": pit_volume_bbl,
            "flow_in": flow_in_bpm,
            "flow_out": flow_out_bpm
        })
        
        # Keep last 100 readings
        if len(self.pressure_history) > 100:
            self.pressure_history.pop(0)
        
        # Check for kick indicators
        kick_indicators = []
        
        # 1. Pit gain
        if len(self.pressure_history) > 5:
            recent_pits = [h["pit"] for h in self.pressure_history[-5:]]
            pit_change = max(recent_pits) - min(recent_pits)
            if pit_change > self.pit_gain_threshold_bbl:
                kick_indicators.append(("PIT_GAIN", pit_change))
        
        # 2. Flow differential
        if flow_in_bpm > 0:
            flow_diff = ((flow_out_bpm - flow_in_bpm) / flow_in_bpm) * 100
            if flow_diff > self.flow_increase_threshold_pct:
                kick_indicators.append(("FLOW_INCREASE", flow_diff))
        
        # 3. Pressure spike
        if len(self.pressure_history) > 2:
            recent_pressure = [h["pressure"] for h in self.pressure_history[-2:]]
            pressure_change = abs(recent_pressure[-1] - recent_pressure[0])
            if pressure_change > self.pressure_spike_threshold_psi:
                kick_indicators.append(("PRESSURE_SPIKE", pressure_change))
        
        # Determine if kick detected
        if len(kick_indicators) >= 2:
            return self._create_kick_event(
                timestamp=timestamp,
                indicators=kick_indicators,
                pit_gain=kick_indicators[0][1] if kick_indicators[0][0] == "PIT_GAIN" else 0,
                pressure=pressure_psi
            )
        
        return None
    
    def _create_kick_event(self,
                           timestamp: str,
                           indicators: List,
                           pit_gain: float,
                           pressure: float) -> KickEvent:
        """Create a kick event"""
        
        # Determine severity
        if pit_gain < 5:
            severity = KickSeverity.MINOR
        elif pit_gain < 20:
            severity = KickSeverity.MODERATE
        elif pit_gain < 50:
            severity = KickSeverity.MAJOR
        else:
            severity = KickSeverity.CRITICAL
        
        # Determine type
        kick_type = KickType.INFLUX
        
        if any("SWAB" in str(ind) for ind in indicators):
            kick_type = KickType.SWAB
        elif any("SURGE" in str(ind) for ind in indicators):
            kick_type = KickType.SURGE
        elif pit_gain > 10:
            kick_type = KickType.GAS_BUBBLE
        
        event = KickEvent(
            event_id=f"KICK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=timestamp,
            kick_type=kick_type.value,
            severity=severity.value,
            pit_gain_bbl=pit_gain,
            flowline_out_bbl=0,
            shut_in_pressure_psi=pressure,
            formation_pressure_psi=pressure + 500,  # Estimate
            mud_weight_ppg=0,
            kill_mud_weight_ppg=0,
            detection_method="ALGORITHM",
            recorded_in_log=False,  # Unrecorded!
            time_to_detect_min=5,
            time_to_control_min=30,
            root_cause="Formation influx"
        )
        
        self.detected_kicks.append(event)
        return event
    
    def scan_for_unrecorded_kicks(self, 
                                   well_data: Dict) -> List[KickEvent]:
        """Scan well data for unrecorded kicks"""
        
        unrecorded = []
        
        # Look for pressure anomalies
        pressures = well_data.get("pressures", [])
        
        for i, p in enumerate(pressures):
            if i > 0:
                pressure_change = abs(p.get("value", 0) - pressures[i-1].get("value", 0))
                
                if pressure_change > 100:
                    event = KickEvent(
                        event_id=f"KICK-SCAN-{i}",
                        timestamp=p.get("time", ""),
                        kick_type=KickType.INFLUX.value,
                        severity=KickSeverity.MODERATE.value,
                        pit_gain_bbl=0,
                        flowline_out_bbl=0,
                        shut_in_pressure_psi=p.get("value", 0),
                        formation_pressure_psi=0,
                        mud_weight_ppg=0,
                        kill_mud_weight_ppg=0,
                        detection_method="PRESSURE_ANOMALY",
                        recorded_in_log=False,
                        time_to_detect_min=0,
                        time_to_control_min=0,
                        root_cause="Pressure anomaly detected"
                    )
                    unrecorded.append(event)
        
        return unrecorded
    
    def get_kick_summary(self) -> Dict:
        """Get summary of detected kicks"""
        
        total = len(self.detected_kicks)
        unrecorded = sum(1 for k in self.detected_kicks if not k.recorded_in_log)
        
        by_severity = {}
        for kick in self.detected_kicks:
            sev = kick.severity
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_kicks": total,
            "unrecorded_kicks": unrecorded,
            "by_severity": by_severity,
            "kick_details": [
                {
                    "event_id": k.event_id,
                    "timestamp": k.timestamp,
                    "type": k.kick_type,
                    "severity": k.severity,
                    "pit_gain": k.pit_gain_bbl,
                    "recorded": k.recorded_in_log
                } for k in self.detected_kicks
            ]
        }

# ==============================================================================
# TUBING HANGER LANDING TRACKER
# ==============================================================================

class TubingHangerTracker:
    """
    Tracks tubing hanger landing operations with weather correlation
    """
    
    def __init__(self):
        self.landings = []
        self.weather_tracker = WeatherTracker()
    
    def record_landing(self,
                       well_id: str,
                       timestamp: str,
                       depth: float,
                       weather: WeatherCondition,
                       rig_motion: str = "NORMAL",
                       successful: bool = True,
                       retries: int = 0,
                       downtime: float = 0) -> TubingHangerLanding:
        """Record a tubing hanger landing"""
        
        landing = TubingHangerLanding(
            landing_id=f"TH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            well_id=well_id,
            timestamp=timestamp,
            depth_msl=depth,
            weather=weather,
            rig_motion=rig_motion,
            landing_successful=successful,
            retries_required=retries,
            downtime_minutes=downtime
        )
        
        self.landings.append(landing)
        return landing
    
    def analyze_weather_correlation(self) -> Dict:
        """Analyze correlation between weather and landing success"""
        
        if not self.landings:
            return {"error": "No landing records"}
        
        # Count by weather severity
        by_weather = defaultdict(lambda: {"total": 0, "successful": 0, "avg_retries": 0})
        
        for landing in self.landings:
            sev = landing.weather.severity
            by_weather[sev]["total"] += 1
            if landing.landing_successful:
                by_weather[sev]["successful"] += 1
            by_weather[sev]["avg_retries"] += landing.retries_required
        
        # Calculate rates
        for sev in by_weather:
            if by_weather[sev]["total"] > 0:
                success_rate = by_weather[sev]["successful"] / by_weather[sev]["total"] * 100
                by_weather[sev]["success_rate"] = round(success_rate, 1)
                by_weather[sev]["avg_retries"] = round(
                    by_weather[sev]["avg_retries"] / by_weather[sev]["total"], 1
                )
        
        return {
            "total_landings": len(self.landings),
            "by_weather_severity": dict(by_weather),
            "recommendation": self._generate_recommendation(by_weather)
        }
    
    def _generate_recommendation(self, by_weather: Dict) -> str:
        """Generate operational recommendations"""
        
        if WeatherSeverity.ROUGH.value in by_weather:
            if by_weather[WeatherSeverity.ROUGH.value]["success_rate"] < 80:
                return "Consider delaying TH landings in rough weather"
        
        if WeatherSeverity.MODERATE.value in by_weather:
            if by_weather[WeatherSeverity.MODERATE.value]["avg_retries"] > 1:
                return "Increase monitoring during moderate weather landings"
        
        return "Weather conditions acceptable for TH landing operations"

# ==============================================================================
# DEMO
# ==============================================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("WEATHER & KICK TRACKER")
    print("=" * 60)
    print()
    
    # Create trackers
    weather_tracker = WeatherTracker()
    kick_detector = KickDetector()
    th_tracker = TubingHangerTracker()
    
    # Demo: Record weather conditions
    print("📊 Recording weather conditions...")
    
    weather1 = weather_tracker.record_weather(
        timestamp="2026-03-01T10:00:00Z",
        wind_speed=15.0,
        wind_dir="NW",
        wave_height=1.5,
        swell_dir="W",
        visibility=10.0,
        temperature=12.0,
        pressure=1013.0
    )
    
    weather2 = weather_tracker.record_weather(
        timestamp="2026-03-01T14:00:00Z",
        wind_speed=35.0,
        wind_dir="W",
        wave_height=3.5,
        swell_dir="NW",
        visibility=5.0,
        temperature=10.0,
        pressure=1008.0
    )
    
    print(f"   Condition 1: {weather1.severity} - {weather1.impact_on_operation}")
    print(f"   Condition 2: {weather2.severity} - {weather2.impact_on_operation}")
    print()
    
    # Demo: Analyze weather impact on TH landing
    print("=" * 60)
    print("🎯 TUBING HANGER LANDING ANALYSIS")
    print("=" * 60)
    print()
    
    # Record landing with weather
    landing1 = th_tracker.record_landing(
        well_id="Stella_3_30",
        timestamp="2026-03-01T10:00:00Z",
        depth=150.0,
        weather=weather1,
        rig_motion="MINIMAL",
        successful=True,
        retries=0,
        downtime=0
    )
    
    landing2 = th_tracker.record_landing(
        well_id="Other_Well",
        timestamp="2026-03-01T14:00:00Z",
        depth=200.0,
        weather=weather2,
        rig_motion="MODERATE_HEAVE",
        successful=False,
        retries=3,
        downtime=90
    )
    
    print(f"Landing 1: {landing1.landing_successful} (Weather: {landing1.weather.severity})")
    print(f"   Retries: {landing1.retries_required}")
    print()
    
    print(f"Landing 2: {landing2.landing_successful} (Weather: {landing2.weather.severity})")
    print(f"   Retries: {landing2.retries_required}")
    print(f"   Downtime: {landing2.downtime_minutes} min")
    print()
    
    # Weather correlation
    correlation = th_tracker.analyze_weather_correlation()
    print(f"Weather Correlation Analysis:")
    print(f"   Recommendation: {correlation['recommendation']}")
    print()
    
    # Demo: Kick detection
    print("=" * 60)
    print("🚨 KICK DETECTION")
    print("=" * 60)
    print()
    
    print("Simulating pressure data analysis...")
    
    # Simulate pressure readings
    readings = [
        ("2026-03-01T10:00:00Z", 4500, 150.0, 200, 200),
        ("2026-03-01T10:05:00Z", 4520, 152.0, 200, 200),
        ("2026-03-01T10:10:00Z", 4550, 155.0, 200, 210),  # Flow increase
        ("2026-03-01T10:15:00Z", 4600, 158.0, 200, 225),  # More flow out
        ("2026-03-01T10:20:00Z", 4700, 162.0, 200, 240),  # Kick detected!
    ]
    
    for ts, pres, pit, flow_in, flow_out in readings:
        kick = kick_detector.analyze_pressure(
            timestamp=ts,
            pressure_psi=pres,
            pit_volume_bbl=pit,
            flow_in_bpm=flow_in,
            flow_out_bpm=flow_out,
            depth_md=10000,
            mud_weight_ppg=12.0
        )
        
        if kick:
            print(f"   🚨 KICK DETECTED at {ts}")
            print(f"      Type: {kick.kick_type}")
            print(f"      Severity: {kick.severity}")
            print(f"      Pit Gain: {kick.pit_gain_bbl} bbl")
            print(f"      Recorded in log: {kick.recorded_in_log}")
            print()
    
    # Kick summary
    summary = kick_detector.get_kick_summary()
    
    print("KICK SUMMARY:")
    print(f"   Total detected: {summary['total_kicks']}")
    print(f"   Unrecorded: {summary['unrecorded_kicks']}")
    print(f"   By severity: {summary['by_severity']}")
    print()
    
    # Save results
    output = {
        "weather_records": [
            {
                "timestamp": w.timestamp,
                "wind_speed": w.wind_speed_knots,
                "wave_height": w.wave_height_m,
                "severity": w.severity
            } for w in weather_tracker.weather_records
        ],
        "landings": [
            {
                "well": l.well_id,
                "timestamp": l.timestamp,
                "weather_severity": l.weather.severity,
                "successful": l.landing_successful,
                "retries": l.retries_required
            } for l in th_tracker.landings
        ],
        "kicks": summary["kick_details"],
        "correlation": correlation
    }
    
    with open("weather_kick_report.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print("=" * 60)
    print("📁 SAVED: weather_kick_report.json")
    print("=" * 60)
