"""
Steganography Analysis Demo
Main application for detecting and extracting hidden data from media files
"""

import os
import sys
import argparse
from steganography_analyzer.image_analyzer import ImageSteganographyAnalyzer
from steganography_analyzer.audio_analyzer import AudioSteganographyAnalyzer
from steganography_analyzer.video_analyzer import VideoSteganographyAnalyzer
from steganography_analyzer.report_generator import ReportGenerator
import numpy as np
from PIL import Image


def create_sample_image_with_steganography(output_path, message="Hello, this is hidden data!"):
    """
    Create a sample image with LSB steganography for demonstration
    
    Args:
        output_path: Path to save the sample image
        message: Message to hide in the image
    """
    # Create a simple image
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    pixels = np.array(img)
    
    # Convert message to binary
    message_binary = ''.join(format(ord(c), '08b') for c in message)
    message_binary += '1111111111111110'  # End marker (16 bits)
    
    # Embed message in LSB
    bit_index = 0
    for i in range(height):
        for j in range(width):
            for channel in range(3):  # RGB channels
                if bit_index < len(message_binary):
                    # Modify LSB
                    pixels[i, j, channel] = (pixels[i, j, channel] & 0xFE) | int(message_binary[bit_index])
                    bit_index += 1
                else:
                    break
            if bit_index >= len(message_binary):
                break
        if bit_index >= len(message_binary):
            break
    
    # Save image
    result_img = Image.fromarray(pixels)
    result_img.save(output_path)
    print(f"Created sample image with steganography: {output_path}")
    print(f"Hidden message: {message}")


def create_sample_audio_with_steganography(output_path, message="Secret audio message"):
    """
    Create a sample audio file with LSB steganography for demonstration
    
    Args:
        output_path: Path to save the sample audio
        message: Message to hide in the audio
    """
    try:
        from pydub import AudioSegment
        import numpy as np
        
        # Create a simple sine wave audio
        duration = 2  # seconds
        sample_rate = 44100
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Normalize and convert to int16
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Convert message to binary
        message_binary = ''.join(format(ord(c), '08b') for c in message)
        message_binary += '1111111111111110'  # End marker
        
        # Embed message in LSB
        bit_index = 0
        for i in range(len(audio_data)):
            if bit_index < len(message_binary):
                audio_data[i] = (audio_data[i] & 0xFFFE) | int(message_binary[bit_index])
                bit_index += 1
            else:
                break
        
        # Convert to AudioSegment
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            channels=1,
            sample_width=2
        )
        
        # Export
        audio_segment.export(output_path, format="wav")
        print(f"Created sample audio with steganography: {output_path}")
        print(f"Hidden message: {message}")
    except Exception as e:
        print(f"Could not create sample audio: {e}")


def analyze_file(file_path, file_type=None):
    """
    Analyze a file for steganography
    
    Args:
        file_path: Path to the file
        file_type: Type of file ('image', 'audio', 'video') or None for auto-detect
    
    Returns:
        dict: Analysis results
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Auto-detect file type if not specified
    if file_type is None:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            file_type = 'image'
        elif ext in ['.wav', '.mp3', '.flac', '.ogg', '.m4a']:
            file_type = 'audio'
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            file_type = 'video'
        else:
            raise ValueError(f"Unknown file type: {ext}")
    
    print(f"\n{'='*60}")
    print(f"Analyzing {file_type.upper()}: {os.path.basename(file_path)}")
    print(f"{'='*60}\n")
    
    try:
        if file_type == 'image':
            analyzer = ImageSteganographyAnalyzer(file_path)
            analysis = analyzer.analyze()
        elif file_type == 'audio':
            analyzer = AudioSteganographyAnalyzer(file_path)
            analysis = analyzer.analyze()
        elif file_type == 'video':
            analyzer = VideoSteganographyAnalyzer(file_path)
            analysis = analyzer.analyze(num_frames=10)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return analysis
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None


def print_analysis_results(analysis):
    """Print analysis results to console"""
    if analysis is None:
        print("Analysis failed.")
        return
    
    # File info
    if 'image_info' in analysis:
        info = analysis['image_info']
        print(f"Image: {info.get('width')}x{info.get('height')}, {info.get('channels')} channels")
    elif 'audio_info' in analysis:
        info = analysis['audio_info']
        print(f"Audio: {info.get('sample_rate')} Hz, {info.get('channels')} channels, {info.get('duration'):.2f}s")
    elif 'video_info' in analysis:
        info = analysis['video_info']
        print(f"Video: {info.get('width')}x{info.get('height')}, {info.get('fps')} fps, {info.get('duration'):.2f}s")
    
    print("\nDetection Results:")
    print("-" * 60)
    
    # LSB Detection
    if 'lsb_detection' in analysis:
        lsb = analysis['lsb_detection']
        status = "✓ DETECTED" if lsb.get('detected') else "✗ NOT DETECTED"
        print(f"LSB Steganography: {status}")
        if lsb.get('detected'):
            print(f"  Confidence: {lsb.get('confidence', 0):.2f}%")
    
    # DCT Detection
    if 'dct_detection' in analysis:
        dct = analysis['dct_detection']
        status = "✓ DETECTED" if dct.get('detected') else "✗ NOT DETECTED"
        print(f"DCT Steganography: {status}")
        if dct.get('detected'):
            print(f"  Confidence: {dct.get('confidence', 0):.2f}%")
    
    # Phase Detection
    if 'phase_detection' in analysis:
        phase = analysis['phase_detection']
        status = "✓ DETECTED" if phase.get('detected') else "✗ NOT DETECTED"
        print(f"Phase Steganography: {status}")
        if phase.get('detected'):
            print(f"  Confidence: {phase.get('confidence', 0):.2f}%")
    
    # Frame Analysis
    if 'frame_analysis' in analysis:
        frame = analysis['frame_analysis']
        status = "✓ DETECTED" if frame.get('detected') else "✗ NOT DETECTED"
        print(f"Frame-based Steganography: {status}")
        if frame.get('detected'):
            print(f"  Confidence: {frame.get('confidence', 0):.2f}%")
            print(f"  Frames with steganography: {frame.get('details', {}).get('frames_with_steganography', 0)}")
    
    # Extraction Results
    extraction = analysis.get('extraction', {})
    if extraction:
        print("\nExtraction Results:")
        print("-" * 60)
        for method, result in extraction.items():
            if result.get('extracted'):
                print(f"{method.upper()} Extraction:")
                data = result.get('data', 'N/A')
                if data and len(data) > 100:
                    data = data[:100] + "..."
                print(f"  Extracted Data: {data}")
                print(f"  Bits Extracted: {result.get('details', {}).get('bits_extracted', 0)}")
    
    print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Steganography Analysis Tool - Detect and extract hidden data from media files'
    )
    parser.add_argument('files', nargs='*', help='File(s) to analyze')
    parser.add_argument('--create-samples', action='store_true', help='Create sample files with steganography')
    parser.add_argument('--report', '-r', help='Generate PDF report (specify output path)')
    parser.add_argument('--type', '-t', choices=['image', 'audio', 'video'], 
                       help='Force file type (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Create sample files if requested
    if args.create_samples:
        print("Creating sample files with steganography...")
        os.makedirs('samples', exist_ok=True)
        
        create_sample_image_with_steganography('samples/sample_image.png', 
                                              "This is a hidden message in the image!")
        create_sample_audio_with_steganography('samples/sample_audio.wav',
                                              "Secret audio message")
        
        print("\nSample files created in 'samples' directory.")
        print("You can now analyze them using:")
        print("  python demo.py samples/sample_image.png")
        print("  python demo.py samples/sample_audio.wav")
        return
    
    # Analyze files
    if not args.files:
        parser.print_help()
        print("\nExample usage:")
        print("  python demo.py image.png")
        print("  python demo.py audio.wav video.mp4")
        print("  python demo.py --create-samples")
        print("  python demo.py file.png --report report.pdf")
        return
    
    analyses = []
    
    for file_path in args.files:
        try:
            analysis = analyze_file(file_path, args.type)
            if analysis:
                analyses.append(analysis)
                print_analysis_results(analysis)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Generate report if requested
    if args.report and analyses:
        print(f"\nGenerating PDF report: {args.report}")
        try:
            generator = ReportGenerator(args.report)
            generator.generate(analyses)
            print(f"Report generated successfully: {args.report}")
        except Exception as e:
            print(f"Error generating report: {e}")


if __name__ == '__main__':
    main()

