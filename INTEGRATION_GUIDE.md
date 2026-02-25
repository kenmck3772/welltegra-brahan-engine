# Brahan Engine - Integration Guide

This guide explains the Brahan Engine - a unified forensic analysis platform that integrates multiple forensic analysis capabilities.

The Brahan Engine combines:
- WellArk Forensics (legacy processing)
- WellABUILD (modern framework)
- Project Airtight (document intelligence)

## Overview

The unified system combines the strengths of all three builds:

### 1. WellArk Forensics (Legacy)
- LAS file processing and log analysis
- PDF metadata extraction
- 7-gate forensic engine
- OSDU-compliant output
- ISO 14224 equipment taxonomy

### 2. WellABUILD (Modern)
- Physics-based integrity engine
- AI-powered pattern recognition
- Material audit capabilities
- 3D spatial drift mapping
- P&A readiness assessment

### 3. Project Airtight (Document Intelligence)
- Document metadata processing
- Procurement analysis
- Relationship mapping
- Anomaly detection
- Intelligence gathering

## Quick Start

### Installation
```bash
# Navigate to the unified analysis directory
cd /home/brahan_welltegra/wellark-forensics/welltegra-brahan-engine-main

# Run the unified analysis
python run_unified_analysis.py
```

### Advanced Usage
```bash
# Custom output directory
python run_unified_analysis.py --output /path/to/output

# Use custom configuration
python run_unified_analysis.py --config custom_config.json

# Specify build paths
python run_unified_analysis.py \
  --wellark /path/to/wellark \
  --wellabuild /path/to/wellabuild \
  --project-airtight /path/to/project_airtight

# Disable audit trail
python run_unified_analysis.py --no-audit

# Verbose output
python run_unified_analysis.py --verbose
```

## Directory Structure

```
welltegra-brahan-engine-main/
├── UNIFIED_INTEGRATION.py      # Main integration script
├── run_unified_analysis.py     # Runner with CLI interface
├── UNIFIED_CONFIG.py           # Configuration module
├── INTEGRATION_GUIDE.md       # This guide
├── src/                        # WellArk source modules
│   ├── forensic_gate_engine.py
│   ├── gr_cement_analyzer.py
│   ├── predicate_manager.py
│   └── ...
├── wellabuild/                 # Symlink to WellABUILD directory
├── output/                     # Analysis results
├── pdf_files/                  # PDF documents
└── las_files/                  # LAS log files
```

## Configuration

### Default Configuration
The system uses a default configuration that automatically detects build paths:

```python
config = UnifiedConfig(
    root_dir="/home/brahan_welltegra",
    temporal_window_days=365,
    predicate_threshold=0.8,
    spatial_tolerance=0.001,
    export_osdu=True,
    generate_visualization=True,
    enable_audit=True,
    audit_signature=True
)
```

### Custom Configuration
Create a JSON file to customize the configuration:

```json
{
  "root_dir": "/home/brahan_welltegra",
  "wellark_dir": "/custom/path/to/wellark-forensics",
  "wellabuild_dir": "/custom/path/to/wellabuild",
  "project_airtight_dir": "/custom/path/to/project-airtight",
  "temporal_window_days": 180,
  "predicate_threshold": 0.7,
  "spatial_tolerance": 0.005,
  "export_osdu": false,
  "generate_visualization": true,
  "enable_audit": true,
  "audit_signature": true,
  "retention_days": 180
}
```

## Execution Flow

### 1. Initialization
- Load configuration from file or defaults
- Validate all build directories exist
- Prepare output directory structure
- Initialize audit trail

### 2. WellArk Analysis
- Execute 7-gate forensic engine
- Process LAS files and logs
- Analyze cement integrity using GR logs
- Evaluate 569 predicates across 5 domains
- Generate OSDU-compliant output

### 3. WellABUILD Analysis
- Harvest forensic data from multiple sources
- Verify material integrity with PE signatures
- Audit cement and pressure for P&A readiness
- Run AI pattern recognition using BrainSearch
- Generate 3D spatial drift maps

### 4. Project Airtight Analysis
- Process document metadata
- Extract key relationships
- Analyze document authenticity
- Generate intelligence reports
- Map procurement patterns

### 5. Correlation & Integration
- Cross-correlate findings from all builds
- Identify common patterns and anomalies
- Generate unified audit trail
- Create consolidated reports

### 6. Output Generation
- Save unified results in JSON format
- Generate build status report
- Create visualization data
- Export audit trail
- Clean up temporary files

## Output Files

### Primary Outputs
- `unified_forensic_analysis_YYYYMMDD_HHMMSS.json`
- `audit_trail_YYYYMMDD_HHMMSS.json`
- `build_status_report_YYYYMMDD_HHMMSS.json`
- `config.json` (saved configuration)

### Output Structure
```json
{
  "analysis_timestamp": "2024-01-01T12:00:00",
  "build_type": "unified",
  "status": "COMPLETED",
  "results": {
    "execution_time": 45.2,
    "total_findings": 150,
    "correlated_findings": 23,
    "build_results": {
      "wellark": {...},
      "wellabuild": {...},
      "project_airtight": {...}
    },
    "correlations": [...]
  },
  "audit_hash": "sha256:..."
}
```

## Integration Features

### 1. Unified Audit Trail
- SHA256 signatures for all outputs
- Comprehensive execution logging
- Chain of custody documentation
- Retention policy management

### 2. Cross-Build Correlation
- Automatic pattern matching across builds
- Confidence scoring for correlations
- Anomaly detection integration
- Unified finding taxonomy

### 3. Flexible Configuration
- Command-line interface
- Configuration file support
- Environment variable override
- Runtime parameter adjustment

### 4. Error Handling
- Graceful degradation on component failure
- Detailed error reporting
- Partial result preservation
- Recovery mechanisms

## Advanced Usage

### Running Individual Builds
```python
from UNIFIED_INTEGRATION import UnifiedForensicEngine, UnifiedConfig

# Initialize engine
config = UnifiedConfig()
engine = UnifiedForensicEngine(config)

# Run individual build
result = engine.run_wellark_analysis()
result = engine.run_wellabuild_analysis()
result = engine.run_project_airtight_analysis()
```

### Custom Correlation Logic
```python
def custom_correlate(results):
    # Implement your own correlation logic
    correlations = []
    # ... your code here ...
    return correlations

# Use in engine
engine._correlate_results = custom_correlate
```

### Extending the System
```python
class CustomEngine(UnifiedForensicEngine):
    def run_custom_analysis(self):
        # Add your custom analysis
        result = UnifiedResult(...)
        # ... implementation ...
        return result

# Use custom engine
engine = CustomEngine(config)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'src.forensic_gate_engine'
   ```
   - Ensure all build directories exist
   - Check Python path configuration
   - Verify module imports are correct

2. **Directory Not Found**
   ```
   FileNotFoundError: Required directory not found
   ```
   - Verify build paths in configuration
   - Check directory permissions
   - Use absolute paths for reliability

3. **Memory Issues**
   ```
   MemoryError: Unable to allocate X bytes
   ```
   - Reduce temporal window size
   - Process files in batches
   - Enable verbose mode for debugging

4. **Permission Errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - Check file permissions
   - Use appropriate user account
   - Verify output directory write access

### Debug Mode
Enable verbose output for detailed debugging:
```bash
python run_unified_analysis.py --verbose
```

### Configuration Validation
Test your configuration before running analysis:
```bash
python -c "
from UNIFIED_INTEGRATION import UnifiedConfig, validate_directories
config = UnifiedConfig()
try:
    validate_directories(config)
    print('✅ Configuration valid')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## Performance Optimization

### 1. Batch Processing
- Process large files in chunks
- Use parallel processing where possible
- Implement caching for repeated operations

### 2. Memory Management
- Process files sequentially for large datasets
- Use generators for memory efficiency
- Implement streaming where applicable

### 3. Caching
- Cache intermediate results
- Save computed predicates
- Reuse spatial calculations

### 4. Parallel Execution
```python
import concurrent.futures

def run_parallel(engine):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        futures.append(executor.submit(engine.run_wellark_analysis))
        futures.append(executor.submit(engine.run_wellabuild_analysis))
        futures.append(executor.submit(engine.run_project_airtight_analysis))

        results = []
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results
```

## Security Considerations

### 1. Data Protection
- Secure storage of audit trails
- Encryption for sensitive data
- Access control on output files

### 2. Integrity Verification
- Regular verification of audit signatures
- Chain of custody documentation
- Tamper-proof logging

### 3. Privacy Compliance
- Anonymization of sensitive data
- Compliance with data protection laws
- Secure data handling practices

## Maintenance

### Regular Tasks
1. Update configuration files
2. Clean up old output files
3. Verify audit trail integrity
4. Update dependencies
5. Monitor performance metrics

### Backup Strategy
- Regular backup of configuration files
- Version control of integration scripts
- Archive important output files
- Maintain audit trail history

### Monitoring
- Track execution times
- Monitor success/failure rates
- Log system performance
- Alert on abnormal behavior

## Contributing

### Adding New Builds
1. Create new enum value in `BuildType`
2. Implement analysis method in `UnifiedForensicEngine`
3. Add correlation logic for the new build
4. Update configuration schema
5. Add documentation

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Document all public methods
- Write comprehensive tests

### Testing
- Unit tests for each component
- Integration tests for the full system
- Performance benchmarking
- Error scenario testing

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the output logs
3. Enable verbose mode for debugging
4. Check configuration validity
5. Verify all dependencies are installed

## Version History

### v1.0.0 (Current)
- Initial unified integration
- Support for WellArk, WellABUILD, and Project Airtight
- Basic correlation engine
- Audit trail implementation
- CLI interface

---

This integration creates a powerful forensic analysis platform that leverages the strengths of all three builds while providing a unified interface for analysis and reporting.