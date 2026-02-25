#!/usr/bin/env python3
"""
Quick Start Script for Brahan Engine
====================================

This script helps you quickly set up and start the Brahan Engine.
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Brahan Engine Quick Start")
    print("=" * 50)
    print()

    # Check current directory
    current_dir = Path.cwd()
    engine_dir = Path(__file__).parent

    if current_dir != engine_dir:
        print(f"⚠️  You're not in the engine directory.")
        print(f"   Current: {current_dir}")
        print(f"   Engine: {engine_dir}")
        print()
        change = input("Change to engine directory? (y/n): ").lower().strip()
        if change == 'y':
            os.chdir(engine_dir)
            print(f"✅ Changed to: {engine_dir}")
        else:
            print("⚠️  Continuing in current directory...")
        print()

    # Check if feed_engine.py exists
    feed_script = engine_dir / "feed_engine.py"
    if feed_script.exists():
        print("📋 Available Options:")
        print("1. Feed Engine - Interactive data feeding")
        print("2. Run Engine Directly - Quick analysis")
        print("3. View Documentation")
        print("4. Exit")
        print()

        choice = input("Choose an option (1-4): ").strip()

        if choice == '1':
            print("\n🔧 Starting Feed Engine...")
            print("   This will help you add documents and logs.")
            print("   Follow the interactive prompts.\n")
            os.system(f"{sys.executable} feed_engine.py")

        elif choice == '2':
            print("\n🚀 Starting Brahan Engine...")
            print("   Processing all files in pdf_files/, las_files/, log_files/\n")
            os.system(f"{sys.executable} run_unified_analysis.py")

        elif choice == '3':
            print("\n📖 Documentation:")
            docs = [
                "BRAHAN_ENGINE_README.md - Main documentation",
                "FEED_ENGINE_GUIDE.md - How to feed data",
                "INTEGRATION_GUIDE.md - Technical guide",
                "INTEGRATION_STATUS.md - Current status"
            ]
            for doc in docs:
                if (engine_dir / doc).exists():
                    print(f"   ✓ {doc}")
                else:
                    print(f"   ❌ {doc}")
            print("\n   Use 'cat <filename>' to view any document.")

        elif choice == '4':
            print("👋 Goodbye!")
            return

        else:
            print("❌ Invalid choice. Please run again and select 1-4.")

    else:
        print("❌ Feed engine script not found.")
        print("   Make sure you're in the correct directory.")
        print(f"   Expected: {engine_dir}")

if __name__ == "__main__":
    main()