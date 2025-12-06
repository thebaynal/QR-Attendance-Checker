# views/event_view.py
"""Modern view for displaying event details and attendance records with time slots."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR, WINDOW_WIDTH
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os


class EventView(BaseView):
    """Modern event detail with attendance log and time slots."""
    
    def build(self, event_id: str):
        """Build and return the event detail view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Get attendance records with time slot info
        attendance = self.db.get_attendance_by_event(event_id)
        
        # Get stats
        stats = self.db.get_attendance_summary(event_id)
        morning_count = stats.get('morning', 0)
        afternoon_count = stats.get('afternoon', 0)
        
        # Create table rows with premium styling
        table_rows = []
        if attendance:
            for user_key, record in attendance.items():
                time_slot = record.get('time_slot', 'morning')
                is_morning = time_slot == 'morning'
                
                table_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(record['name'], size=13, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(user_key.split('_')[0], size=12, color=ft.Colors.GREY_600)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.Icons.WB_SUNNY if is_morning else ft.Icons.NIGHTS_STAY,
                                                size=16,
                                                color=ft.Colors.ORANGE_600 if is_morning else ft.Colors.BLUE_600
                                            ),
                                            ft.Text(
                                                time_slot.title(),
                                                size=12,
                                                weight=ft.FontWeight.W_600,
                                            )
                                        ],
                                        spacing=6,
                                    ),
                                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                                    bgcolor=ft.Colors.ORANGE_50 if is_morning else ft.Colors.BLUE_50,
                                    border_radius=8,
                                )
                            ),
                            ft.DataCell(ft.Text(record['time'], size=12, color=ft.Colors.GREY_600)),
                        ]
                    )
                )
        else:
            table_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.INBOX_ROUNDED, size=48, color=ft.Colors.GREY_300),
                                    ft.Text(
                                        "No attendance records yet",
                                        size=14,
                                        color=ft.Colors.GREY_500,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            padding=30,
                            alignment=ft.alignment.center,
                        )
                    ),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        
        # Modern data table
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("Time Slot", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD, size=13, color=PRIMARY_COLOR)),
            ],
            rows=table_rows,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=12,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=52,
            data_row_min_height=56,
            column_spacing=20,
            horizontal_margin=20,
        )
        
        # Folder picker for PDF export
        folder_picker = ft.FilePicker()
        
        def generate_pdf_at_location(folder_path: str):
            """Generate PDF at the selected location with time slot information."""
            try:
                if not folder_path or not os.path.exists(folder_path):
                    self.show_snackbar("❌ Invalid folder path selected", ft.Colors.RED)
                    return
                
                if not os.access(folder_path, os.W_OK):
                    self.show_snackbar("❌ No write permission for selected folder", ft.Colors.RED)
                    return
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_event_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                                         for c in event['name'])
                filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                pdf_path = os.path.join(folder_path, filename)
                
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=22,
                    textColor=colors.HexColor('#2A73FF'),
                    spaceAfter=16,
                    alignment=1,
                    fontName='Helvetica-Bold'
                )
                story.append(Paragraph("MaScan Attendance Report", title_style))
                story.append(Spacer(1, 0.3*inch))
                
                details_style = ParagraphStyle('Details', parent=styles['Normal'], fontSize=11, spaceAfter=8)
                story.append(Paragraph(f"<b>Event:</b> {event['name']}", details_style))
                story.append(Paragraph(f"<b>Date:</b> {event['date']}", details_style))
                story.append(Paragraph(f"<b>Description:</b> {event.get('desc', 'No description')}", details_style))
                story.append(Paragraph(f"<b>Morning Attendees:</b> {morning_count}", details_style))
                story.append(Paragraph(f"<b>Afternoon Attendees:</b> {afternoon_count}", details_style))
                story.append(Paragraph(f"<b>Total Records:</b> {len(attendance)}", details_style))
                story.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}", details_style))
                story.append(Spacer(1, 0.4*inch))
                
                table_title_style = ParagraphStyle('TableTitle', parent=styles['Heading2'], 
                                                  fontSize=16, textColor=colors.HexColor('#2A73FF'), spaceAfter=12)
                story.append(Paragraph("Attendance Records", table_title_style))
                
                if attendance:
                    table_data = [["#", "Name", "ID", "Time Slot", "Time"]]
                    for idx, (user_key, record) in enumerate(attendance.items(), 1):
                        user_id = user_key.split('_')[0]
                        time_slot = record.get('time_slot', 'N/A').title()
                        table_data.append([
                            str(idx),
                            record['name'],
                            user_id,
                            time_slot,
                            record['time']
                        ])
                    
                    table = Table(table_data, colWidths=[0.4*inch, 2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2A73FF')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                        ('TOPPADDING', (0, 0), (-1, 0), 14),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 1), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ]))
                    story.append(table)
                else:
                    story.append(Paragraph("No attendance records found.", styles['Normal']))
                
                story.append(Spacer(1, 0.6*inch))
                footer_style = ParagraphStyle('Footer', parent=styles['Normal'], 
                                             fontSize=9, textColor=colors.grey, alignment=1)
                story.append(Paragraph(
                    f"Generated by MaScan Attendance System | {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}", 
                    footer_style
                ))
                
                doc.build(story)
                self.show_snackbar(f"✅ PDF saved: {filename}", ft.Colors.GREEN)
                
            except Exception as ex:
                print(f"ERROR generating PDF: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Export failed: {str(ex)}", ft.Colors.RED)
        
        def on_folder_selected(e: ft.FilePickerResultEvent):
            if e.path:
                self.show_snackbar("📄 Generating PDF...", ft.Colors.BLUE)
                generate_pdf_at_location(e.path)
            else:
                self.show_snackbar("⚠️ Export cancelled", ft.Colors.ORANGE)
        
        def export_data(e):
            if not attendance or len(attendance) == 0:
                self.show_snackbar("⚠️ No attendance records to export", ft.Colors.ORANGE)
                return
            
            try:
                folder_picker.on_result = on_folder_selected
                folder_picker.get_directory_path("Select folder to save attendance report")
            except Exception as ex:
                self.show_snackbar(f"❌ Failed to open folder picker: {str(ex)}", ft.Colors.RED)
        
        if folder_picker not in self.page.overlay:
            self.page.overlay.append(folder_picker)
        
        # Build premium content layout - FIXED WIDTH CONTAINER
        content = ft.Container(
            content=ft.Column(
                [
                    # Event header card
                    self.create_modern_card(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE, size=32),
                                            width=64,
                                            height=64,
                                            bgcolor=PRIMARY_COLOR,
                                            border_radius=16,
                                            alignment=ft.alignment.center,
                                        ),
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    event['name'],
                                                    size=22,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=PRIMARY_COLOR,
                                                ),
                                                ft.Row(
                                                    [
                                                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.GREY_600),
                                                        ft.Text(event['date'], size=14, color=ft.Colors.GREY_700),
                                                    ],
                                                    spacing=8,
                                                ),
                                            ],
                                            spacing=6,
                                            expand=True,
                                        ),
                                    ],
                                    spacing=16,
                                ),
                                ft.Container(height=16),
                                ft.Text(
                                    event.get('desc', 'No description'),
                                    size=14,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=0,
                        ),
                        padding=24,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Stats cards row
                    ft.Row(
                        [
                            self.create_modern_card(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.WB_SUNNY, color=ft.Colors.ORANGE_400, size=40),
                                        ft.Text(
                                            str(morning_count),
                                            size=36,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.ORANGE_700,
                                        ),
                                        ft.Text("Morning", size=13, color=ft.Colors.GREY_600),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                padding=24,
                            ),
                            self.create_modern_card(
                                content=ft.Column(
                                    [
                                        ft.Icon(ft.Icons.NIGHTS_STAY, color=ft.Colors.BLUE_400, size=40),
                                        ft.Text(
                                            str(afternoon_count),
                                            size=36,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_700,
                                        ),
                                        ft.Text("Afternoon", size=13, color=ft.Colors.GREY_600),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                padding=24,
                            ),
                        ],
                        spacing=16,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    
                    ft.Container(height=24),
                    
                    # Attendance records section
                    self.create_section_title("📋 Attendance Records", size=18),
                    ft.Container(height=12),
                    
                    self.create_modern_card(
                        content=ft.Column(
                            [attendance_table],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        padding=0,
                    ),
                    
                    ft.Container(height=24),
                    
                    # Export button
                    self.create_modern_button(
                        text="Export to PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=export_data,
                        width=360,
                    ),
                    
                    ft.Container(height=12),
                    
                    # Info card
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.INFO_OUTLINE,
                                    size=18,
                                    color=ft.Colors.BLUE_600 if attendance else ft.Colors.GREY_500,
                                ),
                                ft.Text(
                                    f"{len(attendance)} records ready" if attendance else "No records available",
                                    size=13,
                                    color=ft.Colors.GREY_700,
                                    weight=ft.FontWeight.W_500,
                                ),
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        padding=14,
                        bgcolor=ft.Colors.BLUE_50 if attendance else ft.Colors.GREY_100,
                        border_radius=12,
                        border=ft.border.all(1, ft.Colors.BLUE_200 if attendance else ft.Colors.GREY_300),
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=480,
            alignment=ft.alignment.center,
        )
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                self.create_gradient_container(
                    content=ft.Column(
                        [content],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            ],
            bgcolor=ft.Colors.TRANSPARENT,
        )