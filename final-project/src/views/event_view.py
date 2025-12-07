# views/event_view.py
"""Modern view for displaying event details and attendance records."""

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
    """Modern event detail with attendance log."""
    
    def build(self, event_id: str):
        """Build and return the event detail view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        attendance = self.db.get_attendance_by_event(event_id)
        
        # Modern data table with enhanced styling
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.W_700, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.W_700, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.W_700, size=13, color=PRIMARY_COLOR)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.W_700, size=13, color=PRIMARY_COLOR)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'], size=12, weight=ft.FontWeight.W_500)),
                        ft.DataCell(ft.Text(user_id, size=12, color=ft.Colors.GREY_700)),
                        ft.DataCell(ft.Text(record['time'], size=12, color=ft.Colors.GREY_700)),
                        ft.DataCell(
                            ft.Text(
                                record['status'],
                                color=ft.Colors.WHITE,
                                size=9,
                                weight=ft.FontWeight.W_600,
                                bgcolor=ft.Colors.GREEN_600,
                            )
                        ),
                    ]
                ) for user_id, record in attendance.items()
            ] if attendance else [
                ft.DataRow(cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.INBOX, size=40, color=ft.Colors.GREY_300),
                                    ft.Text(
                                        "No attendance records yet",
                                        size=13,
                                        color=ft.Colors.GREY_500,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            padding=15,
                        )
                    ),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ],
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=12,
            heading_row_color=ft.Colors.BLUE_50,
            heading_row_height=48,
            data_row_min_height=44,
            column_spacing=12,
        )
        
        # Folder picker for PDF export
        folder_picker = ft.FilePicker()
        
        def generate_pdf_at_location(folder_path: str):
            """Generate PDF at the selected location with comprehensive error handling."""
            try:
                # Validate folder path
                if not folder_path or not os.path.exists(folder_path):
                    self.show_snackbar("❌ Invalid folder path selected", ft.Colors.RED)
                    return
                
                # Check write permissions
                if not os.access(folder_path, os.W_OK):
                    self.show_snackbar("❌ No write permission for selected folder", ft.Colors.RED)
                    return
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_event_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                                         for c in event['name'])
                filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                pdf_path = os.path.join(folder_path, filename)
                
                # Create PDF document
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Add title with enhanced styling
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
                
                # Add event details with better formatting
                details_style = ParagraphStyle('Details', parent=styles['Normal'], fontSize=11, spaceAfter=8)
                story.append(Paragraph(f"<b>Event:</b> {event['name']}", details_style))
                story.append(Paragraph(f"<b>Date:</b> {event['date']}", details_style))
                story.append(Paragraph(f"<b>Description:</b> {event.get('desc', 'No description')}", details_style))
                story.append(Paragraph(f"<b>Total Attendees:</b> {len(attendance)}", details_style))
                story.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}", details_style))
                story.append(Spacer(1, 0.4*inch))
                
                # Add table title
                table_title_style = ParagraphStyle('TableTitle', parent=styles['Heading2'], 
                                                  fontSize=16, textColor=colors.HexColor('#2A73FF'), spaceAfter=12)
                story.append(Paragraph("Attendance Records", table_title_style))
                
                if attendance:
                    table_data = [["#", "Name", "ID", "Time", "Status"]]
                    for idx, (user_id, record) in enumerate(attendance.items(), 1):
                        table_data.append([str(idx), record['name'], user_id, record['time'], record['status']])
                    
                    table = Table(table_data, colWidths=[0.5*inch, 2.2*inch, 1.3*inch, 1.2*inch, 1*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2A73FF')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                        ('TOPPADDING', (0, 0), (-1, 0), 14),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 1), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                    ]))
                    story.append(table)
                else:
                    story.append(Paragraph("No attendance records found.", styles['Normal']))
                
                # Footer
                story.append(Paragraph(
                    f"Generated by MaScan Attendance System | {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}", 
                    footer_style
                ))
                
                doc.build(story)
                self.show_snackbar(f"✅ PDF saved successfully: {filename}", ft.Colors.GREEN)
                
            except PermissionError:
                self.show_snackbar("❌ Permission denied: Cannot write to selected folder", ft.Colors.RED)
            except OSError as os_err:
                self.show_snackbar(f"❌ File system error: {str(os_err)}", ft.Colors.RED)
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
            # Comprehensive validation
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
        
        # Build content with mobile-optimized layout
        content = ft.Column(
            [
                # Header section
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.EVENT, color=ft.Colors.WHITE, size=28),
                                        width=56,
                                        height=56,
                                        bgcolor=PRIMARY_COLOR,
                                        border_radius=16,
                                        alignment=ft.alignment.center,
                                        shadow=ft.BoxShadow(
                                            spread_radius=1,
                                            blur_radius=8,
                                            color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                                            offset=ft.Offset(0, 3),
                                        ),
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                event['name'],
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                color=PRIMARY_COLOR,
                                                max_lines=2,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=ft.Colors.GREY_600),
                                                    ft.Text(event['date'], size=13, color=ft.Colors.GREY_700),
                                                ],
                                                spacing=6,
                                            ),
                                        ],
                                        spacing=4,
                                        expand=True,
                                    ),
                                ],
                                spacing=12,
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Container(
                                height=1,
                                bgcolor=ft.Colors.GREY_200,
                                margin=ft.margin.symmetric(vertical=12),
                            ),
                            ft.Text(
                                event.get('desc', 'No description'),
                                size=13,
                                color=ft.Colors.GREY_600,
                                italic=event.get('desc', 'No description') == 'No description',
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=16,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.GREY_200),
                ),
                
                # Stats section
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.PEOPLE, color=PRIMARY_COLOR, size=36),
                            ft.Text(
                                str(len(attendance)),
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR,
                            ),
                            ft.Text("Total Attendees", size=13, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=24,
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=12,
                    border=ft.border.all(1, ft.Colors.BLUE_100),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=6,
                        color=ft.Colors.with_opacity(0.08, ft.Colors.BLUE_900),
                        offset=ft.Offset(0, 2),
                    ),
                    alignment=ft.alignment.center,
                ),
                
                # Attendance table section
                ft.Column(
                    [
                        ft.Text(
                            "📋 Attendance Records",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_800,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [attendance_table],
                                scroll=ft.ScrollMode.AUTO,
                            ),
                            border=ft.border.all(1, ft.Colors.GREY_200),
                            border_radius=12,
                            padding=12,
                            bgcolor=ft.Colors.WHITE,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                blur_radius=6,
                                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                                offset=ft.Offset(0, 2),
                            ),
                        ),
                    ],
                    spacing=12,
                ),
                
                # Export section
                ft.Column(
                    [
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.WHITE, size=18),
                                    ft.Text(
                                        "Export to PDF",
                                        color=ft.Colors.WHITE,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ],
                                spacing=8,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            on_click=export_data,
                            bgcolor=PRIMARY_COLOR,
                            color=ft.Colors.WHITE,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                padding=14,
                                elevation=3,
                            ),
                            width=WINDOW_WIDTH - 64,
                            height=48,
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.INFO_OUTLINE,
                                        size=16,
                                        color=ft.Colors.BLUE_600 if attendance else ft.Colors.GREY_500,
                                    ),
                                    ft.Text(
                                        f"{len(attendance)} records ready" if attendance else "No records available",
                                        size=12,
                                        color=ft.Colors.GREY_700,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=6,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.BLUE_50 if attendance else ft.Colors.GREY_100,
                            border_radius=10,
                            border=ft.border.all(1, ft.Colors.BLUE_200 if attendance else ft.Colors.GREY_300),
                        ),
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=content,
                    padding=16,
                    expand=True,
                    bgcolor=ft.Colors.GREY_50,
                )
            ],
            bgcolor=ft.Colors.GREY_50,
        )