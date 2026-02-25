# Brahan Engine - Your Data Setup Guide

## Quick Start with Your Folders

Since you have LAS, PDF, and TIFF folders, here's the easiest way to start:

### 🚀 Option 1: Automatic Setup (Recommended)

```bash
# Navigate to the engine directory
cd /home/brahan_welltegra/wellark-forensics/welltegra-brahan-engine-main

# Run the automatic setup
python run_with_your_data.py
```

This script will:
1. **Find your folders** automatically
2. **Copy files** to the engine
3. **Run analysis** on all your data
4. **Show you the results**

### 🔧 Option 2: Interactive Setup

```bash
# Use the interactive feeder
python setup_for_your_folders.py
```

This gives you more control over the setup process.

### 📁 Option 3: Manual Setup

If the automatic setup doesn't find your folders, you can specify them manually:

```bash
# Create engine directories
mkdir -p brahan_engine_data/{las_files,pdf_files,tiff_files,output}

# Copy your files
cp /path/to/your/las/*.las brahan_engine_data/las_files/
cp /path/to/your/pdf/*.pdf brahan_engine_data/pdf_files/
cp /path/to/your/tiffs/*.tif* brahan_engine_data/tiff_files/

# Run the engine
python run_unified_analysis.py
```

## What Happens During Analysis

The Brahan Engine will process your files as follows:

### 🔍 LAS Files (.las)
- **Log curve analysis**: GR, RHOB, NPHI, Resistivity, etc.
- **Well parameters**: Depth, temperature, pressure
- **Cement integrity**: Cement bond logs analysis
- **Formation evaluation**: Porosity, permeability calculations
- **Cross-well correlation**: Compare multiple wells

### 📄 PDF Files (.pdf)
- **Text extraction**: Full document OCR and text mining
- **Metadata extraction**: Creation date, author, keywords
- **Relationship mapping**: Connect documents by content
- **Table extraction**: Well data, specifications, reports

### 🖼️ TIFF Files (.tif, .tiff)
- **Image analysis**: Well log images, core photos
- **OCR on images**: Extract text from scanned logs
- **Pattern recognition**: Identify log types and features
- **Spatial analysis**: Correlate images with depth data

### 🔗 Cross-Correlation
The engine will automatically correlate findings across:
- LAS curves vs PDF reports
- TIFF images vs log data
- Multiple time periods
- Different well locations

## Output You'll Get

After running the analysis, you'll find:

### 📊 Primary Results
- `brahan_engine_results_YYYYMMDD_HHMMSS.json`
- `audit_trail_YYYYMMDD_HHMMSS.json`
- `correlation_report.json`

### 📈 Visualizations
- `3d_wellbore_map.html` - Interactive 3D well visualization
- `risk_dashboard.html` - Risk assessment dashboard
- `temporal_trends.png` - Time-based analysis
- `relationship_graph.png` - Document relationships

## Troubleshooting

### If Files Aren't Found
```bash
# Check common locations
ls -la ~/las/ ~/pdf/ ~/tiffs/
ls -la ./las ./pdf ./tiffs
ls -la ../las ../pdf ../tiffs
```

### If Analysis Fails
```bash
# Run with verbose output
python run_unified_analysis.py --verbose > engine.log 2>&1

# Check the log file
tail -f engine.log
```

### Need More Control
```bash
# Use the interactive feed engine
python feed_engine.py
```

## Tips for Best Results

### File Organization
- Keep well-organized folder names
- Separate different wells/fields
- Include dates in filenames when possible

### Data Quality
- Ensure PDFs are readable (not corrupted)
- Validate LAS file formats
- Clean TIFF images if needed

### Performance
- Large datasets may take 2-5 minutes
- The engine processes files in parallel
- Results are saved incrementally

---

## Ready to Start?

Choose your preferred method above and begin your forensic analysis!

**Recommended**: `python run_with_your_data.py`