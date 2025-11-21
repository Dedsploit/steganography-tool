"""
Audio Steganography Analyzer
Detects and extracts hidden data from audio files using:
- LSB (Least Significant Bit) in audio samples
- Phase coding
- Echo hiding
"""

import numpy as np
import os
import tempfile
import warnings

# Suppress FFmpeg warning if not found
warnings.filterwarnings('ignore', message='.*ffmpeg.*', category=RuntimeWarning)

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None


class AudioSteganographyAnalyzer:
    """Analyzes audio files for hidden steganographic data"""
    
    def __init__(self, audio_path):
        """
        Initialize analyzer with audio path
        
        Args:
            audio_path: Path to the audio file
        """
        self.audio_path = audio_path
        self.audio_segment = None
        self.audio_array = None
        self.sample_rate = 0
        self.channels = 0
        self.duration = 0
        self.load_audio()
    
    def load_audio(self):
        """Load audio file and convert to numpy array"""
        if AudioSegment is None:
            raise Exception("pydub is not installed. Please install it with: pip install pydub")
        
        try:
            # Suppress FFmpeg warnings during audio loading
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='.*ffmpeg.*', category=RuntimeWarning)
                warnings.filterwarnings('ignore', message='.*avconv.*', category=RuntimeWarning)
                self.audio_segment = AudioSegment.from_file(self.audio_path)
            
            self.sample_rate = self.audio_segment.frame_rate
            self.channels = self.audio_segment.channels
            self.duration = len(self.audio_segment) / 1000.0  # Convert to seconds
            
            # Convert to numpy array
            raw_audio = self.audio_segment.raw_data
            self.audio_array = np.frombuffer(raw_audio, dtype=np.int16)
            
            # If stereo, reshape
            if self.channels == 2:
                self.audio_array = self.audio_array.reshape(-1, 2)
            
            return True
        except Exception as e:
            raise Exception(f"Error loading audio: {str(e)}")
    
    def detect_lsb_steganography(self):
        """
        Detect LSB steganography in audio samples
        
        Returns:
            dict: Detection results
        """
        results = {
            'method': 'LSB (Least Significant Bit)',
            'detected': False,
            'confidence': 0.0,
            'details': {}
        }
        
        try:
            # Flatten audio array
            if self.channels == 2:
                samples = self.audio_array.flatten()
            else:
                samples = self.audio_array
            
            # Analyze LSB patterns
            lsb_values = samples & 1
            
            # Statistical analysis
            ones_ratio = np.sum(lsb_values) / len(lsb_values)
            deviation = abs(ones_ratio - 0.5)
            
            # Chi-square test
            expected = len(lsb_values) / 2
            chi_square = np.sum((np.bincount(lsb_values) - expected) ** 2 / expected)
            
            # Detection threshold
            if deviation > 0.08 or chi_square > 50:
                results['detected'] = True
                results['confidence'] = min(deviation * 2.5, 1.0) * 100
            
            results['details'] = {
                'ones_ratio': ones_ratio,
                'deviation_from_random': deviation,
                'chi_square': chi_square,
                'total_samples': len(samples),
                'sample_rate': self.sample_rate
            }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def extract_lsb_data(self, num_bits=1000, channel=0):
        """
        Extract data from LSB of audio samples
        
        Args:
            num_bits: Number of bits to extract
            channel: Audio channel (0=left, 1=right for stereo)
        
        Returns:
            dict: Extracted data
        """
        results = {
            'method': 'LSB Extraction',
            'extracted': False,
            'data': None,
            'binary_data': None,
            'details': {}
        }
        
        try:
            # Get channel data
            if self.channels == 2:
                channel_data = self.audio_array[:, channel]
            else:
                channel_data = self.audio_array
            
            # Extract LSBs
            lsb_bits = []
            bits_extracted = 0
            
            for sample in channel_data:
                if bits_extracted >= num_bits:
                    break
                lsb_bits.append(str(sample & 1))
                bits_extracted += 1
            
            binary_string = ''.join(lsb_bits)
            results['binary_data'] = binary_string
            results['extracted'] = True
            
            # Try to decode as ASCII
            try:
                bytes_data = []
                for i in range(0, len(binary_string), 8):
                    if i + 8 <= len(binary_string):
                        byte = binary_string[i:i+8]
                        bytes_data.append(int(byte, 2))
                
                text = ''.join([chr(b) if 32 <= b < 127 else '.' for b in bytes_data])
                results['data'] = text
            except:
                results['data'] = "Binary data (not ASCII)"
            
            results['details'] = {
                'bits_extracted': len(lsb_bits),
                'bytes_extracted': len(binary_string) // 8,
                'channel_used': channel
            }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def detect_phase_steganography(self):
        """
        Detect phase-based steganography
        
        Returns:
            dict: Detection results
        """
        results = {
            'method': 'Phase Coding',
            'detected': False,
            'confidence': 0.0,
            'details': {}
        }
        
        try:
            # Get mono channel for analysis
            if self.channels == 2:
                samples = self.audio_array[:, 0]
            else:
                samples = self.audio_array
            
            # FFT to analyze phase
            fft_result = np.fft.fft(samples[:8192])  # Analyze first 8192 samples
            phase = np.angle(fft_result)
            
            # Check for unusual phase patterns
            phase_diff = np.diff(phase)
            phase_std = np.std(phase_diff)
            
            # Unusual phase variations might indicate steganography
            if phase_std > 0.5:
                results['detected'] = True
                results['confidence'] = min(phase_std, 1.0) * 50
            
            results['details'] = {
                'phase_std': float(phase_std),
                'samples_analyzed': min(8192, len(samples))
            }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def analyze(self):
        """
        Perform comprehensive analysis of audio file
        
        Returns:
            dict: Complete analysis results
        """
        analysis = {
            'file_path': self.audio_path,
            'audio_info': {
                'sample_rate': self.sample_rate,
                'channels': self.channels,
                'duration': self.duration,
                'format': os.path.splitext(self.audio_path)[1]
            },
            'lsb_detection': self.detect_lsb_steganography(),
            'phase_detection': self.detect_phase_steganography(),
            'extraction': {}
        }
        
        # Try extraction if LSB detected
        if analysis['lsb_detection']['detected']:
            analysis['extraction']['lsb'] = self.extract_lsb_data(num_bits=1000)
        
        return analysis

