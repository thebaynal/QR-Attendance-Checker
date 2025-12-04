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
        
        def export_data(e):
            """Export attendance data to PDF."""
            try:
                self.show_snackbar(f"Exporting {len(attendance)} records to PDF...", ft.Colors.BLUE)
                
                # Create Downloads folder path
                downloads_path = os.path.expanduser("~/Downloads/Attendance_Reports")
                os.makedirs(downloads_path, exist_ok=True)
                
                # Generate filename with event name and timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{event['name'].replace(' ', '_')}_{timestamp}.pdf"
                pdf_path = os.path.join(downloads_path, filename)
                
                # Create PDF document
                doc = SimpleDocTemplate(pdf_path, pagesize=letter)
                story = []
                styles = getSampleStyleSheet()
                
                # Add title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#F9A825'),
                    spaceAfter=12,
                    alignment=1
                )
                story.append(Paragraph(f"MaScan Attendance Report", title_style))
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
                story.append(Paragraph(f"<b>Total Attendees:</b> {len(attendance)}", details_style))
                story.append(Paragraph(f"<b>Export Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", details_style))
                story.append(Spacer(1, 0.3*inch))
                
                # Create attendance table data
                table_data = [["Name", "ID", "Time", "Status"]]
                for user_id, record in attendance.items():
                    table_data.append([
                        record['name'],
                        user_id,
                        record['time'],
                        record['status']
                    ])
                
                # Create and style table
                table = Table(table_data, colWidths=[2.2*inch, 1.2*inch, 1.2*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F9A825')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
                ]))
                story.append(table)
                
                # Build PDF
                doc.build(story)
                
                self.show_snackbar(f"PDF exported to Downloads/Attendance_Reports/{filename}", ft.Colors.GREEN)
                print(f"PDF saved to: {pdf_path}")
            except Exception as ex:
                print(f"ERROR exporting PDF: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"Export error: {str(ex)}", ft.Colors.RED)
        
        # Check if current user is admin to show export button
        user_role = self.db.get_user_role(self.app.current_user) if self.app.current_user else None
        
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
            ft.Text(
                f"Total Attendees: {len(attendance)}",
                size=18,
                weight=ft.FontWeight.BOLD
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
        
        # Only add export button if user is admin
        if user_role == 'admin':
            column_content.append(
                ft.ElevatedButton(
                    "Export to PDF",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=export_data,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE
                    )
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