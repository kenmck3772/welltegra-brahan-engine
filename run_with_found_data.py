#!/usr/bin/env python3
"""
Run Brahan Engine with Found Data
=================================

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

    # Create configuration
    config = {
        "input_directories": {
            "las_files": str(engine_data / "las_files"),
            "pdf_files": str(engine_data / "pdf_files"),
            "tiff_files": str(engine_data / "tiff_files"),
            "log_files": str(engine_data / "log_files")
        },
        "analysis_parameters": {
            "temporal_window_days": 365,
            "predicate_threshold": 0.8,
            "enable_pdf_ocr": True,
            "enable_las_validation": True,
            "enable_tiff_analysis": True,
            "enable_log_analysis": True
        },
        "output_settings": {
            "output_directory": str(engine_data / "output"),
            "generate_visualization": True,
            "export_osdu": False,
            "enable_audit": True
        }
    }

    # Save configuration
    config_file = Path("your_data_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n📄 Configuration saved to: {config_file}")

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

                            if 'summary' in data:
                                for key, value in data['summary'].items():
                                    print(f"{key}: {value}")
                            elif 'build_results' in data:
                                wellark = data['build_results'].get('wellark', {})
                                wellabuild = data['build_results'].get('wellabuild', {})

                                if wellark.get('status') == 'SUCCESS':
                                    print("WellArk Analysis: ✅ Completed")
                                if wellabuild.get('status') == 'SUCCESS':
                                    print("WellABUILD Analysis: ✅ Completed")

                                if 'total_findings' in data:
                                    print(f"Total Findings: {data['total_findings']}")
                            else:
                                print("Analysis completed. Check JSON files for details.")

                    except Exception as e:
                        print(f"Could not parse summary: {e}")

            print("\n🎉 Brahan Engine analysis complete!")
            return True

        else:
            print("❌ Analysis failed:")
            print(result.stderr)
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
        print("1. Check file permissions")
        print("2. Verify all files are valid")
        print("3. Try: python3 basic_integration.py")