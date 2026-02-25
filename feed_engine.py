#!/usr/bin/env python3
"""
Brahan Engine Data Feeder
===========================

This script helps you prepare and feed documents/logs to the Brahan Engine.
"""

import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

class BrahanEngineFeeder:
    """Helper class to feed data to Brahan Engine"""

    def __init__(self, engine_dir=None):
        self.engine_dir = engine_dir or os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.engine_dir, "brahan_engine_data")
        self.supported_extensions = {
            'pdf': ['.pdf'],
            'las': ['.las'],
            'tiff': ['.tif', '.tiff'],
            'log': ['.log', '.txt', '.csv']
        }

    def setup_directories(self):
        """Create directory structure for data feeding"""
        print("🔧 Setting up Brahan Engine data directories...")

        # Create main data directory
        os.makedirs(self.data_dir, exist_ok=True)

        # Create subdirectories
        subdirs = ['pdf_files', 'las_files', 'tiff_files', 'log_files', 'output']
        for subdir in subdirs:
            os.makedirs(os.path.join(self.data_dir, subdir), exist_ok=True)

        print(f"✅ Data directory created: {self.data_dir}")

        # List created directories
        for subdir in subdirs:
            path = os.path.join(self.data_dir, subdir)
            print(f"   - {path}")

        return True

    def check_existing_files(self):
        """Check what files are already in the directories"""
        print("\n📁 Checking existing files...")

        results = {}
        for file_type, subdir in [('pdf', 'pdf_files'), ('las', 'las_files'), ('tiff', 'tiff_files'), ('log', 'log_files')]:
            subdir_path = os.path.join(self.data_dir, subdir)
            if os.path.exists(subdir_path):
                files = [f for f in os.listdir(subdir_path)
                        if any(f.endswith(ext) for ext in self.supported_extensions[file_type])]
                results[file_type] = files
                print(f"   {file_type.upper()}: {len(files)} files")
                for file in files[:5]:  # Show first 5
                    print(f"      - {file}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
            else:
                results[file_type] = []
                print(f"   {file_type.upper()}: 0 files")

        return results

    def add_documents(self, source_path, file_type=None):
        """Add documents from source directory"""
        print(f"\n📂 Adding documents from: {source_path}")

        if not os.path.exists(source_path):
            print(f"❌ Source path does not exist: {source_path}")
            return False

        # Determine file type based on source or extension
        if file_type:
            target_dir = os.path.join(self.data_dir, f"{file_type}_files")
            if file_type not in self.supported_extensions:
                print(f"❌ Unsupported file type: {file_type}")
                return False
        else:
            # Auto-detect file type
            files_added = 0
            for file_type, extensions in self.supported_extensions.items():
                target_dir = os.path.join(self.data_dir, f"{file_type}_files")
                for file in os.listdir(source_path):
                    if any(file.endswith(ext) for ext in extensions):
                        src = os.path.join(source_path, file)
                        dst = os.path.join(target_dir, file)
                        shutil.copy2(src, dst)
                        files_added += 1
                        print(f"   ✓ Copied: {file}")
            print(f"✅ Added {files_added} files (auto-detected type)")
            return True

        # Copy files of specific type
        files_copied = 0
        for file in os.listdir(source_path):
            if any(file.endswith(ext) for ext in self.supported_extensions[file_type]):
                src = os.path.join(source_path, file)
                dst = os.path.join(target_dir, file)
                shutil.copy2(src, dst)
                files_copied += 1
                print(f"   ✓ Copied: {file}")

        print(f"✅ Added {files_copied} {file_type.upper()} files")
        return True

    def add_single_file(self, file_path, file_type=None):
        """Add a single file to the engine"""
        print(f"\n📄 Adding file: {file_path}")

        if not os.path.exists(file_path):
            print(f"❌ File does not exist: {file_path}")
            return False

        # Auto-detect file type if not specified
        if not file_type:
            for ftype, extensions in self.supported_extensions.items():
                if any(file_path.endswith(ext) for ext in extensions):
                    file_type = ftype
                    break

            if not file_type:
                print("❌ Cannot determine file type")
                return False

        # Copy file
        target_dir = os.path.join(self.data_dir, f"{file_type}_files")
        os.makedirs(target_dir, exist_ok=True)

        filename = os.path.basename(file_path)
        dst_path = os.path.join(target_dir, filename)
        shutil.copy2(file_path, dst_path)

        print(f"✅ Added {file_type.upper()} file: {filename}")
        return True

    def create_config_file(self):
        """Create a configuration file for the engine"""
        config = {
            "input_directories": {
                "pdf_files": os.path.join(self.data_dir, "pdf_files"),
                "las_files": os.path.join(self.data_dir, "las_files"),
                "log_files": os.path.join(self.data_dir, "log_files")
            },
            "analysis_parameters": {
                "temporal_window_days": 365,
                "predicate_threshold": 0.8,
                "enable_pdf_ocr": True,
                "enable_las_validation": True,
                "enable_log_analysis": True
            },
            "output_settings": {
                "output_directory": os.path.join(self.data_dir, "output"),
                "generate_visualization": True,
                "export_osdu": False,
                "enable_audit": True
            }
        }

        config_path = os.path.join(self.engine_dir, "feeder_config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n📄 Configuration saved to: {config_path}")
        return config_path

    def run_engine(self, config_file=None):
        """Run the Brahan Engine with prepared data"""
        print("\n🚀 Running Brahan Engine...")

        # Change to engine directory
        os.chdir(self.engine_dir)

        # Build command
        cmd = [sys.executable, "run_unified_analysis.py"]
        if config_file:
            cmd.extend(["--config", config_file])

        print(f"   Command: {' '.join(cmd)}")
        print("   Starting analysis...")

        # Run the engine
        try:
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Brahan Engine completed successfully!")
                if result.stdout:
                    print("\nOutput:")
                    print(result.stdout)
            else:
                print("❌ Brahan Engine encountered errors:")
                print(result.stderr)

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running engine: {e}")
            return False

    def preview_data(self):
        """Show a preview of what will be analyzed"""
        print("\n📊 Data Preview:")
        print("=" * 50)

        total_files = 0
        for file_type in ['pdf', 'las', 'log']:
            subdir = os.path.join(self.data_dir, f"{file_type}_files")
            if os.path.exists(subdir):
                files = [f for f in os.listdir(subdir)
                        if any(f.endswith(ext) for ext in self.supported_extensions[file_type])]
                print(f"{file_type.upper()}: {len(files)} files")
                total_files += len(files)

                # Show file sizes
                total_size = 0
                for file in files:
                    file_path = os.path.join(subdir, file)
                    total_size += os.path.getsize(file_path)

                if total_size > 0:
                    size_mb = total_size / (1024 * 1024)
                    print(f"   Total size: {size_mb:.2f} MB")

        print(f"\nTotal files to process: {total_files}")
        print(f"Data directory: {self.data_dir}")

        return total_files > 0

def main():
    """Main feeder interface"""
    print("🔧 Brahan Engine Data Feeder")
    print("=" * 50)

    feeder = BrahanEngineFeeder()

    # Setup directories
    feeder.setup_directories()

    # Check existing files
    existing_files = feeder.check_existing_files()

    # Menu
    while True:
        print("\n" + "=" * 50)
        print("📋 Brahan Engine Feeder Menu")
        print("=" * 50)
        print("1. Add single file")
        print("2. Add directory of files")
        print("3. Preview data")
        print("4. Run Brahan Engine")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            # Add single file
            file_path = input("Enter file path: ").strip()
            if file_path:
                feeder.add_single_file(file_path)
                feeder.preview_data()

        elif choice == '2':
            # Add directory
            dir_path = input("Enter directory path: ").strip()
            file_type = input("File type (pdf/las/log) [auto]: ").strip().lower()

            if not file_type or file_type not in ['pdf', 'las', 'log']:
                file_type = None

            if dir_path:
                feeder.add_documents(dir_path, file_type)
                feeder.preview_data()

        elif choice == '3':
            # Preview data
            feeder.preview_data()

        elif choice == '4':
            # Run engine
            config_file = feeder.create_config_file()
            if feeder.preview_data():
                feeder.run_engine(config_file)
            else:
                print("❌ No data to process. Add files first.")

        elif choice == '5':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()