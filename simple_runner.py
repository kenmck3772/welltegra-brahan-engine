#!/usr/bin/env python3
"""
Simple Unified Runner
======================

A simplified version of the unified integration that works with existing modules.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add both build directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
wellark_dir = os.path.join(current_dir, '..', 'welltegra-brahan-engine-main')
wellabuild_dir = '/home/brahan_welltegra/wellabuild/wellabuild'

sys.path.append(wellark_dir)
sys.path.append(wellabuild_dir)

def main():
    """Simple unified analysis runner"""
    print("🚀 Simple Unified Forensic Analysis")
    print("=" * 50)

    # Setup output directory
    output_dir = os.path.join(os.path.dirname(__file__), "simple_output")
    os.makedirs(output_dir, exist_ok=True)

    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_time = time.time()

    results = {
        'analysis_timestamp': datetime.now().isoformat(),
        'build_results': {},
        'summary': {
            'total_findings': 0,
            'execution_time': 0
        }
    }

    # 1. Run WellABUILD Analysis
    print("\n🔍 Running WellABUILD Analysis...")
    try:
        from forensic_harvester import DataExtractor, ReconciliationEngine
        from run_full_audit import run_full_audit

        # Run full audit from WellABUILD
        audit_results = run_full_audit()

        results['build_results']['wellabuild'] = {
            'status': 'SUCCESS',
            'audit_executed': True,
            'timestamp': datetime.now().isoformat(),
            'results': audit_results
        }
        print(f"✅ WellABUILD audit completed")
    except Exception as e:
        results['build_results']['wellabuild'] = {
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(f"❌ WellABUILD failed: {e}")

    # 2. Run WellArk Analysis
    print("\n🔍 Running WellArk Analysis...")
    try:
        from wellabuild_sdk import WellABuildSDK

        # Use WellABUILD SDK as the unified engine
        sdk = WellABuildSDK()
        sdk_state = sdk.get_operation_state()

        results['build_results']['wellark'] = {
            'status': 'SUCCESS',
            'sdk_initialized': True,
            'operation_state': sdk_state.value,
            'timestamp': datetime.now().isoformat()
        }
        print(f"✅ WellArk/WellABUILD SDK initialized")
    except Exception as e:
        results['build_results']['wellark'] = {
            'status': 'FAILED',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        print(f"❌ WellArk failed: {e}")

    # 3. Create unified summary
    results['summary']['execution_time'] = time.time() - start_time

    successful_builds = sum(1 for r in results['build_results'].values() if r['status'] == 'SUCCESS')
    results['summary']['successful_builds'] = successful_builds
    results['summary']['total_builds'] = len(results['build_results'])

    # 4. Save results
    output_file = os.path.join(output_dir, f"simple_unified_{timestamp}.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {output_file}")
    print("\n📊 Summary:")
    print(f"  - Execution time: {results['summary']['execution_time']:.2f}s")
    print(f"  - Successful builds: {successful_builds}/{results['summary']['total_builds']}")

    if successful_builds == results['summary']['total_builds']:
        print("✅ All builds completed successfully!")
    else:
        print("⚠️  Some builds failed, but results are saved.")

if __name__ == "__main__":
    main()