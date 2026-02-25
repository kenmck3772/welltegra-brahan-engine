#!/usr/bin/env python3
"""
Brahan Engine - Analysis Runner
===============================

Main script to run the Brahan Engine - unified analysis across all platform components:
- WellArk Forensics
- WellABUILD
- Project Airtight

Usage:
    python run_unified_analysis.py [--config CONFIG_FILE] [--output OUTPUT_DIR]
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from UNIFIED_INTEGRATION import UnifiedForensicEngine, UnifiedConfig

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run unified forensic analysis")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument("--output", type=str, help="Output directory for results")
    parser.add_argument("--wellark", type=str, help="WellArk directory path")
    parser.add_argument("--wellabuild", type=str, help="WellABUILD directory path")
    parser.add_argument("--project-airtight", type=str, help="Project Airtight directory path")
    parser.add_argument("--temporal-window", type=int, default=365,
                       help="Temporal window in days (default: 365)")
    parser.add_argument("--predicate-threshold", type=float, default=0.8,
                       help="Predicate threshold (default: 0.8)")
    parser.add_argument("--no-audit", action="store_true",
                       help="Disable audit trail")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")

    return parser.parse_args()

def load_config(config_path):
    """Load configuration from JSON file"""
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        # Handle empty project_airtight_dir
        if 'project_airtight_dir' in config_data and config_data['project_airtight_dir'] == "":
            config_data['project_airtight_dir'] = None
        return UnifiedConfig(**config_data)
    return None

def save_config(config, output_dir):
    """Save configuration to JSON file"""
    config_data = {
        'root_dir': config.root_dir,
        'wellark_dir': config.wellark_dir,
        'wellabuild_dir': config.wellabuild_dir,
        'project_airtight_dir': config.project_airtight_dir,
        'temporal_window_days': config.temporal_window_days,
        'predicate_threshold': config.predicate_threshold,
        'spatial_tolerance': config.spatial_tolerance,
        'output_dir': config.output_dir,
        'export_osdu': config.export_osdu,
        'generate_visualization': config.generate_visualization,
        'enable_audit': config.enable_audit,
        'audit_signature': config.audit_signature,
        'retention_days': config.retention_days
    }

    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    return config_path

def validate_directories(config):
    """Validate that all required directories exist"""
    directories = [
        (config.wellark_dir, "WellArk"),
        (config.wellabuild_dir, "WellABUILD")
    ]

    # Only check Project Airtight if directory is specified
    if config.project_airtight_dir:
        directories.append((config.project_airtight_dir, "Project Airtight"))

    for directory, name in directories:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Required directory not found: {name}: {directory}")

def create_build_status_report(results, output_dir):
    """Create a comprehensive build status report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"build_status_report_{timestamp}.json")

    report = {
        'timestamp': datetime.now().isoformat(),
        'total_builds': len(results),
        'successful_builds': sum(1 for r in results if r.status.value == 'COMPLETED'),
        'failed_builds': sum(1 for r in results if r.status.value == 'FAILED'),
        'partial_builds': sum(1 for r in results if r.status.value == 'PARTIAL'),
        'build_details': []
    }

    for result in results:
        build_detail = {
            'build_type': result.build_type.value,
            'status': result.status.value,
            'timestamp': result.timestamp.isoformat(),
            'audit_hash': result.audit_hash,
            'results_summary': self._summarize_results(result.results)
        }
        report['build_details'].append(build_detail)

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    return report_path

def _summarize_results(results):
    """Create a summary of results"""
    summary = {}

    # Basic metrics
    if 'total_findings' in results:
        summary['total_findings'] = results['total_findings']

    # WellArk specific
    if 'gates' in results:
        summary['gates_analyzed'] = len(results['gates'])

    if 'cement_analysis' in results:
        summary['cement_issues'] = len(results['cement_analysis'])

    if 'predicate_results' in results:
        summary['predicates_evaluated'] = len(results['predicate_results'])

    # WellABUILD specific
    if 'material_findings' in results:
        summary['material_audit_findings'] = len(results['material_findings'])

    if 'cement_pressure_findings' in results:
        summary['cement_pressure_findings'] = len(results['cement_pressure_findings'])

    if 'pattern_findings' in results:
        summary['pattern_findings'] = len(results['pattern_findings'])

    # Project Airtight specific
    if 'documents_processed' in results:
        summary['documents_processed'] = results['documents_processed']

    if 'key_findings' in results:
        summary['document_findings'] = results['key_findings']

    return summary

def main():
    """Main execution function"""
    args = parse_arguments()

    # Load or create configuration
    config = load_config(args.config)
    if config is None:
        print("🔧 Creating default configuration...")
        config = UnifiedConfig()

    # Override configuration with command line arguments
    if args.wellark:
        config.wellark_dir = args.wellark
    if args.wellabuild:
        config.wellabuild_dir = args.wellabuild
    if args.project_airtight:
        config.project_airtight_dir = args.project_airtight
    if args.output:
        config.output_dir = args.output
    if args.temporal_window:
        config.temporal_window_days = args.temporal_window
    if args.predicate_threshold:
        config.predicate_threshold = args.predicate_threshold
    if args.no_audit:
        config.enable_audit = False
        config.audit_signature = False

    # Validate directories
    try:
        validate_directories(config)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Display configuration
    print("🔧 Unified Analysis Configuration:")
    print(f"  WellArk Directory: {config.wellark_dir}")
    print(f"  WellABUILD Directory: {config.wellabuild_dir}")
    print(f"  Project Airtight Directory: {config.project_airtight_dir}")
    print(f"  Output Directory: {config.output_dir}")
    print(f"  Temporal Window: {config.temporal_window_days} days")
    print(f"  Predicate Threshold: {config.predicate_threshold}")
    print(f"  Audit Trail: {'Enabled' if config.enable_audit else 'Disabled'}")
    print()

    # Save configuration
    config_path = save_config(config, config.output_dir)
    print(f"📄 Configuration saved to: {config_path}")
    print()

    # Run analysis
    print("🚀 Starting Unified Forensic Analysis...")
    print("=" * 60)

    if args.verbose:
        print("Verbose mode enabled - detailed output")

    # Initialize engine
    engine = UnifiedForensicEngine(config)

    # Run unified analysis
    try:
        results = engine.run_unified_analysis()

        # Generate status report
        report_path = create_build_status_report(results, config.output_dir)
        print(f"\n📊 Build status report: {report_path}")

        # Summary
        print("\n" + "=" * 60)
        print("🎯 EXECUTION SUMMARY")
        print("=" * 60)

        for result in results:
            status_icon = "✅" if result.status.value == "COMPLETED" else "❌"
            build_name = result.build_type.value.upper()
            print(f"{status_icon} {build_name}: {result.status.value}")

            if args.verbose and 'error' in result.results:
                print(f"   Error: {result.results['error']}")

            if result.audit_hash:
                print(f"   🔗 Audit: {result.audit_hash[:16]}...")

        print(f"\n⏱️  Total execution time: {time.time() - engine.start_time:.2f} seconds")

        # Check for any failed builds
        failed_builds = [r for r in results if r.status.value != "COMPLETED"]
        if failed_builds:
            print(f"\n⚠️  {len(failed_builds)} build(s) completed with warnings")
            for failed in failed_builds:
                print(f"   - {failed.build_type.value}: {failed.status.value}")

        print("\n✅ Analysis complete. Check output directory for detailed results.")

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()