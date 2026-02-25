#!/usr/bin/env python3
"""
Test Integration Script
=======================

Simple script to test the unified integration without running full analysis.
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from UNIFIED_INTEGRATION import UnifiedConfig, UnifiedForensicEngine

def test_configuration():
    """Test configuration loading and validation"""
    print("🔧 Testing Configuration...")

    try:
        config = UnifiedConfig()
        print(f"✅ Configuration loaded successfully")
        print(f"   - WellArk: {config.wellark_dir}")
        print(f"   - WellABUILD: {config.wellabuild_dir}")
        print(f"   - Output: {config.output_dir}")
        return True
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist"""
    print("\n📁 Testing Directory Structure...")

    config = UnifiedConfig()
    directories = [
        config.wellark_dir,
        config.wellabuild_dir,
        config.project_airtight_dir
    ]

    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - NOT FOUND")
            all_exist = False

    return all_exist

def test_module_imports():
    """Test importing modules from both builds"""
    print("\n📦 Testing Module Imports...")

    config = UnifiedConfig()
    success = True

    # Test WellArk imports
    try:
        sys.path.append(config.wellark_dir)
        from src.forensic_gate_engine import ForensicGateEngine
        print("✅ WellArk ForensicGateEngine imported")
    except Exception as e:
        print(f"❌ WellArk import failed: {e}")
        success = False

    # Test WellABUILD imports
    try:
        sys.path.append(config.wellabuild_dir)
        from forensic_harvester import ForensicHarvester
        print("✅ WellABUILD ForensicHarvester imported")
    except Exception as e:
        print(f"❌ WellABUILD import failed: {e}")
        success = False

    return success

def test_output_creation():
    """Test output directory creation"""
    print("\n📤 Testing Output Creation...")

    try:
        config = UnifiedConfig()
        os.makedirs(config.output_dir, exist_ok=True)

        # Test file writing
        test_file = os.path.join(config.output_dir, "test_file.json")
        with open(test_file, 'w') as f:
            json.dump({"test": "success", "timestamp": datetime.now().isoformat()}, f)

        # Verify file exists
        if os.path.exists(test_file):
            print(f"✅ Output directory created and writable")
            os.remove(test_file)  # Clean up
            return True
        else:
            print(f"❌ Failed to create test file")
            return False

    except Exception as e:
        print(f"❌ Output creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Unified Integration Test")
    print("=" * 50)

    tests = [
        test_configuration,
        test_directory_structure,
        test_module_imports,
        test_output_creation
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✅ All tests passed! Integration is ready.")
        print("\nNext steps:")
        print("1. Run: python run_unified_analysis.py")
        print("2. Check output directory for results")
    else:
        print("❌ Some tests failed. Check the output above.")
        print("\nTroubleshooting:")
        print("1. Ensure all build directories exist")
        print("2. Check Python path configuration")
        print("3. Verify module imports work correctly")

if __name__ == "__main__":
    main()