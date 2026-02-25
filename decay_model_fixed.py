#!/usr/bin/env python3
"""
Fixed Decay Model - Correct remaining life calculation
"""

import json
from datetime import datetime

# Corrosion rates (mm/year)
CORROSION_RATES = {
    "SWEET_PRODUCTION": 0.2,
    "SOUR_PRODUCTION": 0.5,
    "SEAWATER": 0.15,
    "BRINE": 0.3,
}

def calculate_decay(initial_wall, install_year, environment, target_year):
    """Calculate decay at target year"""
    
    years = target_year - install_year
    
    # Get corrosion rate
    rate_mm = CORROSION_RATES.get(environment, 0.2)
    rate_in = rate_mm / 25.4  # Convert to inches/year
    
    # Calculate wall loss
    wall_loss = rate_in * years
    remaining_wall = max(0, initial_wall - wall_loss)
    
    return remaining_wall, wall_loss

def calculate_remaining_life(current_wall, min_wall_pct, environment):
    """Calculate remaining life from current state"""
    
    min_wall = current_wall * min_wall_pct
    
    if current_wall <= min_wall:
        return 0, "FAILED"
    
    rate_mm = CORROSION_RATES.get(environment, 0.2)
    rate_in = rate_mm / 25.4
    
    remaining_thickness = current_wall - min_wall
    remaining_years = remaining_thickness / rate_in if rate_in > 0 else 999
    
    # Status
    wall_loss_pct = (1 - current_wall / initial_wall) * 100 if initial_wall > 0 else 0
    
    if wall_loss_pct > 50:
        status = "CRITICAL"
    elif wall_loss_pct > 30:
        status = "SEVERE"
    elif wall_loss_pct > 15:
        status = "MODERATE"
    else:
        status = "ACCEPTABLE"
    
    return remaining_years, status

# Parameters
initial_wall = 0.470  # inches
install_year = 1990
environment = "SWEET_PRODUCTION"
min_wall_pct = 0.5  # 50% minimum before failure

print()
print("=" * 70)
print("DECAY MODEL - CORROSION OVER TIME")
print("=" * 70)
print()

print(f"Initial wall thickness: {initial_wall} inches")
print(f"Install year: {install_year}")
print(f"Environment: {environment}")
print(f"Corrosion rate: {CORROSION_RATES[environment]} mm/year")
print(f"Minimum wall (failure): {initial_wall * min_wall_pct:.3f} inches (50%)")
print()

print("=" * 70)
print("DECAY TIMELINE")
print("=" * 70)
print()

print(f"{'Year':<8} {'Wall(in)':<12} {'Loss%':<10} {'Remaining':<12} {'Status':<12}")
print("-" * 60)

for year in range(1990, 2055, 5):
    wall, loss = calculate_decay(initial_wall, install_year, environment, year)
    
    # Calculate remaining life from THIS point
    if wall > 0:
        remaining_life, status = calculate_remaining_life(wall, min_wall_pct, environment)
    else:
        remaining_life = 0
        status = "FAILED"
    
    loss_pct = (loss / initial_wall) * 100 if initial_wall > 0 else 100
    
    print(f"{year:<8} {wall:<12.3f} {loss_pct:<10.1f} {remaining_life:<12.1f} {status:<12}")

print()

# Find year of failure
failure_year = None
for year in range(install_year, 2100):
    wall, _ = calculate_decay(initial_wall, install_year, environment, year)
    if wall <= initial_wall * min_wall_pct:
        failure_year = year
        break

if failure_year:
    print(f"⚠️ PREDICTED FAILURE YEAR: {failure_year}")
    print(f"   Wall will reach minimum ({initial_wall * min_wall_pct:.3f} in) after {failure_year - install_year} years")
    print()

# Assessment
current_year = 2024
current_wall, _ = calculate_decay(initial_wall, install_year, environment, current_year)
remaining, status = calculate_remaining_life(current_wall, min_wall_pct, environment)

print("=" * 70)
print("CURRENT ASSESSMENT (2024)")
print("=" * 70)
print()
print(f"   Current wall: {current_wall:.3f} inches")
print(f"   Wall loss: {(1-current_wall/initial_wall)*100:.1f}%")
print(f"   Remaining life: {remaining:.1f} years")
print(f"   Status: {status}")
print()

# Save
output = {
    "initial_wall_inches": initial_wall,
    "install_year": install_year,
    "environment": environment,
    "corrosion_rate_mm_per_year": CORROSION_RATES[environment],
    "current_wall_2024": round(current_wall, 3),
    "predicted_failure_year": failure_year,
    "remaining_life_years": round(remaining, 1),
    "status": status
}

with open("decay_assessment.json", "w") as f:
    json.dump(output, f, indent=2)

print("📁 Saved: decay_assessment.json")
