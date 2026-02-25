#!/usr/bin/env python3
"""
Run Brahan Engine with Your Data - Final Version
===============================================

Runs the full Brahan Engine with your LAS, PDF, and TIFF data.
"""

import os
import sys
import shutil
import json
from pathlib import Path
import subprocess
from datetime import datetime

def run_full_brahan_engine():
    """Run the full Brahan Engine with your data"""
    print("🚀 Brahan Engine - Full Analysis with Your Data")
    print("=" * 60)

    # Your data directories
    data_dirs = {
        "las": "/home/brahan_welltegra/wellabuild/wellabuild/las_files",
        "pdf": "/home/brahan_welltegra/wellabuild/wellabuild/pdf_files",
        "tiff": "/home/brahan_welltegra/wellabuild/wellabuild/tiff_files"
    }

    # Check directories exist
    print("\n📁 Checking data directories...")
    for file_type, path in data_dirs.items():
        if os.path.exists(path):
            file_count = len(list(Path(path).glob(f"*{'las' if file_type == 'las' else 'pdf' if file_type == 'pdf' else 'tif*'}")))
            print(f"✅ {file_type.upper()} folder: {path} ({file_count} files)")
        else:
            print(f"❌ {file_type.upper()} folder not found: {path}")
            return False

    # Create engine directory
    engine_data = Path("brahan_engine_data")
    engine_data.mkdir(exist_ok=True)

    # Create subdirectories
    (engine_data / "las_files").mkdir(exist_ok=True)
    (engine_data / "pdf_files").mkdir(exist_ok=True)
    (engine_data / "tiff_files").mkdir(exist_ok=True)
    (engine_data / "log_files").mkdir(exist_ok=True)
    (engine_data / "output").mkdir(exist_ok=True)

    print(f"\n📁 Engine directory created: {engine_data}")

    # Copy files
    print("\n📂 Copying files to engine...")
    total_files = 0

    for file_type, source_dir in data_dirs.items():
        target_dir = engine_data / f"{file_type}_files"
        extension = "las" if file_type == "las" else "pdf" if file_type == "pdf" else "tif*"

        files_copied = 0
        for file_path in Path(source_dir).glob(f"*.{extension}"):
            if file_path.is_file():
                shutil.copy2(file_path, target_dir)
                files_copied += 1
                total_files += 1

        print(f"   ✓ Copied {files_copied} {file_type.upper()} files")

    print(f"\n📊 Total files copied: {total_files}")

    # Create configuration without Project Airtight
    config_data = {
        "root_dir": "/home/brahan_welltegra",
        "wellark_dir": "/home/brahan_welltegra/wellark-forensics/welltegra-brahan-engine-main",
        "wellabuild_dir": "/home/brahan_welltegra/wellabuild/wellabuild",
        "project_airtight_dir": "",
        "temporal_window_days": 365,
        "predicate_threshold": 0.8,
        "spatial_tolerance": 0.001,
        "output_dir": str(engine_data / "output"),
        "export_osdu": False,
        "generate_visualization": True,
        "enable_audit": True,
        "audit_signature": True,
        "retention_days": 90
    }

    # Save configuration
    config_file = Path("your_final_config.json")
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)

    print(f"📄 Configuration saved to: {config_file}")

    # Create a simple test script that imports the actual modules
    create_test_script()

    # Run the analysis
    print("\n🚀 Starting Brahan Engine Analysis...")
    print("This will process all your LAS, PDF, and TIFF files.")
    print("This may take 5-10 minutes...")
    print()

    start_time = datetime.now()

    try:
        # Run the engine
        result = subprocess.run([
            sys.executable, "run_unified_analysis.py",
            "--config", str(config_file),
            "--verbose"
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"\n⏱️  Analysis completed in: {duration}")

        if result.returncode == 0:
            print("✅ Brahan Engine analysis completed successfully!")

            # Show output files
            output_dir = engine_data / "output"
            if output_dir.exists():
                all_files = list(output_dir.glob("*"))
                json_files = [f for f in all_files if f.suffix == '.json']
                html_files = [f for f in all_files if f.suffix == '.html']
                other_files = [f for f in all_files if f not in json_files + html_files]

                print(f"\n📊 Output files created:")
                print(f"   JSON files: {len(json_files)}")
                print(f"   HTML files: {len(html_files)}")
                print(f"   Other files: {len(other_files)}")

                # Show all files
                if json_files:
                    print(f"\n📄 JSON Results:")
                    for json_file in json_files:
                        print(f"   - {json_file.name}")

                if html_files:
                    print(f"\n🌐 HTML Reports:")
                    for html_file in html_files:
                        print(f"   - {html_file.name} (Open in browser)")

                # Show summary from latest results
                if json_files:
                    latest = max(json_files, key=lambda x: x.stat().st_mtime)
                    print(f"\n📋 Latest Results: {latest.name}")

                    try:
                        with open(latest, 'r') as f:
                            data = json.load(f)

                            print("\n" + "="*60)
                            print("🎯 BRAHAN ENGINE ANALYSIS SUMMARY")
                            print("="*60)

                            # Show key metrics
                            if 'analysis_timestamp' in data:
                                print(f"🕐 Analysis Time: {data['analysis_timestamp']}")

                            if 'summary' in data:
                                print(f"\n📊 Summary:")
                                for key, value in data['summary'].items():
                                    print(f"   {key}: {value}")

                            if 'build_results' in data:
                                print(f"\n🏗️  Build Results:")
                                for build_name, result in data['build_results'].items():
                                    status = result.get('status', 'UNKNOWN')
                                    if status == 'SUCCESS':
                                        icon = '✅'
                                    elif status == 'FAILED':
                                        icon = '❌'
                                    else:
                                        icon = '⚠️'
                                    print(f"   {build_name.upper()}: {icon} {status}")

                            if 'correlations' in data:
                                print(f"\n🔗 Correlated Findings: {len(data['correlations'])}")

                            print(f"\n📁 Total Files Processed: {total_files}")

                    except Exception as e:
                        print(f"Could not parse summary: {e}")

            print("\n🎉 BRAHAN ENGINE ANALYSIS COMPLETE!")
            print("\n💡 Next Steps:")
            print("1. Open HTML files in a web browser for visualizations")
            print("2. Review JSON files for detailed analysis")
            print("3. Check audit trail for chain of custody")

            return True

        else:
            print("❌ Analysis failed:")
            print(result.stderr)

            # Check if it's a specific error
            if "No module named" in result.stderr:
                missing_module = result.stderr.split("No module named '")[1].split("'")[0]
                print(f"\n💡 Missing module: {missing_module}")
                print("Try installing it:")
                print(f"pip install --break-system-packages {missing_module}")

            return False

    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out after 10 minutes")
        print("The engine may still be running. Check output directory later.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_script():
    """Create a simple test script to verify imports"""
    test_script = """#!/usr/bin/env python3
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

print("\\nImport test complete!")
"""
    with open("test_imports.py", 'w') as f:
        f.write(test_script)

    os.chmod("test_imports.py", 0o755)

if __name__ == "__main__":
    success = run_full_brahan_engine()
    if success:
        print("\n🎯 SUCCESS: Brahan Engine analysis complete!")
        print("Your forensic analysis is ready.")
    else:
        print("\n❌ Issues encountered during analysis.")
        print("Check the error messages above for troubleshooting.")