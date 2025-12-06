# views/enhanced_event_view.py
"""Event view with enhanced PDF export."""

import flet as ft
from views.base_view import BaseView
from utils.pdf_export import AttendancePDFExporter
from datetime import datetime
import os


class EventView(BaseView):
    """Event detail with grouped attendance export."""
    
    def build(self, event_id: str):
        """Build event detail view."""
        event = self.db.get_event_by_id(event_id)
        if not event:
            self.page.go("/home")
            return ft.View("/", [ft.Container()])
        
        # Get attendance by section
        attendance_by_section = self.db.get_attendance_by_section(event_id)
        
        # Create section tabs
        section_tabs = []
        for section_name, students in sorted(attendance_by_section.items()):
            # Calculate stats
            total = len(students)
            morning_present = sum(1 for s in students if s['morning_status'] == 'Present')
            afternoon_present = sum(1 for s in students if s['afternoon_status'] == 'Present')
            
            # Create table for this section
            table_data = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("#", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Student ID", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Morning Time", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Morning Status", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Afternoon Time", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Afternoon Status", weight=ft.FontWeight.BOLD)),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(idx))),
                            ft.DataCell(ft.Text(s['school_id'])),
                            ft.DataCell(ft.Text(s['name'])),
                            ft.DataCell(ft.Text(s['morning_time'] or '-')),
                            ft.DataCell(ft.Text(
                                s['morning_status'],
                                color=ft.Colors.GREEN if s['morning_status'] == 'Present' else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD
                            )),
                            ft.DataCell(ft.Text(s['afternoon_time'] or '-')),
                            ft.DataCell(ft.Text(
                                s['afternoon_status'],
                                color=ft.Colors.GREEN if s['afternoon_status'] == 'Present' else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD
                            )),
                        ]
                    ) for idx, s in enumerate(students, 1)
                ]
            )
            
            # Section content
            section_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text(f"Total: {total}", size=14),
                                ft.VerticalDivider(),
                                ft.Text(f"Morning: {morning_present}/{total}", 
                                       size=14, color=ft.Colors.GREEN_700),
                                ft.VerticalDivider(),
                                ft.Text(f"Afternoon: {afternoon_present}/{total}", 
                                       size=14, color=ft.Colors.BLUE_700),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        bgcolor=ft.Colors.GREY_100,
                        padding=10,
                        border_radius=5,
                        margin=ft.margin.only(bottom=10)
                    ),
                    ft.Container(
                        content=table_data,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10
                    )
                ],
                scroll=ft.ScrollMode.AUTO
            )
            
            section_tabs.append(
                ft.Tab(
                    text=section_name,
                    content=section_content
                )
            )
        
        # Create tabs view
        tabs = ft.Tabs(
            tabs=section_tabs if section_tabs else [
                ft.Tab(
                    text="No Data",
                    content=ft.Container(
                        content=ft.Text("No attendance records yet"),
                        alignment=ft.alignment.center,
                        padding=50
                    )
                )
            ],
            expand=True
        )
        
        def export_to_pdf(e):
            """Export attendance to PDF."""
            try:
                # Create exports folder
                export_dir = "exports"
                os.makedirs(export_dir, exist_ok=True)
                
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(export_dir, f"Attendance_{event['name']}_{timestamp}.pdf")
                
                # Export
                exporter = AttendancePDFExporter(self.db)
                exporter.export_attendance(event_id, filename)
                
                self.show_snackbar(f"✅ PDF exported: {filename}", ft.Colors.GREEN)
                
            except Exception as ex:
                print(f"Export error: {ex}")
                import traceback
                traceback.print_exc()
                self.show_snackbar(f"❌ Export failed: {str(ex)}", ft.Colors.RED)
        
        return ft.View(
            f"/event/{event_id}",
            [
                self.create_app_bar(event['name'], show_back=True),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                event['name'],
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700
                            ),
                            ft.Text(event['date'], size=16, color=ft.Colors.GREY_700),
                            ft.ElevatedButton(
                                "Export to PDF",
                                icon=ft.Icons.PICTURE_AS_PDF,
                                on_click=export_to_pdf,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_700,
                                    color=ft.Colors.WHITE
                                )
                            ),
                            ft.Divider(),
                            tabs
                        ],
                        spacing=15,
                        expand=True
                    ),
                    padding=20,
                    expand=True
                )
            ]
        )