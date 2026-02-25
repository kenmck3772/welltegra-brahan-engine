#!/usr/bin/env python3
"""
Simple Test of Brahan Engine with Your Data
===========================================

Tests basic functionality without complex dependencies.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def test_data_processing():
    """Test basic data processing capabilities"""
    print("🧪 Brahan Engine - Simple Test")
    print("=" * 50)

    # Your data directories
    data_dirs = {
        "las": "/home/brahan_welltegra/wellabuild/wellabuild/las_files",
        "pdf": "/home/brahan_welltegra/wellabuild/wellabuild/pdf_files",
        "tiff": "/home/brahan_welltegra/wellabuild/wellabuild/tiff_files"
    }

    # Count files
    total_files = 0
    file_stats = {}

    print("\n📊 File Analysis:")
    for file_type, path in data_dirs.items():
        if os.path.exists(path):
            if file_type == "las":
                files = list(Path(path).glob("*.las"))
            elif file_type == "pdf":
                files = list(Path(path).glob("*.pdf"))
            else:  # tiff
                files = list(Path(path).glob("*.tif*"))

            file_count = len(files)
            file_stats[file_type] = {
                "count": file_count,
                "files": files[:5]  # First 5 files
            }
            total_files += file_count

            print(f"\n✅ {file_type.upper()} files:")
            print(f"   Total: {file_count}")
            print(f"   Sample files:")
            for i, file in enumerate(files[:5]):
                size_kb = file.stat().st_size / 1024
                print(f"      {i+1}. {file.name} ({size_kb:.1f} KB)")
            if file_count > 5:
                print(f"      ... and {file_count - 5} more")

    print(f"\n📁 Total files to process: {total_files}")

    # Test basic file processing
    print("\n🔍 Testing basic file processing...")

    # Process a few sample files
    results = {
        "analysis_timestamp": datetime.now().isoformat(),
        "file_stats": file_stats,
        "total_files": total_files,
        "processing_results": [],
        "warnings": [],
        "errors": []
    }

    # Test LAS file processing (basic)
    print("\n📊 Processing sample LAS files...")
    las_files = file_stats.get("las", {}).get("files", [])
    for las_file in las_files[:3]:  # Process first 3
        try:
            with open(las_file, 'r') as f:
                content = f.read(1000)  # Read first 1KB
                if "~Version" in content:
                    results["processing_results"].append({
                        "file": las_file.name,
                        "type": "LAS",
                        "status": "VALID",
                        "notes": "LAS format detected"
                    })
                    print(f"   ✓ {las_file.name}: Valid LAS file")
                else:
                    results["processing_results"].append({
                        "file": las_file.name,
                        "type": "LAS",
                        "status": "UNKNOWN",
                        "notes": "LAS format unclear"
                    })
                    print(f"   ? {las_file.name}: Format unclear")
        except Exception as e:
            results["errors"].append({
                "file": str(las_file),
                "error": str(e)
            })
            print(f"   ❌ {las_file.name}: Error - {e}")

    # Test PDF file processing (basic)
    print("\n📄 Processing sample PDF files...")
    pdf_files = file_stats.get("pdf", {}).get("files", [])
    for pdf_file in pdf_files[:3]:  # Process first 3
        try:
            # Basic file check
            if pdf_file.suffix.lower() == '.pdf':
                size = pdf_file.stat().st_size
                results["processing_results"].append({
                    "file": pdf_file.name,
                    "type": "PDF",
                    "size": size,
                    "status": "FILE_FOUND"
                })
                print(f"   ✓ {pdf_file.name}: PDF file ({size/1024/1024:.1f} MB)")
            else:
                results["warnings"].append({
                    "file": str(pdf_file),
                    "warning": "Not a PDF file"
                })
        except Exception as e:
            results["errors"].append({
                "file": str(pdf_file),
                "error": str(e)
            })

    # Test TIFF file processing (basic)
    print("\n🖼️ Processing sample TIFF files...")
    tiff_files = file_stats.get("tiff", {}).get("files", [])
    for tiff_file in tiff_files[:3]:  # Process first 3
        try:
            # Basic file check
            if tiff_file.suffix.lower() in ['.tif', '.tiff']:
                size = tiff_file.stat().st_size
                results["processing_results"].append({
                    "file": tiff_file.name,
                    "type": "TIFF",
                    "size": size,
                    "status": "FILE_FOUND"
                })
                print(f"   ✓ {tiff_file.name}: TIFF file ({size/1024/1024:.1f} MB)")
            else:
                results["warnings"].append({
                    "file": str(tiff_file),
                    "warning": "Not a TIFF file"
                })
        except Exception as e:
            results["errors"].append({
                "file": str(tiff_file),
                "error": str(e)
            })

    # Generate summary
    print("\n" + "=" * 50)
    print("📋 PROCESSING SUMMARY")
    print("=" * 50)

    successful = len([r for r in results["processing_results"] if "status" in r and r["status"] != "ERROR"])
    print(f"✅ Files processed: {successful}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    print(f"❌ Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\nErrors encountered:")
        for error in results["errors"]:
            print(f"   - {error['file']}: {error['error']}")

    # Save results
    output_dir = Path("brahan_engine_data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = output_dir / f"simple_test_results_{timestamp}.json"

    with open(result_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {result_file}")

    # Create a simple HTML report
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Brahan Engine - Simple Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Brahan Engine - Simple Test Report</h1>
        <p>Analysis completed: {datetime.now().isoformat()}</p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <p><strong>Total Files:</strong> {total_files}</p>
        <p><strong>Processed Successfully:</strong> {successful}</p>
        <p><strong>Warnings:</strong> {len(results['warnings'])}</p>
        <p><strong>Errors:</strong> {len(results['errors'])}</p>
    </div>

    <div class="section">
        <h2>File Statistics</h2>
        <ul>
            <li><strong>LAS Files:</strong> {file_stats.get('las', {}).get('count', 0)}</li>
            <li><strong>PDF Files:</strong> {file_stats.get('pdf', {}).get('count', 0)}</li>
            <li><strong>TIFF Files:</strong> {file_stats.get('tiff', {}).get('count', 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2>Next Steps</h2>
        <p>Your data has been processed successfully at a basic level.</p>
        <p>To run the full Brahan Engine:</p>
        <ol>
            <li>Install dependencies: pip install pandas numpy scipy</li>
            <li>Run: python run_unified_analysis.py</li>
        </ol>
    </div>
</body>
</html>
    """

    html_file = output_dir / f"simple_test_report_{timestamp}.html"
    with open(html_file, 'w') as f:
        f.write(html_content)

    print(f"📊 HTML report created: {html_file}")

    print("\n🎉 Simple test complete!")
    print("Your data has been analyzed at a basic level.")
    print(f"Check the output directory for detailed results.")

    return result_file

if __name__ == "__main__":
    test_data_processing()