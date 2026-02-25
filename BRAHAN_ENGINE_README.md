# Brahan Engine - Unified Forensic Analysis Platform

## Overview

The **Brahan Engine** is a comprehensive forensic analysis platform that unifies multiple forensic analysis capabilities into a single cohesive system. Engineered for advanced wellbore integrity analysis, it combines cutting-edge forensic techniques with AI-powered pattern recognition.

## Platform Architecture

### Core Components

1. **WellArk Forensics Module**
   - 7-gate forensic engine for automated risk detection
   - LAS file processing and log analysis
   - PDF metadata extraction and OCR
   - OSDU-compliant data export
   - ISO 14224 equipment taxonomy integration

2. **WellABUILD Module**
   - Physics-based integrity engine
   - Material audit with PE signature matching
   - Cement and pressure analysis
   - AI-powered pattern recognition (BrainSearch)
   - 3D spatial drift mapping

3. **Project Airtight Module**
   - Document intelligence processing
   - Procurement pattern analysis
   - Relationship mapping
   - Anomaly detection algorithms
   - Intelligence report generation

## Features

### 🔍 Multi-Dimensional Analysis
- **Temporal Analysis**: Year-long pattern detection and historical data processing
- **Spatial Analysis**: 3D wellbore modeling with depth corrections
- **Material Analysis**: Cement integrity and equipment verification
- **Document Analysis**: PDF and document intelligence processing

### 🛡️ Forensic Capabilities
- **7-Gate Risk Detection**: Automated forensic gates for comprehensive risk assessment
- **Predicate System**: 569 integrated predicates across 5 forensic domains
- **Material Substitution Detection**: Advanced equipment authenticity verification
- **Data Tampering Detection**: Anomaly detection in operational data

### 🎯 Integration Features
- **Unified Configuration**: Centralized management system
- **Cross-Build Correlation**: Automatic pattern matching across all components
- **Audit Trail**: SHA256 signatures for chain of custody
- **Flexible Output**: JSON-based results with multiple export formats

## Quick Start

### Prerequisites
```bash
# Install required dependencies
pip install pandas numpy scipy
```

### Basic Usage

```bash
# Run the Brahan Engine
python run_unified_analysis.py

# With custom configuration
python run_unified_analysis.py --config custom_config.json

# With custom output directory
python run_unified_analysis.py --output /path/to/output

# Verbose output
python run_unified_analysis.py --verbose

# Disable audit trail
python run_unified_analysis.py --no-audit
```

### Analysis Options

```bash
# Run specific build paths
python run_unified_analysis.py \
  --wellark /path/to/wellark \
  --wellabuild /path/to/wellabuild \
  --project-airtight /path/to/project-airtight

# Adjust analysis parameters
python run_unified_analysis.py \
  --temporal-window 180 \
  --predicate-threshold 0.7
```

## Output Structure

### Primary Outputs
- `brahan_engine_results_YYYYMMDD_HHMMSS.json` - Unified analysis results
- `audit_trail_YYYYMMDD_HHMMSS.json` - Complete audit trail
- `build_status_report_YYYYMMDD_HHMMSS.json` - Component status report
- `config.json` - Analysis configuration

### Result Format
```json
{
  "analysis_timestamp": "2024-01-01T12:00:00",
  "platform_version": "Brahan Engine v1.0",
  "component_results": {
    "wellark": {
      "status": "COMPLETED",
      "findings": 150,
      "risk_score": 0.85
    },
    "wellabuild": {
      "status": "COMPLETED",
      "integrity_score": 0.92,
      "anomalies": 7
    },
    "project_airtight": {
      "status": "COMPLETED",
      "documents_processed": 234,
      "intelligence_findings": 15
    }
  },
  "unified_score": 0.89,
  "audit_signature": "sha256:..."
}
```

## Configuration

### Default Configuration
```python
{
  "temporal_window_days": 365,
  "predicate_threshold": 0.8,
  "spatial_tolerance": 0.001,
  "export_osdu": true,
  "generate_visualization": true,
  "enable_audit": true,
  "audit_signature": true
}
```

### Custom Configuration File
Create a JSON file to customize the Brahan Engine:

```json
{
  "root_dir": "/home/brahan_welltegra",
  "wellark_dir": "/path/to/wellark",
  "wellabuild_dir": "/path/to/wellabuild",
  "project_airtight_dir": "/path/to/project-airtight",
  "temporal_window_days": 180,
  "predicate_threshold": 0.7,
  "output_dir": "/custom/output/path",
  "export_osdu": false,
  "generate_visualization": true,
  "enable_audit": true,
  "retention_days": 365
}
```

## Advanced Usage

### Programmatic Interface
```python
from UNIFIED_INTEGRATION import BrahanEngine, UnifiedConfig

# Initialize engine
config = UnifiedConfig()
engine = BrahanEngine(config)

# Run specific analysis
results = engine.run_wellark_analysis()
results = engine.run_wellabuild_analysis()
results = engine.run_project_airtight_analysis()

# Get unified results
unified_results = engine.get_correlated_findings()
```

### Custom Correlation Logic
```python
def custom_correlation(results):
    # Implement custom correlation logic
    correlations = []
    # ... your implementation ...
    return correlations

# Use custom correlation
engine.set_correlation_logic(custom_correlation)
```

## Performance

### System Requirements
- Python 3.8+
- 8GB+ RAM (for large datasets)
- 100MB+ storage space
- Network connection for OSDU export (optional)

### Processing Times
- Basic Analysis: 30-60 seconds
- Full Dataset: 2-5 minutes
- Large LAS Files: 5-10 minutes

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install pandas numpy scipy
   ```

2. **Directory Not Found**
   - Verify build paths in configuration
   - Use absolute paths for reliability

3. **Memory Issues**
   - Reduce temporal window size
   - Process files in batches

### Debug Mode
```bash
# Enable verbose output
python run_unified_analysis.py --verbose

# Test configuration
python basic_integration.py
```

## Security

### Data Protection
- All data processed locally
- No external API calls (except OSDU export)
- Audit trail with SHA256 signatures
- Secure output file permissions

### Compliance
- Chain of custody documentation
- Tamper-proof logging
- Access control recommendations
- Privacy protection features

## Maintenance

### Regular Tasks
1. Update dependencies quarterly
2. Clean up old output files
3. Verify audit trail integrity
4. Monitor performance metrics

### Backup Strategy
- Regular configuration backups
- Version control integration scripts
- Archive important analysis results

## Support

### Documentation
- `INTEGRATION_GUIDE.md` - Comprehensive usage guide
- `BRAHAN_ENGINE_README.md` - This file
- `INTEGRATION_STATUS.md` - Current platform status

### Getting Help
1. Run diagnostic tests: `python basic_integration.py`
2. Check configuration: `python run_unified_analysis.py --dry-run`
3. Review audit logs for error details
4. Enable verbose mode for debugging

## Version History

### v1.0.0 (Current)
- Initial platform release
- Unified integration framework
- WellArk, WellABUILD, and Project Airtight integration
- CLI interface
- Audit trail implementation

---

**Brahan Engine** - Advanced Forensic Analysis Platform
*Engineered for Excellence*