# Steganography Analysis Tool

A comprehensive Flask-based web application for detecting and extracting hidden data from images, audio, and video files. This project implements various steganography detection and extraction methods with a modern web interface and detailed reporting capabilities.

## Features

### Detection Methods

**Image Steganography:**
- **LSB (Least Significant Bit)** - Detects hidden data in the least significant bits of image pixels
- **DCT (Discrete Cosine Transform)** - Detects steganography in JPEG images using frequency domain analysis

**Audio Steganography:**
- **LSB** - Detects hidden data in audio sample LSBs
- **Phase Coding** - Detects phase-based steganography using FFT analysis

**Video Steganography:**
- **Frame-based Analysis** - Extracts and analyzes video frames for steganographic content

### Extraction Capabilities

- Extract hidden data from detected steganographic files
- Support for ASCII text extraction
- Binary data extraction and preview

### Web Interface

- Modern, responsive web UI
- Drag-and-drop file upload
- Real-time analysis results
- Interactive visualization of detection results
- Sample file generation for testing

### Reporting

- Generate comprehensive PDF reports
- Detailed analysis results with confidence scores
- Method explanations and technical details
- Clean, professional report formatting

## Installation

1. **Clone or download this repository**

2. **Install required dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Web Application

1. **Run the Flask application:**
```bash
python app.py
```

2. **Open your web browser and navigate to:**
```
http://localhost:5000
```

### Using the Web Interface

1. **Upload a file:**
   - Drag and drop a file onto the upload area, or
   - Click the upload area to select a file

2. **View analysis results:**
   - Results are displayed automatically after upload
   - See detection status, confidence scores, and extracted data

3. **Generate a PDF report:**
   - Click "Generate PDF Report" after analyzing files
   - Download the generated report

4. **Create sample files:**
   - Click "Create Sample Files" to generate test files with embedded steganography
   - Analyze these samples to see the tool in action

### Supported File Types

**Images:** PNG, JPG, JPEG, BMP, TIFF, GIF  
**Audio:** WAV, MP3, FLAC, OGG, M4A  
**Video:** MP4, AVI, MOV, MKV, FLV

## Project Structure

```
Steganography/
├── app.py                          # Flask web application
├── steganography_analyzer/
│   ├── __init__.py
│   ├── image_analyzer.py          # Image steganography detection/extraction
│   ├── audio_analyzer.py          # Audio steganography detection/extraction
│   ├── video_analyzer.py          # Video steganography detection/extraction
│   └── report_generator.py        # PDF report generation
├── templates/
│   └── index.html                 # Web interface template
├── static/
│   ├── css/
│   │   └── style.css              # Stylesheet
│   ├── js/
│   │   └── main.js                # Frontend JavaScript
│   └── samples/                   # Generated sample files
├── uploads/                       # Uploaded files (created automatically)
├── reports/                       # Generated reports (created automatically)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## How It Works

### LSB Steganography Detection

The tool analyzes the least significant bits of pixels (images) or samples (audio) for statistical anomalies. In natural media, LSBs should be random. If patterns are detected, it may indicate hidden data.

**Detection Method:**
1. Extract LSB values from all pixels/samples
2. Calculate statistical distribution (ones vs zeros ratio)
3. Perform chi-square test for randomness
4. Flag anomalies as potential steganography

### DCT Steganography Detection

For JPEG images, the tool analyzes Discrete Cosine Transform coefficients. Steganography often affects high-frequency components in predictable ways.

**Detection Method:**
1. Divide image into 8x8 blocks (JPEG standard)
2. Apply DCT to each block
3. Analyze AC coefficient patterns
4. Detect statistical anomalies

### Data Extraction

When steganography is detected, the tool extracts LSB data and attempts to decode it as ASCII text. Binary data is also available for further analysis.

## API Endpoints

The Flask application provides the following endpoints:

- `GET /` - Main web interface
- `POST /upload` - Upload and analyze a file
- `POST /generate_report` - Generate PDF report from analyses
- `GET /download_report/<filename>` - Download generated report
- `POST /create_samples` - Create sample files with steganography
- `POST /clear_session` - Clear analysis session

## Configuration

You can modify the following settings in `app.py`:

- `MAX_CONTENT_LENGTH` - Maximum file upload size (default: 100MB)
- `UPLOAD_FOLDER` - Directory for uploaded files
- `REPORTS_FOLDER` - Directory for generated reports
- Server host and port (in `if __name__ == '__main__'` block)

## Limitations

- **Detection is probabilistic** - False positives and false negatives are possible
- **Advanced steganography** - Some sophisticated methods may evade detection
- **Encrypted payloads** - Extracted data may be encrypted and require additional decryption
- **Large files** - Video analysis is limited to sampled frames for performance
- **File size** - Maximum upload size is 100MB by default

## Technical Details

### Dependencies

- **Flask** - Web framework
- **Pillow** - Image processing
- **NumPy** - Numerical operations
- **OpenCV** - Video and advanced image processing
- **pydub** - Audio processing
- **scipy** - Scientific computing
- **reportlab** - PDF generation
- **Werkzeug** - WSGI utilities

## Development

### Running in Development Mode

```bash
python app.py
```

The application runs in debug mode by default, which provides:
- Automatic reloading on code changes
- Detailed error messages
- Debug toolbar

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Future Enhancements

- Support for more steganography methods (spread spectrum, wavelet-based)
- Machine learning-based detection
- Batch file processing
- Real-time analysis progress indicators
- Export results in multiple formats (JSON, CSV)
- User authentication and session management
- Support for more file formats

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Disclaimer

This tool is intended for legitimate security research, digital forensics, and educational purposes only. Users are responsible for ensuring they have proper authorization before analyzing files.
