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
        
        # Get attendance data - handle both old and new database structures
        try:
            attendance_by_section = self.db.get_attendance_by_section(event_id)
        except Exception as e:
            print(f"Error getting attendance by section: {e}")
            # Fallback: try to get attendance from old table structure
            attendance_by_section = self._get_attendance_fallback(event_id)
            if not attendance_by_section:
                raise ValueError("Could not retrieve attendance data")
        
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
        
        # Handle empty attendance
        if not attendance_by_section:
            empty_text = Paragraph(
                "No attendance records found for this event.",
                self.styles['Normal']
            )
            story.append(empty_text)
        else:
            # Process each section
            for section_name, students in sorted(attendance_by_section.items()):
                # Section header
                section_header = Paragraph(f"Section: {section_name}", self.styles['SectionHeader'])
                story.append(section_header)
                
                # Calculate statistics
                total_students = len(students)
                morning_present = sum(1 for s in students if s.get('morning_status') == 'Present')
                afternoon_present = sum(1 for s in students if s.get('afternoon_status') == 'Present')
                
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
                        student.get('school_id', ''),
                        student.get('name', ''),
                        student.get('morning_time') or '-',
                        student.get('morning_status', 'Absent'),
                        student.get('afternoon_time') or '-',
                        student.get('afternoon_status', 'Absent')
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
                    if student.get('morning_status') == 'Present':
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
                    if student.get('afternoon_status') == 'Present':
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
    
    def _get_attendance_fallback(self, event_id: str) -> dict:
        """Fallback method to get attendance from old table structure."""
        try:
            # Try to get from old attendance table
            query = """
            SELECT user_id, user_name, timestamp 
            FROM attendance 
            WHERE event_id = ?
            ORDER BY timestamp DESC
            """
            results = self.db._execute(query, (event_id,), fetch_all=True)
            
            if not results:
                return {}
            
            # Group by a generic section
            grouped_data = {"General": []}
            for row in results:
                user_id, user_name, timestamp = row
                grouped_data["General"].append({
                    'school_id': user_id,
                    'name': user_name,
                    'morning_time': timestamp,
                    'morning_status': 'Present',
                    'afternoon_time': '',
                    'afternoon_status': 'Absent'
                })
            
            return grouped_data
        except Exception as e:
            print(f"Fallback method failed: {e}")
            return {}