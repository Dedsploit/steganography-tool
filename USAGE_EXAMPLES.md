# Usage Examples

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Sample Files with Steganography
```bash
python demo.py --create-samples
```

This creates:
- `samples/sample_image.png` - Contains hidden message: "This is a hidden message in the image!"
- `samples/sample_audio.wav` - Contains hidden message: "Secret audio message"

### 3. Analyze Sample Files
```bash
# Analyze the sample image
python demo.py samples/sample_image.png

# Analyze the sample audio
python demo.py samples/sample_audio.wav

# Analyze both
python demo.py samples/sample_image.png samples/sample_audio.wav
```

### 4. Generate PDF Report
```bash
python demo.py samples/sample_image.png samples/sample_audio.wav --report analysis_report.pdf
```

## Advanced Usage

### Analyze Your Own Files
```bash
# Single file
python demo.py my_image.png

# Multiple files
python demo.py image1.png audio1.wav video1.mp4

# Force file type (if auto-detection fails)
python demo.py file.ext --type image
```

### Programmatic Usage

```python
from steganography_analyzer.image_analyzer import ImageSteganographyAnalyzer
from steganography_analyzer.audio_analyzer import AudioSteganographyAnalyzer
from steganography_analyzer.report_generator import ReportGenerator

# Analyze an image
analyzer = ImageSteganographyAnalyzer('image.png')
results = analyzer.analyze()
print(results)

# Analyze audio
audio_analyzer = AudioSteganographyAnalyzer('audio.wav')
audio_results = audio_analyzer.analyze()
print(audio_results)

# Generate report
generator = ReportGenerator('report.pdf')
generator.generate([results, audio_results])
```

## Expected Output

When analyzing a file with steganography, you'll see output like:

```
============================================================
Analyzing IMAGE: sample_image.png
============================================================

Image: 400x300, 3 channels

Detection Results:
------------------------------------------------------------
LSB Steganography: ✓ DETECTED
  Confidence: 85.23%
DCT Steganography: ✗ NOT DETECTED

Extraction Results:
------------------------------------------------------------
LSB Extraction:
  Extracted Data: This is a hidden message in the image!
  Bits Extracted: 1000
```

## Troubleshooting

### Import Errors
If you get import errors, make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Audio Format Issues
Some audio formats may require additional codecs. For MP3 support, you may need:
```bash
# On Windows
pip install pydub[mp3]

# On Linux/Mac
sudo apt-get install ffmpeg  # or brew install ffmpeg
```

### Video Format Issues
OpenCV should support most common video formats. If you encounter issues, try converting the video to MP4 first.

