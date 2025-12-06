# views/event_view.py
"""View for displaying event details and attendance records."""

import flet as ft
from views.base_view import BaseView
from config.constants import PRIMARY_COLOR
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os


class EventView(BaseView):
    """Event detail with attendance log."""
    
    def build(self, event_id: str):
        """Build and return the event detail view.
        
        Args:
            event_id: ID of the event to display
        """
        event = self.db.get_event_by_id(event_id)
        if not event:
            # FIX: Must return a valid view, not None
            self.page.go("/home")
            # Return a dummy view while redirecting
            return ft.View(
                "/",
                [ft.Container()]
            )
        
        attendance = self.db.get_attendance_by_event(event_id)
        
        attendance_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record['name'])),
                        ft.DataCell(ft.Text(user_id)),
                        ft.DataCell(ft.Text(record['time'])),
                        ft.DataCell(ft.Text(record['status'], color=ft.Colors.GREEN)),
                    ]
                ) for user_id, record in attendance.items()
            ] if attendance else [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("No attendance records yet", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            ]
        )
        
        # Create folder picker for PDF export
        folder_picker = ft.FilePicker()
        
        def generate_pdf_at_location(folder_path: str):
            """Generate PDF at the selected location."""
            try:
                # Generate filename with event name and timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_event_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                                         for c in event['name'])
                filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                pdf_path = os.path.join(folder_path, filename)
                
                # Create PDF document
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Add title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#1976D2'),
                    spaceAfter=12,
                    alignment=1
                )
                story.append(Paragraph(f"MoScan Attendance Report", title_style))
                story.append(Spacer(1, 0.2*inch))
                
                # Add event details
                details_style = ParagraphStyle(
                    'Details',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=6
                )
                story.append(Paragraph(f"<b>Event:</b> {event['name']}", details_style))
                story.append(Paragraph(f"<b>Date:</b> {event['date']}", details_style))
                story.append(Paragraph(f"<b>Description:</b> {event.get('desc', 'N/A')}", details_style))
                story.append(Paragraph(f"<b>Total Attendees:</b> {len(attendance)}", details_style))
                story.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", details_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Add attendance table title
                table_title_style = ParagraphStyle(
                    'TableTitle',
                    parent=styles['Heading2'],
                    fontSize=14,
                    textColor=colors.HexColor('#1976D2'),
                    spaceAfter=10
                )
                story.append(Paragraph("Attendance Records", table_title_style))
                
                # Create attendance table data
                if attendance:
                    table_data = [["#", "Name", "ID", "Time", "Status"]]
                    for idx, (user_id, record) in enumerate(attendance.items(), 1):
                        table_data.append([
                            str(idx),
                            record['name'],
                            user_id,
                            record['time'],
                            record['status']
                        ])
                    
                    # Create and style table
                    table = Table(table_data, colWidths=[0.4*inch, 2*inch, 1.2*inch, 1*inch, 1*inch])
                    table.setStyle(TableStyle([
                        # Header styling
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('TOPPADDING', (0, 0), (-1, 0), 12),
                        
                        # Body styling
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    story.append(table)
                else:
                    story.append(Paragraph("No attendance records found.", styles['Normal']))
                
                # Add footer
                story.append(Spacer(1, 0.5*inch))
                footer_style = ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=1
                )
                story.append(Paragraph(
                    f"Generated by MoScan Attendance System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                    footer_style
                ))
                
                # Build PDF
                doc.build(story)
                
                self.show_snackbar(f"✅ PDF saved successfully: {filename}", ft.Colors.GREEN)
                print(f"PDF saved to: {pdf_path}")
                
            except Exception as ex:
                print(f"ERROR generating PDF: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Export error: {str(ex)}", ft.Colors.RED)
        
        def on_folder_selected(e: ft.FilePickerResultEvent):
            """Handle folder selection result."""
            if e.path:
                print(f"Selected folder: {e.path}")
                self.show_snackbar("Generating PDF...", ft.Colors.BLUE)
                generate_pdf_at_location(e.path)
            else:
                print("Folder selection cancelled")
                self.show_snackbar("Export cancelled", ft.Colors.ORANGE)
        
        def export_data(e):
            """Open folder picker to choose save location."""
            if not attendance:
                self.show_snackbar("⚠️ No attendance records to export", ft.Colors.ORANGE)
                return
            
            try:
                # Set the callback for folder selection
                folder_picker.on_result = on_folder_selected
                # Open folder picker dialog
                folder_picker.get_directory_path(
                    dialog_title=f"Select folder to save attendance report"
                )
                print("Folder picker opened")
            except Exception as ex:
                print(f"ERROR opening folder picker: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Error: {str(ex)}", ft.Colors.RED)
        
        # Add folder picker to page overlay
        if folder_picker not in self.page.overlay:
            self.page.overlay.append(folder_picker)
        
        # Check if current user is admin to show export button
        user_role = None
        try:
            user_role = self.db.get_user_role(self.app.current_user) if self.app.current_user else None
        except AttributeError:
            # If get_user_role doesn't exist, show export button for all users
            user_role = 'admin'
        
        # Build column content with optional export button
        column_content = [
            ft.Text(
                event['name'],
                size=24,
                weight=ft.FontWeight.BOLD,
                color=PRIMARY_COLOR
            ),
            ft.Text(event['date'], size=16, color=ft.Colors.GREY_700),
            ft.Divider(),
            ft.Row(
                [
                    ft.Icon(ft.Icons.PEOPLE, color=PRIMARY_COLOR, size=30),
                    ft.Text(
                        f"Total Attendees: {len(attendance)}",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),
                ],
                spacing=10
            ),
            ft.Container(
                content=ft.Column(
                    [attendance_table],
                    scroll=ft.ScrollMode.AUTO
                ),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=10,
                padding=10,
                expand=True
            ),
        ]
        
        # Add export button (show for all users or just admins based on your needs)
        # For now, showing for all users - remove the if condition if you want all users to export
        column_content.append(
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Export to PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        on_click=export_data,
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY_COLOR,
                            color=ft.Colors.WHITE
                        ),
                        height=50
                    ),
                    ft.Text(
                        f"📄 {len(attendance)} records ready to export",
                        size=12,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ) if attendance else ft.Text(
                        "No records to export",
                        size=12,
                        color=ft.Colors.GREY_400,
                        italic=True
                    )
                ],
                spacing=15,
                alignment=ft.MainAxisAlignment.START
            )
        )
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=ft.Column(
                        column_content,
                        spacing=15
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )