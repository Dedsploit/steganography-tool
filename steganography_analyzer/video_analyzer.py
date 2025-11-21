"""
Video Steganography Analyzer
Detects and extracts hidden data from video files by analyzing frames
"""

import cv2
import numpy as np
import os
from .image_analyzer import ImageSteganographyAnalyzer
import tempfile


class VideoSteganographyAnalyzer:
    """Analyzes video files for hidden steganographic data"""
    
    def __init__(self, video_path):
        """
        Initialize analyzer with video path
        
        Args:
            video_path: Path to the video file
        """
        self.video_path = video_path
        self.cap = None
        self.fps = 0
        self.frame_count = 0
        self.width = 0
        self.height = 0
        self.load_video()
    
    def load_video(self):
        """Load video file and get metadata"""
        try:
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                raise Exception("Could not open video file")
            
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            return True
        except Exception as e:
            raise Exception(f"Error loading video: {str(e)}")
    
    def extract_frames(self, num_frames=10):
        """
        Extract frames from video for analysis
        
        Args:
            num_frames: Number of frames to extract
        
        Returns:
            list: Array of frame arrays
        """
        frames = []
        frame_interval = max(1, self.frame_count // num_frames)
        
        for i in range(0, self.frame_count, frame_interval):
            if len(frames) >= num_frames:
                break
            
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = self.cap.read()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame_rgb)
        
        return frames
    
    def analyze_frames(self, frames):
        """
        Analyze extracted frames for steganography
        
        Args:
            frames: List of frame arrays
        
        Returns:
            dict: Analysis results
        """
        results = {
            'method': 'Frame-based Analysis',
            'detected': False,
            'confidence': 0.0,
            'frame_results': [],
            'details': {}
        }
        
        detections = []
        confidences = []
        
        # Analyze each frame
        for idx, frame in enumerate(frames):
            # Save frame temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                cv2.imwrite(tmp_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            try:
                # Use image analyzer on frame
                frame_analyzer = ImageSteganographyAnalyzer(tmp_path)
                frame_analysis = frame_analyzer.analyze()
                
                frame_result = {
                    'frame_number': idx,
                    'lsb_detected': frame_analysis['lsb_detection']['detected'],
                    'lsb_confidence': frame_analysis['lsb_detection']['confidence']
                }
                
                results['frame_results'].append(frame_result)
                
                if frame_analysis['lsb_detection']['detected']:
                    detections.append(True)
                    confidences.append(frame_analysis['lsb_detection']['confidence'])
                
            except Exception as e:
                frame_result = {
                    'frame_number': idx,
                    'error': str(e)
                }
                results['frame_results'].append(frame_result)
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Overall detection
        if detections:
            results['detected'] = True
            results['confidence'] = np.mean(confidences)
            results['details'] = {
                'frames_with_steganography': len(detections),
                'total_frames_analyzed': len(frames),
                'detection_rate': len(detections) / len(frames)
            }
        else:
            results['details'] = {
                'frames_analyzed': len(frames),
                'detection_rate': 0.0
            }
        
        return results
    
    def analyze(self, num_frames=10):
        """
        Perform comprehensive analysis of video file
        
        Args:
            num_frames: Number of frames to analyze
        
        Returns:
            dict: Complete analysis results
        """
        analysis = {
            'file_path': self.video_path,
            'video_info': {
                'width': self.width,
                'height': self.height,
                'fps': self.fps,
                'frame_count': self.frame_count,
                'duration': self.frame_count / self.fps if self.fps > 0 else 0,
                'format': os.path.splitext(self.video_path)[1]
            },
            'frame_analysis': None,
            'extraction': {}
        }
        
        # Extract and analyze frames
        frames = self.extract_frames(num_frames)
        analysis['frame_analysis'] = self.analyze_frames(frames)
        
        return analysis
    
    def __del__(self):
        """Clean up video capture"""
        if self.cap:
            self.cap.release()

