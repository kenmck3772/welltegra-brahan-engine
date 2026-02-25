#!/usr/bin/env python3
"""
Run Brahan Engine with Found Data - Fixed Version
===============================================

Uses the data directories found in your wellabuild folder.
"""

import os
import sys
import shutil
import json
from pathlib import Path
import subprocess

def run_brahan_engine():
    """Run the Brahan Engine with your data"""
    print("🎯 Brahan Engine - Running with Your Data")
    print("=" * 50)

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

    # Update the UnifiedConfig with correct format
    # Modify run_unified_analysis.py to use the config correctly
    print("\n🔧 Setting up configuration...")

    # Simple configuration for now
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
    config_file = Path("your_data_config.json")
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)

    print(f"📄 Configuration saved to: {config_file}")

    # Run the engine
    print("\n🚀 Starting Brahan Engine Analysis...")
    print("This may take 2-5 minutes depending on file sizes.")
    print()

    try:
        result = subprocess.run([
            sys.executable, "run_unified_analysis.py",
            "--config", str(config_file)
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode == 0:
            print("✅ Analysis completed successfully!")

            # Show output files
            output_dir = engine_data / "output"
            if output_dir.exists():
                json_files = list(output_dir.glob("*.json"))
                print(f"\n📊 Output files created ({len(json_files)}):")
                for json_file in json_files:
                    print(f"   - {json_file.name}")

                # Show latest results
                if json_files:
                    latest = max(json_files, key=lambda x: x.stat().st_mtime)
                    print(f"\n📋 Latest results: {latest.name}")

                    # Try to show summary
                    try:
                        with open(latest, 'r') as f:
                            data = json.load(f)

                            print("\n" + "="*50)
                            print("📈 ANALYSIS SUMMARY")
                            print("="*50)

                            if 'analysis_timestamp' in data:
                                print(f"Analysis Time: {data['analysis_timestamp']}")
                            if 'build_results' in data:
                                for build_name, result in data['build_results'].items():
                                    status = result.get('status', 'UNKNOWN')
                                    if status == 'SUCCESS':
                                        icon = '✅'
                                    elif status == 'FAILED':
                                        icon = '❌'
                                    else:
                                        icon = '⚠️'
                                    print(f"{build_name.upper()}: {icon} {status}")

                            if 'summary' in data:
                                print(f"\nSummary:")
                                for key, value in data['summary'].items():
                                    print(f"  {key}: {value}")

                    except Exception as e:
                        print(f"Could not parse summary: {e}")

            print("\n🎉 Brahan Engine analysis complete!")
            return True

        else:
            print("❌ Analysis failed:")
            print(result.stderr)

            # Check if it's a config error
            if "unexpected keyword argument" in result.stderr:
                print("\n💡 Configuration error detected.")
                print("Trying with default configuration...")

                # Try without config file
                result2 = subprocess.run([
                    sys.executable, "run_unified_analysis.py"
                ], capture_output=True, text=True, timeout=60)

                if result2.returncode == 0:
                    print("✅ Analysis completed with default config!")
                    return True
                else:
                    print("❌ Still failed with default config:")
                    print(result2.stderr)
                    return False

            return False

    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out after 5 minutes")
        print("The engine may still be running. Check output directory later.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = run_brahan_engine()
    if success:
        print("\n💡 Next steps:")
        print("1. Check brahan_engine_data/output/ for results")
        print("2. Open HTML files in a browser for visualizations")
        print("3. Review JSON files for detailed analysis")
    else:
        print("\n💡 Troubleshooting:")
        print("1. Try: python3 basic_integration.py")
        print("2. Check: ls -la brahan_engine_data/output/")
        print("3. The engine may be processing large files")