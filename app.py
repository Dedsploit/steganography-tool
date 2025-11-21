"""
Flask Web Application for Steganography Analysis
"""

import os
import uuid
import warnings

# Suppress FFmpeg warnings from pydub
warnings.filterwarnings('ignore', message='.*ffmpeg.*', category=RuntimeWarning)
warnings.filterwarnings('ignore', message='.*avconv.*', category=RuntimeWarning)

from flask import Flask, render_template, request, jsonify, send_file, session
from werkzeug.utils import secure_filename
from steganography_analyzer.image_analyzer import ImageSteganographyAnalyzer
from steganography_analyzer.audio_analyzer import AudioSteganographyAnalyzer
from steganography_analyzer.video_analyzer import VideoSteganographyAnalyzer
from steganography_analyzer.report_generator import ReportGenerator
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
os.makedirs('static/samples', exist_ok=True)

ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'},
    'audio': {'wav', 'mp3', 'flac', 'ogg', 'm4a'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'flv'}
}

def allowed_file(filename, file_type='all'):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'all':
        all_exts = set()
        for exts in ALLOWED_EXTENSIONS.values():
            all_exts.update(exts)
        return ext in all_exts
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    for file_type, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return file_type
    return None

def create_sample_image_with_steganography(output_path, message="Hello, this is hidden data!"):
    """Create a sample image with LSB steganography"""
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    pixels = np.array(img)
    
    message_binary = ''.join(format(ord(c), '08b') for c in message)
    message_binary += '1111111111111110'  # End marker
    
    bit_index = 0
    for i in range(height):
        for j in range(width):
            for channel in range(3):
                if bit_index < len(message_binary):
                    pixels[i, j, channel] = (pixels[i, j, channel] & 0xFE) | int(message_binary[bit_index])
                    bit_index += 1
                else:
                    break
            if bit_index >= len(message_binary):
                break
        if bit_index >= len(message_binary):
            break
    
    result_img = Image.fromarray(pixels)
    result_img.save(output_path)
    return output_path

def create_sample_audio_with_steganography(output_path, message="Secret audio message"):
    """Create a sample audio file with LSB steganography"""
    try:
        # Suppress FFmpeg warnings during import and usage
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='.*ffmpeg.*', category=RuntimeWarning)
            warnings.filterwarnings('ignore', message='.*avconv.*', category=RuntimeWarning)
            from pydub import AudioSegment
        
        duration = 2
        sample_rate = 44100
        frequency = 440
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)
        audio_data = (audio_data * 32767).astype(np.int16)
        
        message_binary = ''.join(format(ord(c), '08b') for c in message)
        message_binary += '1111111111111110'
        
        bit_index = 0
        for i in range(len(audio_data)):
            if bit_index < len(message_binary):
                audio_data[i] = (audio_data[i] & 0xFFFE) | int(message_binary[bit_index])
                bit_index += 1
            else:
                break
        
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='.*ffmpeg.*', category=RuntimeWarning)
            warnings.filterwarnings('ignore', message='.*avconv.*', category=RuntimeWarning)
            audio_segment = AudioSegment(
                audio_data.tobytes(),
                frame_rate=sample_rate,
                channels=1,
                sample_width=2
            )
            audio_segment.export(output_path, format="wav")
        return output_path
    except Exception as e:
        raise Exception(f"Could not create sample audio: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not supported'}), 400
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    try:
        # Determine file type and analyze
        file_type = get_file_type(filename)
        
        if file_type == 'image':
            analyzer = ImageSteganographyAnalyzer(filepath)
            analysis = analyzer.analyze()
        elif file_type == 'audio':
            analyzer = AudioSteganographyAnalyzer(filepath)
            analysis = analyzer.analyze()
        elif file_type == 'video':
            analyzer = VideoSteganographyAnalyzer(filepath)
            analysis = analyzer.analyze(num_frames=10)
        else:
            return jsonify({'error': 'Unknown file type'}), 400
        
        # Store analysis in session
        if 'analyses' not in session:
            session['analyses'] = []
        
        analysis['original_filename'] = filename
        analysis['unique_filename'] = unique_filename
        session['analyses'].append(analysis)
        session.modified = True
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'File analyzed successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate PDF report from analyses"""
    try:
        analyses = session.get('analyses', [])
        if not analyses:
            return jsonify({'error': 'No analyses to report'}), 400
        
        # Generate report
        report_filename = f"steganography_report_{uuid.uuid4()}.pdf"
        report_path = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        
        generator = ReportGenerator(report_path)
        generator.generate(analyses)
        
        return jsonify({
            'success': True,
            'report_filename': report_filename,
            'message': 'Report generated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/download_report/<filename>')
def download_report(filename):
    """Download generated report"""
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create_samples', methods=['POST'])
def create_samples():
    """Create sample files with steganography"""
    try:
        sample_image_path = os.path.join('static', 'samples', 'sample_image.png')
        sample_audio_path = os.path.join('static', 'samples', 'sample_audio.wav')
        
        create_sample_image_with_steganography(
            sample_image_path,
            "This is a hidden message in the image!"
        )
        create_sample_audio_with_steganography(
            sample_audio_path,
            "Secret audio message"
        )
        
        return jsonify({
            'success': True,
            'samples': {
                'image': '/static/samples/sample_image.png',
                'audio': '/static/samples/sample_audio.wav'
            },
            'message': 'Sample files created successfully'
        })
    
    except Exception as e:
        return jsonify({'error': f'Sample creation failed: {str(e)}'}), 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear analysis session"""
    session['analyses'] = []
    session.modified = True
    return jsonify({'success': True, 'message': 'Session cleared'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

