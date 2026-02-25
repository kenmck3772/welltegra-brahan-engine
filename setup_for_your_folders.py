#!/usr/bin/env python3
"""
Setup Script for Your Folder Structure
======================================

This script configures the Brahan Engine to work with your specific folder structure:
- LAS folder
- PDF folder
- TIFFs folder
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

def setup_for_your_folders():
    """Setup the Brahan Engine for your specific folder structure"""
    print("🔧 Brahan Engine Setup for Your Folders")
    print("=" * 50)

    # Common locations for your folders
    common_locations = [
        "/home/brahan_welltegra",  # Your home directory
        "./",                    # Current directory
        "../",                   # Parent directory
        "~/",                    # Home directory shortcut
    ]

    # Find your folders
    las_folder = None
    pdf_folder = None
    tiff_folder = None

    print("\n📁 Looking for your folders...")

    # Check common locations
    for base in common_locations:
        base_path = Path(base).expanduser()

        # Look for LAS folder
        if not las_folder:
            las_patterns = ["las", "LAS", "Logs", "LOGS"]
            for pattern in las_patterns:
                test_path = base_path / pattern
                if test_path.exists() and any(test_path.glob("*.las")):
                    las_folder = test_path
                    print(f"✅ Found LAS folder: {las_folder}")
                    break

        # Look for PDF folder
        if not pdf_folder:
            pdf_patterns = ["pdf", "PDF", "Documents", "docs", "DOCS"]
            for pattern in pdf_patterns:
                test_path = base_path / pattern
                if test_path.exists() and any(test_path.glob("*.pdf")):
                    pdf_folder = test_path
                    print(f"✅ Found PDF folder: {pdf_folder}")
                    break

        # Look for TIFF folder
        if not tiff_folder:
            tiff_patterns = ["tiffs", "TIFFS", "tiff", "TIFF", "Images", "IMG"]
            for pattern in tiff_patterns:
                test_path = base_path / pattern
                if test_path.exists() and any(test_path.glob("*.tif*")):
                    tiff_folder = test_path
                    print(f"✅ Found TIFF folder: {tiff_folder}")
                    break

    # If not found, ask for paths
    if not las_folder:
        print("\n❌ Could not find LAS folder")
        las_folder = input("Enter path to your LAS folder: ").strip()
        if las_folder:
            las_folder = Path(las_folder).expanduser()
            if las_folder.exists():
                print(f"✅ Using LAS folder: {las_folder}")
            else:
                print("❌ LAS folder does not exist")
                return

    if not pdf_folder:
        print("\n❌ Could not find PDF folder")
        pdf_folder = input("Enter path to your PDF folder: ").strip()
        if pdf_folder:
            pdf_folder = Path(pdf_folder).expanduser()
            if pdf_folder.exists():
                print(f"✅ Using PDF folder: {pdf_folder}")
            else:
                print("❌ PDF folder does not exist")
                return

    if not tiff_folder:
        print("\n❌ Could not find TIFF folder")
        tiff_folder = input("Enter path to your TIFF folder: ").strip()
        if tiff_folder:
            tiff_folder = Path(tiff_folder).expanduser()
            if tiff_folder.exists():
                print(f"✅ Using TIFF folder: {tiff_folder}")
            else:
                print("❌ TIFF folder does not exist")
                return

    # Create engine data directory
    engine_data_dir = Path("brahan_engine_data")
    engine_data_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (engine_data_dir / "las_files").mkdir(exist_ok=True)
    (engine_data_dir / "pdf_files").mkdir(exist_ok=True)
    (engine_data_dir / "tiff_files").mkdir(exist_ok=True)
    (engine_data_dir / "output").mkdir(exist_ok=True)

    print(f"\n📁 Created engine data directory: {engine_data_dir}")

    # Count files
    las_count = len(list(las_folder.glob("*.las")))
    pdf_count = len(list(pdf_folder.glob("*.pdf")))
    tiff_count = len(list(tiff_folder.glob("*.tif*")))

    print(f"\n📊 File counts:")
    print(f"   LAS files: {las_count}")
    print(f"   PDF files: {pdf_count}")
    print(f"   TIFF files: {tiff_count}")

    # Copy files (ask for confirmation)
    print("\n📂 Copying files to engine...")

    # Copy LAS files
    if las_count > 0:
        print(f"   Copying {las_count} LAS files...")
        for las_file in las_folder.glob("*.las"):
            shutil.copy2(las_file, engine_data_dir / "las_files")

    # Copy PDF files
    if pdf_count > 0:
        print(f"   Copying {pdf_count} PDF files...")
        for pdf_file in pdf_folder.glob("*.pdf"):
            shutil.copy2(pdf_file, engine_data_dir / "pdf_files")

    # Copy TIFF files
    if tiff_count > 0:
        print(f"   Copying {tiff_count} TIFF files...")
        for tiff_file in tiff_folder.glob("*.tif*"):
            shutil.copy2(tiff_file, engine_data_dir / "tiff_files")

    # Create configuration
    config = {
        "input_directories": {
            "las_files": str(engine_data_dir / "las_files"),
            "pdf_files": str(engine_data_dir / "pdf_files"),
            "tiff_files": str(engine_data_dir / "tiff_files"),
            "log_files": str(engine_data_dir / "log_files")
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
            "output_directory": str(engine_data_dir / "output"),
            "generate_visualization": True,
            "export_osdu": False,
            "enable_audit": True
        }
    }

    # Save configuration
    config_file = Path("your_folders_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to: {config_file}")

    # Create summary
    print("\n📋 Setup Summary:")
    print("=" * 50)
    print(f"LAS folder: {las_folder}")
    print(f"PDF folder: {pdf_folder}")
    print(f"TIFF folder: {tiff_folder}")
    print(f"Engine data: {engine_data_dir}")
    print(f"Config file: {config_file}")
    print("\n🚀 Ready to run Brahan Engine!")
    print("\nNext steps:")
    print("1. Run: python run_unified_analysis.py --config your_folders_config.json")
    print("2. Or use: python feed_engine.py")

    # Show file preview
    print("\n📊 Files ready for analysis:")
    print(f"   LAS files: {len(list((engine_data_dir / 'las_files').glob('*.las')))}")
    print(f"   PDF files: {len(list((engine_data_dir / 'pdf_files').glob('*.pdf')))}")
    print(f"   TIFF files: {len(list((engine_data_dir / 'tiff_files').glob('*.tif*')))}")

    return True

def run_quick_analysis():
    """Run a quick analysis with the setup"""
    print("\n🚀 Running Quick Analysis...")

    # Check if config exists
    config_file = Path("your_folders_config.json")
    if not config_file.exists():
        print("❌ No configuration found. Run setup first.")
        return False

    # Run the engine
    import subprocess
    result = subprocess.run([
        sys.executable, "run_unified_analysis.py",
        "--config", str(config_file)
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Analysis completed!")
        print("\nResults:")
        print(result.stdout)

        # Show output files
        output_dir = Path("brahan_engine_data/output")
        if output_dir.exists():
            print(f"\n📄 Output files in {output_dir}:")
            for file in output_dir.glob("*.json"):
                print(f"   - {file.name}")
        return True
    else:
        print("❌ Analysis failed:")
        print(result.stderr)
        return False

def main():
    """Main function"""
    print("🎯 Brahan Engine Setup for Your Specific Folders")
    print("=" * 60)

    print("This script will:")
    print("1. Find your LAS, PDF, and TIFF folders")
    print("2. Copy files to the engine")
    print("3. Create configuration")
    print("4. Ready the engine for analysis")
    print()

    setup_for_your_folders()

    # Ask if user wants to run analysis
    run_now = input("\nRun analysis now? (y/n): ").lower().strip()
    if run_now == 'y':
        run_quick_analysis()

if __name__ == "__main__":
    main()