"""
Report Generator
Creates clean, formatted reports of steganography analysis results
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


class ReportGenerator:
    """Generates PDF reports from analysis results"""
    
    def __init__(self, output_path):
        """
        Initialize report generator
        
        Args:
            output_path: Path where report will be saved
        """
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Add custom styles only if they don't exist
        if 'CustomTitle' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER
            ))
        
        if 'SectionHeader' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12
            ))
        
        # Use a different name for custom body text to avoid conflict
        if 'CustomBodyText' not in self.styles.byName:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['BodyText'],
                fontSize=10,
                alignment=TA_JUSTIFY,
                spaceAfter=6
            ))
    
    def format_detection_result(self, detection):
        """Format detection result for display"""
        if 'error' in detection:
            return f"Error: {detection['error']}"
        
        status = "DETECTED" if detection.get('detected', False) else "NOT DETECTED"
        confidence = detection.get('confidence', 0.0)
        
        result_text = f"<b>Status:</b> {status}<br/>"
        result_text += f"<b>Method:</b> {detection.get('method', 'Unknown')}<br/>"
        result_text += f"<b>Confidence:</b> {confidence:.2f}%<br/>"
        
        if 'details' in detection:
            result_text += "<b>Details:</b><br/>"
            for key, value in detection['details'].items():
                if isinstance(value, float):
                    result_text += f"  • {key}: {value:.4f}<br/>"
                else:
                    result_text += f"  • {key}: {value}<br/>"
        
        return result_text
    
    def format_extraction_result(self, extraction):
        """Format extraction result for display"""
        if 'error' in extraction:
            return f"Error: {extraction['error']}"
        
        result_text = f"<b>Method:</b> {extraction.get('method', 'Unknown')}<br/>"
        result_text += f"<b>Extracted:</b> {'Yes' if extraction.get('extracted', False) else 'No'}<br/>"
        
        if extraction.get('extracted', False):
            data = extraction.get('data', 'N/A')
            if data and len(data) > 200:
                data = data[:200] + "... (truncated)"
            result_text += f"<b>Data Preview:</b> {data}<br/>"
            
            if 'details' in extraction:
                result_text += "<b>Extraction Details:</b><br/>"
                for key, value in extraction['details'].items():
                    result_text += f"  • {key}: {value}<br/>"
        
        return result_text
    
    def generate_image_report(self, analysis, story):
        """Generate report section for image analysis"""
        story.append(Paragraph("Image Analysis", self.styles['SectionHeader']))
        
        # File info
        info = analysis.get('image_info', {})
        info_text = f"<b>File:</b> {os.path.basename(analysis['file_path'])}<br/>"
        info_text += f"<b>Dimensions:</b> {info.get('width', 'N/A')} x {info.get('height', 'N/A')}<br/>"
        info_text += f"<b>Channels:</b> {info.get('channels', 'N/A')}<br/>"
        info_text += f"<b>Format:</b> {info.get('format', 'N/A')}<br/>"
        story.append(Paragraph(info_text, self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # LSB Detection
        story.append(Paragraph("LSB Steganography Detection", self.styles['Heading3']))
        lsb_detection = analysis.get('lsb_detection', {})
        story.append(Paragraph(self.format_detection_result(lsb_detection), self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # DCT Detection
        story.append(Paragraph("DCT Steganography Detection", self.styles['Heading3']))
        dct_detection = analysis.get('dct_detection', {})
        story.append(Paragraph(self.format_detection_result(dct_detection), self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # Extraction
        extraction = analysis.get('extraction', {})
        if extraction:
            story.append(Paragraph("Data Extraction", self.styles['Heading3']))
            for method, result in extraction.items():
                story.append(Paragraph(f"<b>{method.upper()} Extraction:</b>", self.styles.get('CustomBodyText', self.styles['BodyText'])))
                story.append(Paragraph(self.format_extraction_result(result), self.styles.get('CustomBodyText', self.styles['BodyText'])))
                story.append(Spacer(1, 0.1*inch))
    
    def generate_audio_report(self, analysis, story):
        """Generate report section for audio analysis"""
        story.append(Paragraph("Audio Analysis", self.styles['SectionHeader']))
        
        # File info
        info = analysis.get('audio_info', {})
        info_text = f"<b>File:</b> {os.path.basename(analysis['file_path'])}<br/>"
        info_text += f"<b>Sample Rate:</b> {info.get('sample_rate', 'N/A')} Hz<br/>"
        info_text += f"<b>Channels:</b> {info.get('channels', 'N/A')}<br/>"
        info_text += f"<b>Duration:</b> {info.get('duration', 'N/A'):.2f} seconds<br/>"
        info_text += f"<b>Format:</b> {info.get('format', 'N/A')}<br/>"
        story.append(Paragraph(info_text, self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # LSB Detection
        story.append(Paragraph("LSB Steganography Detection", self.styles['Heading3']))
        lsb_detection = analysis.get('lsb_detection', {})
        story.append(Paragraph(self.format_detection_result(lsb_detection), self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # Phase Detection
        story.append(Paragraph("Phase Steganography Detection", self.styles['Heading3']))
        phase_detection = analysis.get('phase_detection', {})
        story.append(Paragraph(self.format_detection_result(phase_detection), self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # Extraction
        extraction = analysis.get('extraction', {})
        if extraction:
            story.append(Paragraph("Data Extraction", self.styles['Heading3']))
            for method, result in extraction.items():
                story.append(Paragraph(f"<b>{method.upper()} Extraction:</b>", self.styles.get('CustomBodyText', self.styles['BodyText'])))
                story.append(Paragraph(self.format_extraction_result(result), self.styles.get('CustomBodyText', self.styles['BodyText'])))
                story.append(Spacer(1, 0.1*inch))
    
    def generate_video_report(self, analysis, story):
        """Generate report section for video analysis"""
        story.append(Paragraph("Video Analysis", self.styles['SectionHeader']))
        
        # File info
        info = analysis.get('video_info', {})
        info_text = f"<b>File:</b> {os.path.basename(analysis['file_path'])}<br/>"
        info_text += f"<b>Dimensions:</b> {info.get('width', 'N/A')} x {info.get('height', 'N/A')}<br/>"
        info_text += f"<b>FPS:</b> {info.get('fps', 'N/A')}<br/>"
        info_text += f"<b>Frame Count:</b> {info.get('frame_count', 'N/A')}<br/>"
        info_text += f"<b>Duration:</b> {info.get('duration', 'N/A'):.2f} seconds<br/>"
        story.append(Paragraph(info_text, self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.2*inch))
        
        # Frame Analysis
        frame_analysis = analysis.get('frame_analysis', {})
        if frame_analysis:
            story.append(Paragraph("Frame-based Steganography Detection", self.styles['Heading3']))
            story.append(Paragraph(self.format_detection_result(frame_analysis), self.styles.get('CustomBodyText', self.styles['BodyText'])))
            story.append(Spacer(1, 0.2*inch))
            
            # Frame results table
            if frame_analysis.get('frame_results'):
                story.append(Paragraph("Individual Frame Results", self.styles['Heading4']))
                table_data = [['Frame #', 'LSB Detected', 'Confidence']]
                for frame_result in frame_analysis['frame_results'][:20]:  # Limit to 20 frames
                    if 'error' not in frame_result:
                        table_data.append([
                            str(frame_result.get('frame_number', 'N/A')),
                            'Yes' if frame_result.get('lsb_detected', False) else 'No',
                            f"{frame_result.get('lsb_confidence', 0):.2f}%"
                        ])
                
                if len(table_data) > 1:
                    table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1.5*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
    
    def generate(self, analyses):
        """
        Generate PDF report from analysis results
        
        Args:
            analyses: List of analysis result dictionaries
        """
        doc = SimpleDocTemplate(self.output_path, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("Steganography Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        meta_text = f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        meta_text += f"<b>Files Analyzed:</b> {len(analyses)}<br/>"
        story.append(Paragraph(meta_text, self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        total_detections = sum(1 for a in analyses if self.has_detection(a))
        summary_text = f"This report analyzes {len(analyses)} file(s) for hidden steganographic data.<br/>"
        summary_text += f"<b>Files with detected steganography:</b> {total_detections}<br/>"
        summary_text += f"<b>Files without detected steganography:</b> {len(analyses) - total_detections}<br/>"
        story.append(Paragraph(summary_text, self.styles.get('CustomBodyText', self.styles['BodyText'])))
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed analysis for each file
        for idx, analysis in enumerate(analyses):
            if idx > 0:
                story.append(PageBreak())
            
            file_type = self.determine_file_type(analysis)
            
            if file_type == 'image':
                self.generate_image_report(analysis, story)
            elif file_type == 'audio':
                self.generate_audio_report(analysis, story)
            elif file_type == 'video':
                self.generate_video_report(analysis, story)
        
        # Build PDF
        doc.build(story)
    
    def has_detection(self, analysis):
        """Check if analysis has any detections"""
        if 'lsb_detection' in analysis and analysis['lsb_detection'].get('detected'):
            return True
        if 'dct_detection' in analysis and analysis['dct_detection'].get('detected'):
            return True
        if 'phase_detection' in analysis and analysis['phase_detection'].get('detected'):
            return True
        if 'frame_analysis' in analysis and analysis['frame_analysis'].get('detected'):
            return True
        return False
    
    def determine_file_type(self, analysis):
        """Determine file type from analysis"""
        if 'image_info' in analysis:
            return 'image'
        elif 'audio_info' in analysis:
            return 'audio'
        elif 'video_info' in analysis:
            return 'video'
        return 'unknown'

