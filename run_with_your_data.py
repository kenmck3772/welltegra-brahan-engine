#!/usr/bin/env python3
"""
Run Brahan Engine with Your Data
================================

This script will automatically find and use your LAS, PDF, and TIFF folders.
"""

import os
import sys
from pathlib import Path
import subprocess

def find_your_folders():
    """Find your data folders"""
    print("🔍 Looking for your data folders...")

    # Common locations
    search_paths = [
        Path.home(),
        Path.cwd(),
        Path.cwd().parent,
        Path("/home/brahan_welltegra")
    ]

    folders = {}

    # Look for LAS folder
    for search_path in search_paths:
        las_found = False
        for pattern in ["las", "LAS", "Logs", "LOGS"]:
            test_path = search_path / pattern
            if test_path.exists() and any(test_path.glob("*.las")):
                folders["las"] = test_path
                print(f"✅ Found LAS folder: {test_path}")
                las_found = True
                break
        if las_found:
            break

    # Look for PDF folder
    for search_path in search_paths:
        pdf_found = False
        for pattern in ["pdf", "PDF", "Documents", "docs"]:
            test_path = search_path / pattern
            if test_path.exists() and any(test_path.glob("*.pdf")):
                folders["pdf"] = test_path
                print(f"✅ Found PDF folder: {test_path}")
                pdf_found = True
                break
        if pdf_found:
            break

    # Look for TIFF folder
    for search_path in search_paths:
        tiff_found = False
        for pattern in ["tiffs", "TIFFS", "tiff", "TIFF", "Images"]:
            test_path = search_path / pattern
            if test_path.exists() and any(test_path.glob("*.tif*")):
                folders["tiff"] = test_path
                print(f"✅ Found TIFF folder: {test_path}")
                tiff_found = True
                break
        if tiff_found:
            break

    return folders

def count_files(folders):
    """Count files in each folder"""
    counts = {}
    for file_type, folder in folders.items():
        if file_type == "las":
            counts[file_type] = len(list(folder.glob("*.las")))
        elif file_type == "pdf":
            counts[file_type] = len(list(folder.glob("*.pdf")))
        elif file_type == "tiff":
            counts[file_type] = len(list(folder.glob("*.tif*")))

    return counts

def setup_engine(folders):
    """Setup the engine with your folders"""
    print("\n🔧 Setting up Brahan Engine...")

    # Create engine data directory
    engine_data = Path("brahan_engine_data")
    engine_data.mkdir(exist_ok=True)

    # Create subdirectories
    (engine_data / "las_files").mkdir(exist_ok=True)
    (engine_data / "pdf_files").mkdir(exist_ok=True)
    (engine_data / "tiff_files").mkdir(exist_ok=True)
    (engine_data / "output").mkdir(exist_ok=True)

    print(f"✅ Engine directory created: {engine_data}")

    # Copy files
    print("\n📂 Copying files...")
    for file_type, folder in folders.items():
        target_dir = engine_data / f"{file_type}_files"
        files_copied = 0

        for file_path in folder.glob(f"*{'las' if file_type == 'las' else 'pdf' if file_type == 'pdf' else 'tif*'}"):
            if file_path.is_file():
                import shutil
                shutil.copy2(file_path, target_dir)
                files_copied += 1

        print(f"   ✓ Copied {files_copied} {file_type.upper()} files")

    return engine_data

def run_analysis():
    """Run the Brahan Engine"""
    print("\n🚀 Running Brahan Engine Analysis...")
    print("This will analyze your LAS, PDF, and TIFF files.")
    print("Please wait... This may take a few minutes.")
    print()

    try:
        result = subprocess.run([
            sys.executable, "run_unified_analysis.py"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        if result.returncode == 0:
            print("✅ Analysis completed successfully!")
            print("\n" + "="*50)
            print("📊 Results Summary")
            print("="*50)

            # Look for output files
            output_dir = Path("brahan_engine_data/output")
            if output_dir.exists():
                json_files = list(output_dir.glob("*.json"))
                print(f"\n📄 Output files created ({len(json_files)}):")
                for json_file in json_files:
                    print(f"   - {json_file.name}")

                # Show latest results
                if json_files:
                    latest = max(json_files, key=lambda x: x.stat().st_mtime)
                    print(f"\n📋 Latest results: {latest.name}")
                    try:
                        import json
                        with open(latest, 'r') as f:
                            data = json.load(f)
                            if 'summary' in data:
                                print("\nSummary:")
                                for key, value in data['summary'].items():
                                    print(f"   {key}: {value}")
                    except:
                        pass

            return True
        else:
            print("❌ Analysis failed with errors:")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("❌ Analysis timed out after 5 minutes")
        print("The engine may still be running in the background.")
        return False
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        return False

def main():
    """Main function"""
    print("🎯 Brahan Engine - Run with Your Data")
    print("=" * 50)
    print()
    print("This script will:")
    print("1. Find your LAS, PDF, and TIFF folders")
    print("2. Copy files to the engine")
    print("3. Run forensic analysis")
    print("4. Show you the results")
    print()

    # Find your folders
    folders = find_your_folders()

    if len(folders) < 3:
        print("❌ Could not find all required folders.")
        print("Found:")
        for file_type, folder in folders.items():
            print(f"   {file_type.upper()}: {folder}")
        print()

        # Ask for manual input
        while len(folders) < 3:
            missing = []
            if "las" not in folders:
                missing.append("LAS")
            if "pdf" not in folders:
                missing.append("PDF")
            if "tiff" not in folders:
                missing.append("TIFF")

            print(f"Please provide paths for: {', '.join(missing)}")

            for file_type in missing:
                path = input(f"Enter {file_type} folder path: ").strip()
                if path:
                    folder_path = Path(path).expanduser()
                    if folder_path.exists():
                        folders[file_type] = folder_path
                        print(f"✅ Using {file_type} folder: {folder_path}")
                    else:
                        print("❌ Path does not exist")

    # Count files
    counts = count_files(folders)
    print(f"\n📊 File counts:")
    print(f"   LAS files: {counts.get('las', 0)}")
    print(f"   PDF files: {counts.get('pdf', 0)}")
    print(f"   TIFF files: {counts.get('tiff', 0)}")
    print(f"   Total: {sum(counts.values())}")

    if sum(counts.values()) == 0:
        print("❌ No files found. Please check your folders.")
        return

    # Ask to proceed
    proceed = input("\nProceed with analysis? (y/n): ").lower().strip()
    if proceed != 'y':
        print("❌ Analysis cancelled.")
        return

    # Setup and run
    engine_data = setup_engine(folders)
    run_analysis()

if __name__ == "__main__":
    main()