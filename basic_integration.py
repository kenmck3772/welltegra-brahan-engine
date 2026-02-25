#!/usr/bin/env python3
"""
Basic Integration Test
======================

A simple integration that demonstrates the unification of the builds
without requiring complex dependencies.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def get_build_info():
    """Get information about both builds"""
    builds = {}

    # WellABUILD info
    wellabuild_dir = '/home/brahan_welltegra/wellabuild/wellabuild'
    if os.path.exists(wellabuild_dir):
        builds['wellabuild'] = {
            'path': wellabuild_dir,
            'exists': True,
            'modules': [],
            'python_files': []
        }

        # List Python files
        for file in os.listdir(wellabuild_dir):
            if file.endswith('.py'):
                builds['wellabuild']['python_files'].append(file)

        # Check for key modules
        key_modules = [
            'wellabuild_sdk.py',
            'forensic_harvester.py',
            'material_audit.py',
            'run_full_audit.py'
        ]

        for module in key_modules:
            if os.path.exists(os.path.join(wellabuild_dir, module)):
                builds['wellabuild']['modules'].append(module)

    # WellArk info (treating current directory as WellArk)
    wellark_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(wellark_dir):
        builds['wellark'] = {
            'path': wellark_dir,
            'exists': True,
            'modules': [],
            'python_files': []
        }

        # List Python files
        for file in os.listdir(wellark_dir):
            if file.endswith('.py'):
                builds['wellark']['python_files'].append(file)

        # Check for integration scripts
        integration_modules = [
            'UNIFIED_INTEGRATION.py',
            'run_unified_analysis.py',
            'simple_runner.py'
        ]

        for module in integration_modules:
            if os.path.exists(os.path.join(wellark_dir, module)):
                builds['wellark']['modules'].append(module)

    return builds

def analyze_build_structure(builds):
    """Analyze and provide insights about the builds"""
    analysis = {
        'total_builds': len(builds),
        'functional_builds': 0,
        'key_features': {},
        'integration_points': []
    }

    for name, build in builds.items():
        if build['exists']:
            analysis['functional_builds'] += 1

            # Identify key features based on available modules
            features = []

            if name == 'wellabuild':
                if 'wellabuild_sdk.py' in build['modules']:
                    features.append('Physics-based integrity engine')
                if 'forensic_harvester.py' in build['modules']:
                    features.append('Forensic data collection')
                if 'material_audit.py' in build['modules']:
                    features.append('Material integrity verification')
                if 'cement_pressure_audit.py' in build['modules']:
                    features.append('Cement and pressure analysis')

            elif name == 'wellark':
                if 'UNIFIED_INTEGRATION.py' in build['modules']:
                    features.append('Unified integration framework')
                if 'run_unified_analysis.py' in build['modules']:
                    features.append('CLI interface')
                if 'simple_runner.py' in build['modules']:
                    features.append('Simplified execution')

            analysis['key_features'][name] = features

            # Suggest integration points
            if name == 'wellabuild':
                analysis['integration_points'].extend([
                    'SDK for core forensic operations',
                    'Harvester for data collection',
                    'Audit modules for integrity checks'
                ])
            elif name == 'wellark':
                analysis['integration_points'].extend([
                    'Integration framework orchestration',
                    'Configuration management',
                    'Output consolidation'
                ])

    return analysis

def generate_integration_plan(analysis):
    """Generate a step-by-step integration plan"""
    plan = {
        'phase': 'Preparation',
        'steps': [],
        'dependencies': [],
        'next_actions': []
    }

    # Phase 1: Foundation
    plan['steps'] = [
        {
            'step': 1,
            'action': 'Install missing dependencies',
            'details': 'Install pandas, numpy, scipy for WellABUILD',
            'critical': True
        },
        {
            'step': 2,
            'action': 'Verify module imports',
            'details': 'Test all critical modules can be imported',
            'critical': True
        },
        {
            'step': 3,
            'action': 'Create unified workspace',
            'details': 'Set up common directory structure and paths',
            'critical': False
        }
    ]

    # Dependencies
    plan['dependencies'] = [
        'Python 3.8+',
        'pandas >= 1.3.0',
        'numpy >= 1.21.0',
        'scipy >= 1.7.0',
        'Required Python packages from both builds'
    ]

    # Next actions
    plan['next_actions'] = [
        'Run: pip install pandas numpy scipy',
        'Test module imports with basic_integration.py',
        'Execute: python run_unified_analysis.py --dry-run'
    ]

    return plan

def create_integration_report():
    """Create a comprehensive integration report"""
    print("🔍 Analyzing Build Integration...")

    # Get build information
    builds = get_build_info()

    # Analyze structure
    analysis = analyze_build_structure(builds)

    # Generate plan
    plan = generate_integration_plan(analysis)

    # Create report
    report = {
        'generation_timestamp': datetime.now().isoformat(),
        'builds': builds,
        'analysis': analysis,
        'integration_plan': plan,
        'recommendations': []
    }

    # Add recommendations
    if analysis['functional_builds'] < 2:
        report['recommendations'].append("Ensure both builds are properly installed")

    if len(analysis['key_features']) < 2:
        report['recommendations'].append("Check build module availability")

    # Save report
    output_dir = os.path.join(os.path.dirname(__file__), "integration_reports")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"integration_report_{timestamp}.json")

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    return report_file

def display_summary(report):
    """Display a summary of the integration analysis"""
    print("\n" + "=" * 60)
    print("📊 INTEGRATION ANALYSIS SUMMARY")
    print("=" * 60)

    builds = report['builds']
    analysis = report['analysis']

    print(f"\n🏗️  Build Status:")
    for name, build in builds.items():
        status = "✅" if build['exists'] else "❌"
        print(f"   {status} {name.upper()}")
        print(f"      Path: {build['path']}")
        print(f"      Python files: {len(build['python_files'])}")
        print(f"      Key modules: {len(build['modules'])}")

    print(f"\n🔍 Analysis:")
    print(f"   Total builds found: {analysis['total_builds']}")
    print(f"   Functional builds: {analysis['functional_builds']}")

    print(f"\n🎯 Key Features:")
    for name, features in analysis['key_features'].items():
        print(f"   {name.upper()}:")
        for feature in features:
            print(f"      • {feature}")

    print(f"\n📋 Integration Steps:")
    for step in report['integration_plan']['steps']:
        critical = " [CRITICAL]" if step['critical'] else ""
        print(f"   {step['step']}. {step['action']}{critical}")
        print(f"      {step['details']}")

    print(f"\n🚀 Next Actions:")
    for action in report['integration_plan']['next_actions']:
        print(f"   • {action}")

    if report['recommendations']:
        print(f"\n⚠️  Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

    print(f"\n📄 Full report saved to: {report['integration_plan']['steps'][-1]['details']}")

def main():
    """Main execution function"""
    print("🧪 Basic Integration Analysis")
    print("=" * 60)

    start_time = time.time()

    try:
        # Create integration report
        report_file = create_integration_report()

        # Display summary
        with open(report_file, 'r') as f:
            report = json.load(f)

        display_summary(report)

        execution_time = time.time() - start_time
        print(f"\n⏱️  Analysis completed in {execution_time:.2f} seconds")

        print("\n✅ Integration analysis complete!")

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()