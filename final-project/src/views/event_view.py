# views/enhanced_event_view.py
"""Event view with enhanced PDF export."""

import flet as ft
from views.base_view import BaseView
from utils.pdf_export import AttendancePDFExporter
from datetime import datetime
import os
import threading
from tkinter import filedialog
import tkinter as tk


class EventView(BaseView):
    """Event detail with grouped attendance export."""
    
    def build(self, event_id: str):
        """Build event detail view."""
        try:
            print(f"DEBUG: Building event view for event_id: {event_id}")
            
            event = self.db.get_event_by_id(event_id)
            if not event:
                print(f"DEBUG: Event not found: {event_id}")
                self.page.go("/home")
                return ft.View("/", [ft.Container()])
            
            print(f"DEBUG: Event found: {event}")
            
            # Get current user role
            current_username = self.app.current_user
            current_user_role = self.db.get_user_role(current_username) if current_username else 'scanner'
            is_admin = current_user_role and current_user_role.lower() == 'admin'
            
            # Get attendance by section
            attendance_by_section = self.db.get_attendance_by_section(event_id)
            print(f"DEBUG: attendance_by_section: {attendance_by_section}")
            
            if not attendance_by_section:
                print("DEBUG: No attendance data found")
                attendance_by_section = {}
            
            # Create section tabs
            section_tabs = []
            for section_name, students in sorted(attendance_by_section.items()):
                # Calculate stats
                total = len(students)
                morning_present = sum(1 for s in students if s.get('morning_status') == 'Present')
                afternoon_present = sum(1 for s in students if s.get('afternoon_status') == 'Present')
                
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
                                ft.DataCell(ft.Text(s.get('school_id', ''))),
                                ft.DataCell(ft.Text(s.get('name', ''))),
                                ft.DataCell(ft.Text(s.get('morning_time') or '-')),
                                ft.DataCell(ft.Text(
                                    s.get('morning_status', 'Absent'),
                                    color=ft.Colors.GREEN if s.get('morning_status') == 'Present' else ft.Colors.RED,
                                    weight=ft.FontWeight.BOLD
                                )),
                                ft.DataCell(ft.Text(s.get('afternoon_time') or '-')),
                                ft.DataCell(ft.Text(
                                    s.get('afternoon_status', 'Absent'),
                                    color=ft.Colors.GREEN if s.get('afternoon_status') == 'Present' else ft.Colors.RED,
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
                """Export attendance to PDF with file picker."""
                # Check if user is admin
                if not is_admin:
                    self.show_snackbar("Only admins can export attendance reports", ft.Colors.RED)
                    return
                
                try:
                    print("DEBUG: Export to PDF button clicked")
                    
                    # Sanitize event name for filename
                    safe_event_name = "".join(c for c in event['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    # Generate default filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_filename = f"Attendance_{safe_event_name}_{timestamp}.pdf"
                    
                    # Show file picker dialog in a separate thread to avoid blocking UI
                    def pick_save_location():
                        try:
                            # Create hidden root window for tkinter
                            root = tk.Tk()
                            root.withdraw()
                            root.attributes('-topmost', True)
                            
                            # Show file save dialog
                            filepath = filedialog.asksaveasfilename(
                                defaultextension=".pdf",
                                initialfile=default_filename,
                                initialdir=os.path.expanduser("~/Documents"),
                                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                                title="Save Attendance Report"
                            )
                            
                            root.destroy()
                            
                            # If user cancelled, return None
                            if not filepath:
                                print("DEBUG: File picker cancelled by user")
                                return None
                            
                            print(f"DEBUG: User selected location: {filepath}")
                            return filepath
                        
                        except Exception as picker_error:
                            print(f"Error in file picker: {picker_error}")
                            return None
                    
                    # Run file picker in background thread
                    filepath = pick_save_location()
                    
                    if not filepath:
                        print("DEBUG: No file location selected")
                        return
                    
                    print(f"DEBUG: Exporting to {filepath}")
                    
                    # Create parent directory if it doesn't exist
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    
                    # Export
                    exporter = AttendancePDFExporter(self.db)
                    result = exporter.export_attendance(event_id, filepath)
                    
                    # Verify file was created
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        print(f"DEBUG: PDF created successfully, size: {file_size} bytes")
                        print(f"DEBUG: Export result: {result}")
                        
                        # Show success message with file location
                        filename_only = os.path.basename(filepath)
                        self.show_snackbar(f"✅ PDF saved: {filename_only}", ft.Colors.GREEN)
                    else:
                        print(f"DEBUG: PDF file was not created at {filepath}")
                        raise FileNotFoundError(f"PDF file was not created: {filepath}")
                    
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
                            ] + (
                                [
                                    ft.ElevatedButton(
                                        "Export to PDF",
                                        icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=export_to_pdf,
                                        width=200,
                                        height=50,
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.Colors.RED_700,
                                            color=ft.Colors.WHITE,
                                            padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                            shape=ft.RoundedRectangleBorder(radius=5)
                                        )
                                    ),
                                    ft.Divider(),
                                ] if is_admin else [ft.Divider()]
                            ) + [
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
        
        except Exception as e:
            print(f"ERROR building event view: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error view
            return ft.View(
                f"/event/{event_id}",
                [
                    self.create_app_bar("Event Error", show_back=True),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR, size=80, color=ft.Colors.RED),
                                ft.Text("Error loading event", size=20, color=ft.Colors.RED),
                                ft.Text(str(e), size=14, color=ft.Colors.GREY_600),
                                ft.TextButton(
                                    "Go Back",
                                    on_click=lambda e: self.page.go("/home")
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20
                        ),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ]
            )
    
    def load_events(self):
        """Reload events (called by sync service when data changes)."""
        try:
            # Refresh the current view by rebuilding it
            pass
        except Exception as e:
            print(f"Error loading events: {e}")