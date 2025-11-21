# Quick Start Guide

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Flask server:**
```bash
python app.py
```

2. **Open your browser:**
Navigate to `http://localhost:5000`

## First Steps

### 1. Create Sample Files

Click the **"Create Sample Files"** button to generate test files with embedded steganography:
- `static/samples/sample_image.png` - Contains hidden message
- `static/samples/sample_audio.wav` - Contains hidden message

### 2. Analyze a File

1. Drag and drop a file onto the upload area, or click to select
2. Wait for analysis to complete
3. View the results showing:
   - Detection status (DETECTED / NOT DETECTED)
   - Confidence scores
   - Extracted data (if found)

### 3. Generate a Report

1. After analyzing one or more files, click **"Generate PDF Report"**
2. Download the generated PDF report
3. The report includes all analysis results with detailed information

## Example Workflow

1. Start the application: `python app.py`
2. Open browser: `http://localhost:5000`
3. Click "Create Sample Files"
4. Upload `static/samples/sample_image.png`
5. View the analysis results showing detected steganography
6. Click "Generate PDF Report"
7. Download and review the report

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, modify `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Missing Dependencies

If you get import errors:
```bash
pip install -r requirements.txt
```

### Audio Format Issues

For MP3 support, you may need additional codecs:
```bash
# Windows
pip install pydub[mp3]

# Linux/Mac
sudo apt-get install ffmpeg  # or brew install ffmpeg
```

### File Upload Errors

- Check file size (max 100MB by default)
- Verify file format is supported
- Ensure `uploads/` directory exists and is writable

## Next Steps

- Try analyzing your own files
- Experiment with different file types
- Review the generated PDF reports
- Check the README.md for detailed documentation

