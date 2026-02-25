#!/usr/bin/env python3
# Test imports for Brahan Engine

import sys
import os

# Add paths
sys.path.append('/home/brahan_welltegra/wellark-forensics/welltegra-brahan-engine-main')
sys.path.append('/home/brahan_welltegra/wellabuild/wellabuild')

print("Testing imports...")

try:
    import pandas as pd
    print("✅ pandas imported")
except Exception as e:
    print(f"❌ pandas failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported")
except Exception as e:
    print(f"❌ numpy failed: {e}")

try:
    import scipy
    print("✅ scipy imported")
except Exception as e:
    print(f"❌ scipy failed: {e}")

try:
    # Test WellABUILD imports
    from forensic_harvester import DataExtractor, ReconciliationEngine
    print("✅ WellABUILD forensic_harvester imported")
except Exception as e:
    print(f"❌ WellABUILD import failed: {e}")

try:
    # Test WellABUILD SDK
    from wellabuild_sdk import WellABuildSDK
    print("✅ WellABUILD SDK imported")
except Exception as e:
    print(f"❌ WellABUILD SDK failed: {e}")

print("\nImport test complete!")
