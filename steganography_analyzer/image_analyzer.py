"""
Image Steganography Analyzer
Detects and extracts hidden data from images using various methods:
- LSB (Least Significant Bit)
- DCT (Discrete Cosine Transform) - JPEG steganography
"""

import numpy as np
from PIL import Image
import cv2
from scipy import fft
import os


class ImageSteganographyAnalyzer:
    """Analyzes images for hidden steganographic data"""
    
    def __init__(self, image_path):
        """
        Initialize analyzer with image path
        
        Args:
            image_path: Path to the image file
        """
        self.image_path = image_path
        self.image = None
        self.image_array = None
        self.width = 0
        self.height = 0
        self.channels = 0
        self.load_image()
    
    def load_image(self):
        """Load image and convert to numpy array"""
        try:
            self.image = Image.open(self.image_path)
            self.image_array = np.array(self.image)
            
            if len(self.image_array.shape) == 2:
                # Grayscale
                self.height, self.width = self.image_array.shape
                self.channels = 1
            else:
                # Color (RGB/RGBA)
                self.height, self.width, self.channels = self.image_array.shape
            
            return True
        except Exception as e:
            raise Exception(f"Error loading image: {str(e)}")
    
    def detect_lsb_steganography(self):
        """
        Detect LSB steganography by analyzing bit patterns
        
        Returns:
            dict: Detection results with confidence and method details
        """
        results = {
            'method': 'LSB (Least Significant Bit)',
            'detected': False,
            'confidence': 0.0,
            'details': {}
        }
        
        try:
            # Flatten image array
            if self.channels == 1:
                pixels = self.image_array.flatten()
            else:
                pixels = self.image_array.flatten()
            
            # Analyze LSB patterns
            lsb_values = pixels & 1
            
            # Statistical analysis
            # Random data should have ~50% 0s and 50% 1s in LSB
            ones_ratio = np.sum(lsb_values) / len(lsb_values)
            
            # Check for patterns that suggest hidden data
            # If LSBs are not random, might indicate steganography
            deviation = abs(ones_ratio - 0.5)
            
            # Chi-square test for randomness
            expected = len(lsb_values) / 2
            chi_square = np.sum((np.bincount(lsb_values) - expected) ** 2 / expected)
            
            # Threshold for detection (can be tuned)
            if deviation > 0.1 or chi_square > 100:
                results['detected'] = True
                results['confidence'] = min(deviation * 2, 1.0) * 100
            
            results['details'] = {
                'ones_ratio': ones_ratio,
                'deviation_from_random': deviation,
                'chi_square': chi_square,
                'total_pixels': len(pixels)
            }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def extract_lsb_data(self, num_bits=1000, channel=0):
        """
        Extract data from LSB of image
        
        Args:
            num_bits: Number of bits to extract
            channel: Color channel to extract from (0=R, 1=G, 2=B)
        
        Returns:
            dict: Extracted data and metadata
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
            if self.channels == 1:
                channel_data = self.image_array.flatten()
            else:
                channel_data = self.image_array[:, :, channel].flatten()
            
            # Extract LSBs
            lsb_bits = []
            bits_extracted = 0
            
            for pixel in channel_data:
                if bits_extracted >= num_bits:
                    break
                lsb_bits.append(str(pixel & 1))
                bits_extracted += 1
            
            binary_string = ''.join(lsb_bits)
            results['binary_data'] = binary_string
            results['extracted'] = True
            
            # Try to decode as ASCII
            try:
                # Convert binary to bytes
                bytes_data = []
                for i in range(0, len(binary_string), 8):
                    if i + 8 <= len(binary_string):
                        byte = binary_string[i:i+8]
                        bytes_data.append(int(byte, 2))
                
                # Try to decode as text
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
    
    def detect_dct_steganography(self):
        """
        Detect DCT-based steganography (common in JPEG)
        
        Returns:
            dict: Detection results
        """
        results = {
            'method': 'DCT (Discrete Cosine Transform)',
            'detected': False,
            'confidence': 0.0,
            'details': {}
        }
        
        try:
            # Convert to grayscale if needed
            if self.channels > 1:
                gray = cv2.cvtColor(self.image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = self.image_array
            
            # Apply DCT
            # Work with 8x8 blocks (JPEG standard)
            block_size = 8
            dct_coefficients = []
            
            for i in range(0, gray.shape[0] - block_size, block_size):
                for j in range(0, gray.shape[1] - block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size].astype(np.float32)
                    dct_block = cv2.dct(block)
                    dct_coefficients.append(dct_block)
            
            if dct_coefficients:
                # Analyze DCT coefficients
                # Steganography often affects high-frequency components
                all_coeffs = np.array(dct_coefficients).flatten()
                
                # Check for unusual patterns in AC coefficients
                ac_coeffs = all_coeffs[all_coeffs != 0]  # Exclude DC component
                
                if len(ac_coeffs) > 0:
                    # Statistical analysis
                    mean_abs = np.mean(np.abs(ac_coeffs))
                    std_abs = np.std(np.abs(ac_coeffs))
                    
                    # Unusual patterns might indicate steganography
                    if std_abs > mean_abs * 0.5:
                        results['detected'] = True
                        results['confidence'] = min(std_abs / mean_abs, 1.0) * 50
                
                results['details'] = {
                    'blocks_analyzed': len(dct_coefficients),
                    'ac_coefficients': len(ac_coeffs),
                    'mean_abs_coeff': float(mean_abs) if len(ac_coeffs) > 0 else 0,
                    'std_abs_coeff': float(std_abs) if len(ac_coeffs) > 0 else 0
                }
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def analyze(self):
        """
        Perform comprehensive analysis of image
        
        Returns:
            dict: Complete analysis results
        """
        analysis = {
            'file_path': self.image_path,
            'image_info': {
                'width': self.width,
                'height': self.height,
                'channels': self.channels,
                'format': self.image.format if self.image else 'Unknown'
            },
            'lsb_detection': self.detect_lsb_steganography(),
            'dct_detection': self.detect_dct_steganography(),
            'extraction': {}
        }
        
        # Try extraction if LSB detected
        if analysis['lsb_detection']['detected']:
            analysis['extraction']['lsb'] = self.extract_lsb_data(num_bits=1000)
        
        return analysis

