# utils/pdf_export.py
"""Enhanced PDF export with section grouping."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


class AttendancePDFExporter:
    """Export attendance data to formatted PDF with section grouping."""
    
    def __init__(self, db):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='EventTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1976D2'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='Stats',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            spaceAfter=10,
            alignment=TA_CENTER
        ))
    
    def export_attendance(self, event_id: str, filename: str):
        """Export attendance grouped by section."""
        # Get event info
        event = self.db.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        
        # Get attendance data grouped by section
        attendance_by_section = self.db.get_attendance_by_section(event_id)
        
        # Create PDF
        doc = SimpleDocTemplate(
            filename,
            pagesize=landscape(letter),
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        
        # Title
        title = Paragraph(f"Attendance Report: {event['name']}", self.styles['EventTitle'])
        story.append(title)
        
        # Event details
        date_info = Paragraph(
            f"Date: {event['date']} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Stats']
        )
        story.append(date_info)
        story.append(Spacer(1, 0.3*inch))
        
        # Process each section
        for section_name, students in sorted(attendance_by_section.items()):
            # Section header
            section_header = Paragraph(f"Section: {section_name}", self.styles['SectionHeader'])
            story.append(section_header)
            
            # Calculate statistics
            total_students = len(students)
            morning_present = sum(1 for s in students if s['morning_status'] == 'Present')
            afternoon_present = sum(1 for s in students if s['afternoon_status'] == 'Present')
            
            stats_text = f"Total Students: {total_students} | Morning: {morning_present}/{total_students} | Afternoon: {afternoon_present}/{total_students}"
            stats = Paragraph(stats_text, self.styles['Normal'])
            story.append(stats)
            story.append(Spacer(1, 0.15*inch))
            
            # Create table data
            table_data = [
                ['#', 'Student ID', 'Name', 'Morning Time', 'Morning Status', 'Afternoon Time', 'Afternoon Status']
            ]
            
            for idx, student in enumerate(students, 1):
                table_data.append([
                    str(idx),
                    student['school_id'],
                    student['name'],
                    student['morning_time'] or '-',
                    student['morning_status'],
                    student['afternoon_time'] or '-',
                    student['afternoon_status']
                ])
            
            # Create table
            col_widths = [0.4*inch, 1.2*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch]
            table = Table(table_data, colWidths=col_widths, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Body styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # ID column
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Name column
                ('ALIGN', (3, 1), (-1, -1), 'CENTER'), # Time/Status columns
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1976D2')),
                
                # Padding
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            # Color code statuses
            for row_idx, student in enumerate(students, 1):
                # Morning status
                if student['morning_status'] == 'Present':
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor('#C8E6C9')),
                        ('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.HexColor('#2E7D32')),
                        ('FONTNAME', (4, row_idx), (4, row_idx), 'Helvetica-Bold'),
                    ]))
                else:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (4, row_idx), (4, row_idx), colors.HexColor('#FFCDD2')),
                        ('TEXTCOLOR', (4, row_idx), (4, row_idx), colors.HexColor('#C62828')),
                        ('FONTNAME', (4, row_idx), (4, row_idx), 'Helvetica-Bold'),
                    ]))
                
                # Afternoon status
                if student['afternoon_status'] == 'Present':
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (6, row_idx), (6, row_idx), colors.HexColor('#C8E6C9')),
                        ('TEXTCOLOR', (6, row_idx), (6, row_idx), colors.HexColor('#2E7D32')),
                        ('FONTNAME', (6, row_idx), (6, row_idx), 'Helvetica-Bold'),
                    ]))
                else:
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (6, row_idx), (6, row_idx), colors.HexColor('#FFCDD2')),
                        ('TEXTCOLOR', (6, row_idx), (6, row_idx), colors.HexColor('#C62828')),
                        ('FONTNAME', (6, row_idx), (6, row_idx), 'Helvetica-Bold'),
                    ]))
            
            story.append(table)
            story.append(PageBreak())  # New page for each section
        
        # Build PDF
        doc.build(story)
        return filename