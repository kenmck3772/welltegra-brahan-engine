# Brahan Engine - Feed Data Guide

## Opening and Feeding Documents & Logs

This guide shows you how to open the Brahan Engine and feed it documents and logs for forensic analysis.

## Quick Start

### Method 1: Automatic Data Discovery (Recommended)

```bash
# Navigate to the engine directory
cd /home/brahan_welltegra/wellark-forensics/welltegra-brahan-engine-main

# The engine will automatically discover and process:
# - PDF files in pdf_files/ directory
# - LAS files in las_files/ directory
# - Log files in logs/ directory

python run_unified_analysis.py
```

### Method 2: Manual Data Feeding

```bash
# Create directories and add your files
mkdir -p my_documents/my_pdfs
mkdir -p my_documents/my_las
mkdir -p my_documents/my_logs

# Copy your files
cp /path/to/your/documents/*.pdf my_documents/my_pdfs/
cp /path/to/your/logs/*.las my_documents/my_las/
cp /path/to/your/logs/*.log my_documents/my_logs/

# Run the engine with custom paths
python run_unified_analysis.py --output my_analysis_results
```

## Step-by-Step Instructions

### Step 1: Prepare Your Data

Create the following directory structure:

```
brahan-engine-data/
├── pdf_files/          # PDF documents
│   ├── report_2024.pdf
│   ├── manual.pdf
│   └── specifications.pdf
├── las_files/          # LAS log files
│   ├── well_1.las
│   ├── well_2.las
│   └── well_3.las
├── log_files/         # Text/log files
│   ├── operations.log
│   ├── maintenance.log
│   └── inspection.log
└── output/            # Analysis results
```

### Step 2: Add Your Documents

#### PDF Documents
- Place PDF files in `pdf_files/` directory
- Supported formats: .pdf
- The engine will extract:
  - Metadata
  - Text content
  - Relationships between documents

#### LAS Files
- Place LAS files in `las_files/` directory
- Supported formats: .las
- The engine will analyze:
  - Log curves
  - Well parameters
  - Depth correlations

#### Log Files
- Place text/log files in `log_files/` directory
- Supported formats: .log, .txt
- The engine will process:
  - Operational data
  - Maintenance records
  - Inspection reports

### Step 3: Configure the Engine

Create a configuration file (optional):

```json
{
  "input_directories": {
    "pdf_files": "pdf_files/",
    "las_files": "las_files/",
    "log_files": "log_files/"
  },
  "analysis_parameters": {
    "temporal_window_days": 365,
    "predicate_threshold": 0.8,
    "enable_pdf_ocr": true,
    "enable_las_validation": true
  },
  "output_settings": {
    "output_directory": "output/",
    "generate_visualization": true,
    "export_osdu": false
  }
}
```

Save this as `engine_config.json`.

### Step 4: Run the Engine

#### Basic Execution
```bash
# Run with default settings
python run_unified_analysis.py
```

#### With Custom Configuration
```bash
# Run with custom config
python run_unified_analysis.py --config engine_config.json
```

#### With Custom Output
```bash
# Specify output directory
python run_unified_analysis.py --output /path/to/custom/output
```

#### Verbose Mode
```bash
# See detailed processing
python run_unified_analysis.py --verbose
```

### Step 5: Monitor Progress

When running, you'll see:

```
🚀 Starting Brahan Engine Analysis
============================================================
📄 Processing PDF Documents...
  - Extracting metadata from report_2024.pdf
  - OCR processing on manual.pdf
  - Document relationship mapping...

📊 Processing LAS Files...
  - Analyzing well_1.las curves
  - Depth correlation across wells
  - Cement integrity analysis...

📋 Processing Log Files...
  - Parsing operations.log
  - Anomaly detection in maintenance.log
  - Pattern recognition in inspection.log...

🔄 Cross-correlating findings...
✅ Brahan Engine analysis completed in 45.23s
```

## Advanced Data Feeding Methods

### Method 3: Programmatic Feeding

```python
from UNIFIED_INTEGRATION import BrahanEngine, UnifiedConfig
import os

# Initialize engine
config = UnifiedConfig()
config.pdf_dir = "/path/to/your/pdfs"
config.las_dir = "/path/to/your/las"
config.log_dir = "/path/to/your/logs"

engine = BrahanEngine(config)

# Feed documents programmatically
pdf_files = ["/path/to/doc1.pdf", "/path/to/doc2.pdf"]
las_files = ["/path/to/well1.las", "/path/to/well2.las"]
log_files = ["/path/to/ops.log", "/path/to/maint.log"]

# Process files
results = engine.process_documents(pdf_files)
results = engine.process_logs(las_files)
results = engine.process_text_files(log_files)

# Get unified analysis
unified_results = engine.run_complete_analysis()
```

### Method 4: Batch Processing

```bash
# Process multiple directories
for dir in data_directories; do
    echo "Processing $dir..."
    python run_unified_analysis.py --output "results_$dir"
done
```

### Method 5: Real-time Processing

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BrahanEngineHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        if file_path.endswith(('.pdf', '.las', '.log')):
            print(f"New file detected: {file_path}")
            # Trigger Brahan Engine processing
            process_file(file_path)

# Setup file watcher
observer = Observer()
observer.schedule(BrahanEngineHandler(), path='/watch/directory')
observer.start()
```

## File Processing Details

### PDF Processing
The engine extracts:
- Document metadata
- Full text content (OCR for scanned docs)
- Tables and figures
- Document relationships
- Signature verification
- Tamper detection

### LAS File Processing
The engine analyzes:
- Log curves (GR, RHOB, NPHI, etc.)
- Well header information
- Depth correlations
- Cement integrity
- Formation properties
- Anomaly detection

### Log File Processing
The engine processes:
- Operational data
- Maintenance records
- Inspection reports
- Anomaly patterns
- Temporal trends
- Relationship mapping

## Output Files

After processing, you'll find:

### Primary Results
- `brahan_engine_results_YYYYMMDD_HHMMSS.json`
- `audit_trail_YYYYMMDD_HHMMSS.json`
- `document_analysis.json`
- `log_analysis.json`
- `correlation_report.json`

### Visualizations
- `3d_wellbore_map.html`
- `temporal_trends.png`
- `risk_dashboard.html`
- `relationship_graph.png`

## Troubleshooting

### Common Issues

1. **Files Not Found**
   ```bash
   # Check directory structure
   ls -la pdf_files/ las_files/ log_files/

   # Ensure files exist
   find . -name "*.pdf" -o -name "*.las" -o -name "*.log"
   ```

2. **Permission Errors**
   ```bash
   # Fix permissions
   chmod 755 pdf_files/ las_files/ log_files/
   chmod 644 pdf_files/* las_files/* log_files/*
   ```

3. **Empty Results**
   ```bash
   # Check file formats
   file pdf_files/*.pdf
   file las_files/*.las

   # Validate LAS files
   python -c "import lasio; las = lasio.read('las_files/well1.las')"
   ```

### Debug Mode

```bash
# Enable verbose output
python run_unified_analysis.py --verbose > engine.log 2>&1

# Check logs
tail -f engine.log

# Test individual components
python basic_integration.py
```

## Best Practices

### 1. File Organization
- Keep file names descriptive
- Use consistent naming conventions
- Separate different well data
- Archive old data separately

### 2. Data Quality
- Ensure PDFs are readable
- Validate LAS file formats
- Clean log data before processing
- Remove duplicates

### 3. Performance
- Process files in batches
- Use appropriate temporal windows
- Monitor memory usage
- Clean up old results regularly

### 4. Security
- Protect sensitive documents
- Use encrypted storage for logs
- Implement access controls
- Regular audit trail checks

## Getting Help

### Check Status
```bash
# Run diagnostic
python basic_integration.py

# Test file processing
python -c "
from UNIFIED_INTEGRATION import BrahanEngine
engine = BrahanEngine()
print('Engine ready')
print(f'PDF directory: {engine.config.pdf_dir}')
print(f'LAS directory: {engine.config.las_dir}')
"
```

### View Results
```bash
# Check latest results
ls -la output/ | tail -10

# View analysis summary
cat output/brahan_engine_results_*.json | jq '.summary'
```

---

The Brahan Engine is ready to process your documents and logs. Follow these steps to get comprehensive forensic analysis results!